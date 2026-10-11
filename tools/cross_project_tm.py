#!/usr/bin/env python3
"""Offline cross-project translation memory for RetroThai Framework V3.1.

Read-only source project scanning; approved/reviewed text only. Generates
suggestions, never changes project masters, ROMs, patches, or gate statuses.
Works without external Python dependencies.
"""
from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from collections import Counter

REVIEWED_STATES = {"REVIEWED", "APPROVED", "VERIFIED"}
APPROVED_FLAGS = {"1", "YES", "TRUE", "APPROVED", "REVIEWED"}
TOKEN_RE = re.compile(r"\{(?:[A-Za-z_][A-Za-z_0-9]*|\d+)(?::[^{}]+)?\}|%(?:(?:\d+)\$)?[-+# 0]*\d*(?:\.\d+)?[sdifuxX]|\\[nrt]|<[/A-Za-z_][^<>]{0,80}>")
SOURCE_KEYS = ("Source_Text", "English", "Original", "Source")
THAI_KEYS = ("Thai", "Thai_Text", "Translation")
SUGGEST_FIELDS = ["ID", "Bank", "Source_Text", "Context_Key", "Suggested_Thai", "Source_Game", "Source_Platform", "Source_Project", "Source_Status", "Source_Series", "Similarity", "Match_Type", "Context_Match", "Review_Status", "Conflict", "Reason"]
TERM_FIELDS = ["ID", "Bank", "Source_Text", "Term", "Thai_Term", "Source_Game", "Source_Platform", "Source_Project", "Series_Match", "Review_Status"]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def pick(row: dict, *keys: str) -> str:
    for k in keys:
        if row.get(k):
            return str(row[k])
    return ""


def norm(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip()


def tokens(text: str) -> Counter:
    return Counter(TOKEN_RE.findall(text))


def token_safe(src: str, thai: str) -> bool:
    return tokens(src) == tokens(thai)


def is_reviewed(row: dict) -> bool:
    state = (row.get("TranslationStatus") or "").strip().upper()
    explicitly = (row.get("Reviewed") or "").strip().upper()
    return state in REVIEWED_STATES or explicitly in APPROVED_FLAGS


def load_project(project: Path):
    profile = json.loads((project / "project_profile.json").read_text(encoding="utf-8"))
    return profile, project / "translations" / "master.csv", project / "translations" / "glossary.csv"


def atomic_write_csv(path: Path, fields: list[str], rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}; provide a new output filename")
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def make_db(db: Path, projects: Path) -> dict:
    if not projects.is_dir():
        raise ValueError(f"Projects directory does not exist: {projects}")
    db.parent.mkdir(parents=True, exist_ok=True)
    temporary = db.with_name(db.name + ".new")
    if temporary.exists():
        raise FileExistsError(f"Temporary DB exists, refusing to overwrite: {temporary}")
    conn = sqlite3.connect(temporary)
    stats = dict(projects=0, approved_rows=0, rejected_unreviewed=0, rejected_unsafe_tokens=0,
                 missing_masters=0, glossary_terms=0, source_rows=0)
    try:
        conn.executescript('''
           CREATE TABLE memory (slug TEXT, title TEXT, platform TEXT, series TEXT,
             publisher TEXT, region TEXT, bank TEXT, entry_id TEXT, context_key TEXT,
             scene TEXT, speaker TEXT, source TEXT, source_norm TEXT, thai TEXT, status TEXT);
           CREATE INDEX idx_source ON memory(source_norm);
           CREATE INDEX idx_series ON memory(series);
           CREATE TABLE terms (slug TEXT, title TEXT, platform TEXT, series TEXT,
             publisher TEXT, source_term TEXT, thai_term TEXT);
           CREATE INDEX idx_term_series ON terms(series);
        ''')
        for project in sorted(projects.iterdir()):
            if not project.is_dir() or not (project / "project_profile.json").is_file():
                continue
            prof, master, glossary = load_project(project)
            stats["projects"] += 1
            slug = str(prof.get("project_slug") or project.name)
            title = str(prof.get("game_title") or project.name)
            platform = str(prof.get("platform") or "")
            series = norm(str(prof.get("series_id") or "")).casefold()
            publisher = norm(str(prof.get("publisher") or "")).casefold()
            region = str(prof.get("region") or "")
            if not master.is_file():
                stats["missing_masters"] += 1
            else:
                for row in read_csv(master):
                    source, thai = pick(row, *SOURCE_KEYS), pick(row, *THAI_KEYS)
                    if not (source.strip() and thai.strip()):
                        continue
                    stats["source_rows"] += 1
                    if not is_reviewed(row):
                        stats["rejected_unreviewed"] += 1
                        continue
                    if not token_safe(source, thai):
                        stats["rejected_unsafe_tokens"] += 1
                        continue
                    conn.execute("INSERT INTO memory VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                 (slug, title, platform, series, publisher, region,
                                  pick(row, "Bank"), pick(row, "ID"), pick(row, "Context_Key"),
                                  pick(row, "Scene"), pick(row, "Speaker"), source, norm(source), thai,
                                  pick(row, "TranslationStatus", "Reviewed")))
                    stats["approved_rows"] += 1
            if glossary.is_file():
                for g in read_csv(glossary):
                    en, th = pick(g, "Source_Term"), pick(g, "Thai_Term")
                    if not en.strip() or not th.strip() or str(g.get("Approved", "")).strip().upper() not in APPROVED_FLAGS:
                        continue
                    conn.execute("INSERT INTO terms VALUES (?,?,?,?,?,?,?)",
                                 (slug, title, platform, series, publisher, en, th))
                    stats["glossary_terms"] += 1
        conn.commit()
    except Exception:
        conn.close()
        temporary.unlink(missing_ok=True)
        raise
    conn.close()
    temporary.replace(db)  # publish only after a successful full rebuild
    stats["db"] = str(db)
    return stats


