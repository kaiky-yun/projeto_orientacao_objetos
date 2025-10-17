#!/usr/bin/env bash
set -e
if ! command -v python3.12 >/dev/null 2>&1; then
  echo "⚠️  python3.12 não encontrado. Instale com: brew install python@3.12"
  exit 1
fi
[ -d .venv ] || python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt >/dev/null
python3.12 -m finance.cli
