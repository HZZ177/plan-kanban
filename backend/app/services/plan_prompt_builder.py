from __future__ import annotations

from pathlib import Path
from typing import Any


def build_plan_prompt(precheck: dict[str, Any]) -> str:
    card = precheck["card"]
    output_paths = precheck["output_paths"]
    requirements_path = precheck["requirements_path"]
    project_root = precheck["project_root"]
    stage_files = precheck.get("stage_files") or []
    return "\n".join(
        [
            "请基于当前卡片执行 plan skill，生成执行合同正文与 Issues CSV。",
            f"card_id: {card['id']}",
            f"project_id: {card['project_id']}",
            f"title: {card['title']}",
            f"summary: {card['summary']}",
            f"owner: {card['owner']}",
            f"priority: {card['priority']}",
            f"current_stage: {card['current_stage']}",
            f"raw_requirement: {card['raw_requirement']}",
            f"requirements_path: {requirements_path}",
            f"project_root: {project_root}",
            f"cwd: {precheck['cwd']}",
            f"plan_path: {output_paths['plan_path']}",
            f"issues_path: {output_paths['issues_path']}",
            f"test_path: {output_paths['test_path']}",
            f"stage_files: {', '.join(stage_files)}",
            f"plan_skill_path: {Path(__file__).resolve().parents[3] / '.claude' / 'skills' / 'plan' / 'SKILL.md'}",
            "要求：Plan 必须包含 View 1: Review 与 View 2: Issue Contract。",
            "要求：Issues CSV 必须可由 Plan 的 Issue Contract 直接映射，并通过 validate-csv.py 校验。",
            "要求：不要输出模板占位 issue，必须生成可执行的真实 issue 列表。",
        ]
    )
