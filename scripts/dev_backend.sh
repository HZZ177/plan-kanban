#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT_DIR/.venv/Scripts/python.exe" -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
