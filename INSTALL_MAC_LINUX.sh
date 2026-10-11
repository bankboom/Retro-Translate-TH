#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 tools/install_once.py install
printf '\nInstallation complete. Open ~/RetroThaiProjects in Codex and start a new chat.\n'
