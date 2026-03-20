from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_contract
from backend.app.services.issue_projection_service import build_issue_rows
from backend.app.services.issues_csv_service import generate_issues_csv, validate_issues_csv
from backend.app.services.plan_file_service import build_plan_paths, write_plan_file
from backend.app.services.plan_precheck_service import run_plan_precheck
from backend.app.services.plan_prompt_builder import build_plan_prompt
from backend.app.services.process_state_service import update_process_state
from backend.app.services.session_service import create_session_record, session_to_payload
from common.core.exceptions import ValidationError


def _default_issue_contract() -> list[dict[str, Any]]:
    return [
        {
            "id": "PLAN-001",
            "priority": "P0",
            "title": "补全执行合同",
            "design_refs": ["docs/Plan-Kanban-需求与架构设计文档.md:1401"],
            "code_refs": ["backend/app/services/plan_process_service.py (generated)"],
            "notes": "generated-by:plan-process",
        }
    ]


def _build_plan_markdown(card_title: str, requirements_path: str, issues_path: str) -> str:
    created_at = datetime.now(timezone.utc).isoformat()
    return f"""---
mode: plan
cwd: {Path(__file__).resolve().parents[3]}
task: {card_title}
complexity: medium
created_at: {created_at}
requirements_path: {requirements_path}
issues_path: {issues_path}
contract_version: v3
---

# Plan: {card_title}

## View 1: Review

### 任务概述

基于当前 plan 阶段卡片生成执行合同与 CSV 投影。

### 设计来源

#### 主需求文档

- `{requirements_path}`

#### 默认沿用的设计

- `{requirements_path}:1401`

#### 本次 Plan 的覆盖 / 补充决策

- 采用最小闭环生成单条执行合同。

### 需求边界（已确认）

#### 本次必须实现

- 生成 Plan 文件
- 生成并校验 CSV

#### 本次明确不做

- 不扩展额外 issue 拆分策略

#### TODO 占位 / 并行模块策略

- 后续可替换为真实大模型产物

### 现状分析

当前后端已具备 card/session/process 基础能力，可承接 plan 落盘。

### 关键决策

- **决策 1**：使用固定模板生成最小可执行 Plan — 理由：先打通 plan 到 contract 的最短闭环。

### 否决方案

- 直接跳过 Plan 文件写入 — 原因：违反 Plan 是合同正文的要求。

### 执行约束

- Plan 是合同正文
- CSV 由 Plan 直接映射生成

### 测试策略

#### 测试类型

接口测试、服务测试

#### 测试用例

| 功能点 | 测试用例 | 场景 | 预期结果 |
|--------|---------|------|---------|
| plan 落盘 | 触发 generate-contract | 正常 | 生成 Plan 与 CSV，并推进到 contract |

#### 测试文件位置

测试文件统一放在 `.dev/test/` 目录下，命名为 `test_plan-kanban-full-platform.py`。

### 风险与注意事项

- 当前为最小模板生成实现

### 参考

- `{requirements_path}:1401`

---

## View 2: Issue Contract

### Issue 列表概览

| ID | Priority | Title | Depends On | Summary |
|----|----------|-------|------------|---------|
| PLAN-001 | P0 | 补全执行合同 | 无 | 生成后续可继续扩展的最小执行合同 |

### PLAN-001 补全执行合同

- `id`: PLAN-001
- `priority`: P0
- `title`: 补全执行合同
- `summary`: 生成后续可继续扩展的最小执行合同。
- `design_refs`:
  - `{requirements_path}:1401`
- `code_refs`:
  - `backend/app/services/plan_process_service.py`
- `acceptance_criteria`:
  - 可映射生成 CSV
  - 产物可被 execute-issues 继续消费
- `test_cases`:
  - 验证生成正常路径
  - 验证 CSV 校验通过
- `constraints`:
  - Plan 是合同正文
  - CSV 由 Plan 直接映射生成
- `depends_on`: 无
- `notes`: generated-by:plan-process

---

## CSV Projection

```text
id,priority,title,refs,dev_state,test_state,owner,notes
```
"""


async def start_plan_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    precheck = await run_plan_precheck(session, card_id)
    card = await get_card_or_raise(session, card_id)
    session_record = await create_session_record(session, card_id, stage_key="plan", session_type="skill_plan")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="running",
            active_process_session_id=session_record.id,
        ),
    )
    return {
        "precheck": precheck,
        "session": session_to_payload(session_record),
        "prompt": build_plan_prompt(card, precheck["requirements_path"]),
    }


async def finish_plan_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    precheck = await run_plan_precheck(session, card_id)
    card = await get_card_or_raise(session, card_id)
    plan_path, issues_path, _basename = build_plan_paths(card.title)
    plan_content = _build_plan_markdown(card.title, precheck["requirements_path"], str(issues_path))
    write_plan_file(plan_path, plan_content)
    issue_rows = build_issue_rows(_default_issue_contract())
    generate_issues_csv(issue_rows, issues_path)
    validate_issues_csv(issues_path)

    card.plan_path = str(plan_path)
    card.issues_path = str(issues_path)
    await session.flush()
    await advance_card_to_contract(session, card_id)
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="finished",
            active_process_session_id=card.active_process_session_id,
        ),
    )
    updated_card = await get_card_or_raise(session, card_id)
    return {
        "card_id": updated_card.id,
        "current_stage": updated_card.current_stage,
        "plan_path": updated_card.plan_path,
        "issues_path": updated_card.issues_path,
    }


async def fail_plan_process(session: AsyncSession, card_id: str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValidationError("Failure reason cannot be empty")
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "plan":
        raise ValidationError("plan 失败回滚只能发生在 plan 阶段")
    if card.active_process_type != "skill_plan":
        raise ValidationError("当前卡片没有运行中的 plan process")
    if card.active_process_status not in {"running", "failed"}:
        raise ValidationError("只有运行中或失败中的 plan process 才能回滚")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="failed",
            active_process_session_id=card.active_process_session_id,
        ),
    )
    refreshed = await get_card_or_raise(session, card_id)
    return {
        "card_id": refreshed.id,
        "current_stage": refreshed.current_stage,
        "active_process_type": refreshed.active_process_type,
        "active_process_status": refreshed.active_process_status,
        "reason": reason,
    }