def comparable(row: sqlite3.Row, prof: dict):
    series = norm(str(prof.get("series_id") or "")).casefold()
    publisher = norm(str(prof.get("publisher") or "")).casefold()
    return bool(series and row["series"] == series), bool(publisher and row["publisher"] == publisher)


def candidate_conflict(candidates: list[dict]):
    # A conflict is specifically an exact source, same non-empty context, same family,
    # and incompatible approved targets. Conflicts are surfaced, not resolved blindly.
    by_key = {}
    for c in candidates:
        if c["Match_Type"] != "EXACT" or c["Context_Match"] != "YES":
            continue
        key = (c["Source_Text"], c["Context_Key"], c["Source_Series"])
        by_key.setdefault(key, set()).add(norm(c["Suggested_Thai"]))
    for c in candidates:
        key = (c["Source_Text"], c["Context_Key"], c["Source_Series"])
        c["Conflict"] = "YES" if len(by_key.get(key, ())) > 1 else "NO"
        if c["Conflict"] == "YES":
            c["Review_Status"] = "CONFLICT_REVIEW_REQUIRED"
            c["Reason"] = "Different approved translations exist for identical source/context"
    return candidates


def suggestions(project: Path, db: Path, output: Path, fuzzy_threshold: float = .9,
                max_per_row: int = 3, max_fuzzy_pool: int = 2000):
    prof, master, _ = load_project(project)
    if not master.is_file():
        raise FileNotFoundError(master)
    if not db.is_file():
        raise FileNotFoundError(db)
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    results, counters = [], dict(target_missing=0, exact=0, fuzzy=0, conflicts=0, rows_with_suggestions=0)
    try:
        for target in read_csv(master):
            source = pick(target, *SOURCE_KEYS)
            if not source.strip() or pick(target, *THAI_KEYS).strip():
                continue
            counters["target_missing"] += 1
            sn = norm(source)
            context = pick(target, "Context_Key")
            tok = tokens(source)
            match_rows = conn.execute("SELECT * FROM memory WHERE source_norm = ?", (sn,)).fetchall()
            exact = []
            for mem in match_rows:
                if mem["slug"] == (prof.get("project_slug") or project.name):
                    continue
                if tok != tokens(mem["source"]) or not token_safe(source, mem["thai"]):
                    continue
                exact.append((1.0, mem))
            fuzzy = []
            series = norm(str(prof.get("series_id") or "")).casefold()
            if not exact and series and len(sn) >= 14 and fuzzy_threshold <= 1:
                pool = conn.execute("SELECT * FROM memory WHERE series = ? AND length(source_norm) BETWEEN ? AND ? LIMIT ?",
                                    (series, max(1, int(len(sn) * .83)), int(len(sn) * 1.18) + 1,
                                     max_fuzzy_pool)).fetchall()
                for mem in pool:
                    if mem["slug"] == (prof.get("project_slug") or project.name):
                        continue
                    if tok != tokens(mem["source"]) or tok != tokens(mem["thai"]):
                        continue
                    sim = SequenceMatcher(None, sn, mem["source_norm"]).ratio()
                    if fuzzy_threshold <= sim < 1:
                        fuzzy.append((sim, mem))
            matches = exact or fuzzy
            candidates = []
            for similarity, mem in matches:
                same_series, same_publisher = comparable(mem, prof)
                ctx_match = bool(context and mem["context_key"] and context == mem["context_key"])
                reason = ("Same series and matching context; verify story/tone/UI"
                          if same_series and ctx_match and similarity == 1 else
                          "Same source string; context needs checking" if similarity == 1 else
                          "Similar source text only; do not copy blindly")
                candidates.append({
                    "ID": pick(target, "ID"), "Bank": pick(target, "Bank"),
                    "Source_Text": source, "Context_Key": context,
                    "Suggested_Thai": mem["thai"], "Source_Game": mem["title"],
                    "Source_Platform": mem["platform"], "Source_Project": mem["slug"],
                    "Source_Status": mem["status"], "Source_Series": mem["series"],
                    "Similarity": f"{similarity:.3f}", "Match_Type": "EXACT" if similarity == 1 else "FUZZY",
                    "Context_Match": "YES" if ctx_match else "NO",
                    "Review_Status": "REVIEW_REQUIRED", "Conflict": "NO", "Reason": reason,
                    "_rank": (similarity, same_series, ctx_match, same_publisher)
                })
            candidate_conflict(candidates)
            candidates.sort(key=lambda r: r["_rank"], reverse=True)
            seen = set()
            accepted = []
            for c in candidates:
                key = (c["Suggested_Thai"], c["Source_Game"], c["Match_Type"])
                if key in seen: continue
                seen.add(key)
                accepted.append({k: v for k, v in c.items() if not k.startswith("_")})
                if len(accepted) >= max_per_row: break
            results.extend(accepted)
            if accepted:
                counters["rows_with_suggestions"] += 1
                counters["exact" if exact else "fuzzy"] += 1
                counters["conflicts"] += int(any(r["Conflict"] == "YES" for r in accepted))
    finally:
        conn.close()
    atomic_write_csv(output, SUGGEST_FIELDS, results)
    return {**counters, "suggestions_written": len(results), "output": str(output),
            "note": "Suggestions only. Not applied; all require context review and original Thai typography QA."}


