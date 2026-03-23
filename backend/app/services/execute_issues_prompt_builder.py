from __future__ import annotations

from typing import Any


def build_execute_issues_prompt(precheck: dict[str, Any]) -> str:
    card = precheck["card"]
    worktree = precheck["worktree"]
    return "\n".join(
        [
            "请执行 execute-issues 过程。",
            f"card_id: {card['id']}",
            f"project_id: {card['project_id']}",
            f"title: {card['title']}",
            f"current_stage: {card['current_stage']}",
            f"project_root: {precheck['project_root']}",
            f"project_path: {precheck['project_path']}",
            f"requirements_path: {precheck['requirements_path']}",
            f"plan_path: {precheck['plan_path']}",
            f"issues_path: {precheck['issues_path']}",
            f"test_path: {precheck['output_paths']['test_path']}",
            f"worktree_path: {worktree['worktree_path']}",
            f"branch_name: {worktree['branch_name']}",
            "要求：CSV 是唯一状态源，Plan 与 requirements 是唯一语义源。",
            "要求：启动后进入 developing，只有真实完成后才推进 acceptance。",
        ]
    )
