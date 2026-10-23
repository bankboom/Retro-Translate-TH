# Pokémon Omega Paradox TH — P5.6 REAL BPS: 6 White TH Native donor messages

**Actual binary work (24 October 2026 local checkpoint).** Unlike previous synthetic-only P5.3–P5.5 CI work, this checkpoint processed the owner's full ROM files and private 56,700 / 25,976 row CSVs locally and produced a real BPS artifact for the owner. **NOT a full-game 100% release and NOT emulator-tested on these six new scenes.**

## Exact source inputs and proof

- Clean Omega ROM SHA256 `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`
- Pokémon White TH ROM SHA256 `1daeb35e3d508196cb84697f77179f3e62a31824cb68a1ce49e8ef68e2d7702c`
- English White ROM SHA256 `b288bb061fd646894f5059f55cd0a1efb13b4f0cfd3d9e06e9e42a5bd9431ac6`
- P3.5 56,700 inventory SHA256 `d5a680554e1130eb63b99f515b410937179acfb7f943c2420a4e7f4010f65e34`
- White Thai 25,976 TM SHA256 `c352a547d9b44dfc881eafddb1e146e9f1fd4b5a2ec49678e99debcd4b688557`
- P4.6 **source-ROM** BPS SHA256 `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`; **independently reapplied** in a container against the exact clean ROM, yielding target SHA256 `945c0bc11b137580311af9c38b6f62852a6cf688e16a89854e7d64ed00427a04`.

## Real new full-source native-donor inventory

One pass over **25,976** original White Thai TM records and **56,700** Omega inventory records found:
- 823 Omega messages have at least one segment of exact same-file/renderer-bank English -> native PUA source that fits the source segment's current fixed capacity.
- **53** untranslated/review-pending Omega messages have *all* visible segments backed by unique same-bank exact-English native donor fragments, with each segment's PUA codeunit count <= original ASCII length.
- These 53 are **candidates**, not 53 automatically context-approved messages. The 25,976 master includes many reordered page/control symbols and 284 conflicting same-bank phrase keys; only strict same-command-sequence and unique donor mappings were admitted.
- Six very short messages were selected for the minimal-risk pilot because maximum right-side padding is <=3 code units; further context and pixel QA are required for longer messages.

## P5.6 changed message IDs (exactly SIX)

| Archive | File ID | Message ID | English source mnemonic |
| --- | ---: | ---: | --- |
| system | 195 | 3 | short '...Um, hello?!' utterance |
| story | 87 | 6 | local NPC bat-related utterance |
| story | 99 | 2 | 'Nuha nuha nuhaha!' |
| story | 105 | 2 | 'Skee!' |
| story | 159 | 57 | 'Wahaha!' |
| story | 444 | 8 | 'Chip kwip!' |

**Each segment's native Thai bytes were checked directly in the Pokémon White TH ROM** and its paired English original in the White English ROM, in the same `archive/file_id` bank. No guessed Unicode Thai->PUA encoding and no synthetic replacement were used. Native font PUA bitmap nonblank verified for **37 distinct selected PUA codepoints across all 3 NFTR fonts**. All 6 modified strings preserve exact plaintext UTF-16 lengths, encrypted message slot sizes, **script control token operation sequence and positions**; no pointer relocation.

## Applied patch and independent 56,700-message regression

- P5.6 original-ROM BPS filename: `Pokemon_Omega_Paradox_TH_P5_6_6_Native_Donor_Pilot_from_Clean_Omega.bps`
- P5.6 **BPS SHA256**: `6f8cfe2caafebebe2f4710ac1b4a73f08763be4cb6ebcbc41df9fd4450e07379`
- P5.6 **APPLIED TARGET SHA256**: `93df7891d410ec2eb785fe4711f90aa275e823e01ff4cc892ac4a461b93d9483`
- Applied real BPS independently against clean Omega ROM: source CRC PASS, patch CRC PASS, applied target CRC PASS, applied target SHA PASS.
- Independently decrypted **all 56,700 Omega messages** from both P4.6 and P5.6. **Exactly the six listed message IDs differ**; every other message is identical after decryption. The existing Cynthia P4.6 content remains unchanged.
- Exactly same ROM byte length, file map/FAT paths, three-font NARC bytes and all non-target member data.
- **Source ROM is not changed**. BPS payload only; no copyrighted original game ROM has been uploaded to the public repository.
- Private conversation deliverables include this BPS and owner-facing ZIP with reproducible scripts and detailed QA JSONs. They are not part of public GitHub release assets.

## User emulator QA NOT YET COMPLETED for P5.6

The user previously tested P4.6 Cynthia clauses, dialogue advance, Save/Load = scoped PASS. The six *new* P5.6 messages have NOT been independently played or screenshot-tested on melonDS Android. **G3/G4 still PENDING for these six**.

For player testing, apply P5.6 BPS directly to **the exact clean Omega source**, never to P4.6 already patched ROM. Verify basic boot/continue/save/load and display of new six messages as each becomes reachable; note `????`, clipping, fonts, progression. Revert to P4.6 if any regression appears.

## Why this is not full localization

P3.5 has 25,001 Thai PUA-coded messages as a snapshot, but 20,096 other messages are queued for translation/context classification; 270 more complete Omega full-message Unicode Thai DRAFTS were created across P3.9–P5.2 (these are **NOT** newly encoded or injected in this P5.6 build). A literal 100% declaration would be unsupported. Remaining work: approve semantic Unicode->PUA mapping for new text beyond exact donor phrases; translate/QA full remaining inventory, preserve controls & pixel layouts, full playthrough including battle/items/menus and any English text embedded in graphical assets.

## Next single focused task, no repeated pilot loops

1. User-scoped emulator smoke test of P5.6; P4.6 remains stable rollback until passed.
2. Extend to additional **source-exact, context-valid native donor candidates** with scene QA and localized padding/layout constraints, not all 53 blindly.
3. For remaining new Thai Unicode drafts, solve and certify actual Thai grapheme/cluster -> native PUA mapping and safe MSG/NARC writer per bank, rather than treating PUA glyph count as semantic mapping.
4. Continue 20,096 review statuses and full original+modified ROM G0–G5 evidence to 100%.

**Status:** P5.6 original-ROM BPS genuinely built + source/patch/target CRC/SHA + full text-diff regression **PASS**; P5.6 emulator **PENDING**; entire-game 100% **PENDING**.
