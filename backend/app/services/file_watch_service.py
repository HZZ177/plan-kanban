from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.stage_file_service import list_stage_files


async def poll_stage_files(session: AsyncSession, card_id: str) -> dict[str, Any]:
    files = await list_stage_files(session, card_id)
    return {
        "count": len(files),
        "files": [
            {
                **item,
                "modified": Path(item["path"]).stat().st_mtime if Path(item["path"]).exists() else None,
            }
            for item in files
        ],
    }
