$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"
& $Python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
