from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from common.core.config import get_settings
from common.core.exceptions import ValidationError


def _plan_python() -> str:
    settings = get_settings()
    root = settings.project_root
    candidates = [root / ".venv" / "Scripts" / "python.exe", root / ".venv" / "bin" / "python"]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    raise ValidationError("Virtualenv python not found")


def generate_issues_csv(rows: list[dict], csv_path: Path) -> Path:
    python = _plan_python()
    script_path = get_settings().project_root / ".claude" / "skills" / "plan" / "scripts" / "generate-csv.py"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(rows, handle, ensure_ascii=False)
        temp_json_path = Path(handle.name)
    try:
        result = subprocess.run(
            [python, str(script_path), str(temp_json_path), str(csv_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValidationError((result.stderr or result.stdout).strip() or "generate csv failed")
        return csv_path
    finally:
        temp_json_path.unlink(missing_ok=True)


def validate_issues_csv(csv_path: Path) -> Path:
    python = _plan_python()
    script_path = get_settings().project_root / ".claude" / "skills" / "plan" / "scripts" / "validate-csv.py"
    result = subprocess.run([python, str(script_path), str(csv_path)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ValidationError((result.stdout or result.stderr).strip() or "validate csv failed")
    return csv_path