def term_occurs(source: str, term: str) -> bool:
    if not term: return False
    # Case-insensitive word boundaries around Latin terms, substring for other scripts.
    pattern = r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
    return re.search(pattern, source, re.IGNORECASE) is not None


def term_suggestions(project: Path, db: Path, output: Path):
    prof, master, _ = load_project(project)
    series = norm(str(prof.get("series_id") or "")).casefold()
    conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    result = []
    try:
        terms = conn.execute("SELECT * FROM terms").fetchall()
        for row in read_csv(master):
            src = pick(row, *SOURCE_KEYS)
            if not src.strip() or pick(row, *THAI_KEYS).strip(): continue
            for term in terms:
                if term["slug"] == (prof.get("project_slug") or project.name): continue
                if not term_occurs(src, term["source_term"]): continue
                result.append({"ID": pick(row, "ID"), "Bank": pick(row, "Bank"),
                               "Source_Text": src, "Term": term["source_term"],
                               "Thai_Term": term["thai_term"], "Source_Game": term["title"],
                               "Source_Platform": term["platform"], "Source_Project": term["slug"],
                               "Series_Match": "YES" if series and term["series"] == series else "NO",
                               "Review_Status": "TERM_SUGGESTION_REVIEW_REQUIRED"})
    finally:
        conn.close()
    result.sort(key=lambda x: (x["ID"], x["Series_Match"] != "YES", x["Term"], x["Source_Game"]))
    atomic_write_csv(output, TERM_FIELDS, result)
    return {"term_suggestions": len(result), "output": str(output),
            "note": "Glossary candidates only; game-specific nomenclature and rendering require review."}


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline reuse of reviewed Thai translations across retro-game projects")
    sub = p.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="Build a local SQLite memory from reviewed project translations")
    index.add_argument("--projects", default="projects")
    index.add_argument("--db", default="shared_memory/cross_project_tm.sqlite")
    suggest = sub.add_parser("suggest", help="Find cross-game candidate translations without changing masters")
    suggest.add_argument("--project", required=True)
    suggest.add_argument("--db", default="shared_memory/cross_project_tm.sqlite")
    suggest.add_argument("--output", required=True)
    suggest.add_argument("--fuzzy-threshold", type=float, default=.9)
    suggest.add_argument("--max-per-row", type=int, default=3)
    terms = sub.add_parser("terms", help="Find approved terminology across projects")
    terms.add_argument("--project", required=True)
    terms.add_argument("--db", default="shared_memory/cross_project_tm.sqlite")
    terms.add_argument("--output", required=True)
    a = p.parse_args(argv)
    try:
        if a.command == "index":
            out = make_db(Path(a.db), Path(a.projects))
        elif a.command == "suggest":
            if not (.7 <= a.fuzzy_threshold <= 1) or a.max_per_row < 1:
                raise ValueError("fuzzy threshold must be between 0.70 and 1; max-per-row >= 1")
            out = suggestions(Path(a.project), Path(a.db), Path(a.output), a.fuzzy_threshold, a.max_per_row)
        else:
            out = term_suggestions(Path(a.project), Path(a.db), Path(a.output))
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, FileNotFoundError, FileExistsError, sqlite3.Error, OSError, json.JSONDecodeError) as ex:
        print("ERROR:", ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
