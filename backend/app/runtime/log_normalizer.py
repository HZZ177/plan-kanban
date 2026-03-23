from __future__ import annotations

import json
from typing import Any

IGNORED_EVENT_TYPES = {"system"}
SUMMARY_PREVIEW_LIMIT = 240


def _extract_message(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if not payload:
        return None
    message = payload.get("message") if isinstance(payload.get("message"), dict) else payload
    return message if isinstance(message, dict) else None


def _extract_content_blocks(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    message = _extract_message(payload)
    content_blocks = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content_blocks, list):
        return []
    return [block for block in content_blocks if isinstance(block, dict)]


def _extract_text_parts(payload: dict[str, Any] | None) -> list[str]:
    parts: list[str] = []
    for block in _extract_content_blocks(payload):
        if block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text)
    return parts


def _extract_thinking_parts(payload: dict[str, Any] | None) -> list[str]:
    parts: list[str] = []
    for block in _extract_content_blocks(payload):
        if block.get("type") == "thinking":
            thinking = block.get("thinking")
            if isinstance(thinking, str) and thinking.strip():
                parts.append(thinking)
    return parts


def _extract_message_id(payload: dict[str, Any] | None) -> str | None:
    message = _extract_message(payload)
    if isinstance(message, dict):
        message_id = message.get("id")
        if isinstance(message_id, str) and message_id.strip():
            return message_id
    return None


def _build_tool_use_entry(payload: dict[str, Any], message_id: str | None) -> dict[str, Any] | None:
    for block in _extract_content_blocks(payload):
        if block.get("type") != "tool_use":
            continue
        tool_id = block.get("id") if isinstance(block.get("id"), str) else None
        tool_name = block.get("name") if isinstance(block.get("name"), str) else "工具"
        tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
        summary = tool_name
        if isinstance(tool_input.get("description"), str) and tool_input.get("description"):
            summary = f"{tool_name} · {tool_input['description']}"
        elif isinstance(tool_input.get("command"), str) and tool_input.get("command"):
            summary = f"{tool_name} · {tool_input['command']}"
        elif isinstance(tool_input.get("url"), str) and tool_input.get("url"):
            summary = f"{tool_name} · {tool_input['url']}"
        elif isinstance(tool_input.get("question"), str) and tool_input.get("question"):
            summary = f"{tool_name} · {tool_input['question']}"
        merge_key = tool_id or message_id or tool_name
        return {
            "entry_type": "tool_use",
            "role": "tool",
            "content": summary,
            "payload": {
                "merge_key": merge_key,
                "tool_id": tool_id,
                "tool_name": tool_name,
                "tool_input": tool_input,
                "raw_block": block,
            },
            "merge_key": merge_key,
        }
    return None


def _build_tool_result_entry(payload: dict[str, Any], message_id: str | None) -> dict[str, Any] | None:
    blocks = _extract_content_blocks(payload)
    for block in blocks:
        if block.get("type") != "tool_result":
            continue
        tool_use_id = block.get("tool_use_id") if isinstance(block.get("tool_use_id"), str) else None
        content = block.get("content") if isinstance(block.get("content"), str) else ""
        is_error = bool(block.get("is_error"))
        merge_key = tool_use_id or message_id or "tool_result"
        return {
            "entry_type": "tool_result",
            "role": "tool",
            "content": content or ("工具调用失败" if is_error else "工具调用完成"),
            "payload": {
                "merge_key": merge_key,
                "tool_use_id": tool_use_id,
                "is_error": is_error,
                "tool_use_result": payload.get("tool_use_result"),
                "raw_block": block,
            },
            "merge_key": merge_key,
        }
    return None


def _build_result_summary_entry(payload: dict[str, Any]) -> dict[str, Any]:
    subtype = payload.get("subtype") if isinstance(payload.get("subtype"), str) else "unknown"
    duration_ms = payload.get("duration_ms")
    stop_reason = payload.get("stop_reason") if isinstance(payload.get("stop_reason"), str) else ""
    result_text = payload.get("result") if isinstance(payload.get("result"), str) else ""
    summary = f"执行结束 · {subtype}"
    if isinstance(duration_ms, int):
        summary += f" · {duration_ms}ms"
    if stop_reason:
        summary += f" · {stop_reason}"
    return {
        "entry_type": "summary",
        "role": "assistant",
        "content": summary,
        "payload": {
            "result_text": result_text,
            "result_preview": result_text[:SUMMARY_PREVIEW_LIMIT],
            "duration_ms": duration_ms,
            "num_turns": payload.get("num_turns"),
            "stop_reason": stop_reason,
            "usage": payload.get("usage"),
            "permission_denials": payload.get("permission_denials"),
            "subtype": subtype,
        },
    }


def normalize_log_event(event: dict[str, Any]) -> dict[str, Any] | None:
    event_type = event.get("event_type", "raw")
    raw_text = event.get("raw_text") or event.get("content") or ""
    payload = event.get("payload")

    if event_type == "raw" and isinstance(raw_text, str):
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            payload = parsed
            event_type = parsed.get("type") or parsed.get("subtype") or event_type

    if not isinstance(payload, dict):
        payload = None

    if event_type in IGNORED_EVENT_TYPES:
        return None

    message_id = _extract_message_id(payload)

    if event_type == "assistant":
        text_parts = _extract_text_parts(payload)
        if text_parts:
            return {
                "entry_type": "assistant_text",
                "role": "assistant",
                "content": "\n\n".join(text_parts),
                "payload": payload,
                "merge_key": message_id,
            }

        tool_use_entry = _build_tool_use_entry(payload or {}, message_id)
        if tool_use_entry is not None:
            return tool_use_entry

        thinking_parts = _extract_thinking_parts(payload)
        if thinking_parts or any(block.get("type") == "thinking" for block in _extract_content_blocks(payload)):
            thinking_text = "\n\n".join(thinking_parts).strip() or "Claude 正在思考"
            return {
                "entry_type": "thinking",
                "role": "assistant",
                "content": thinking_text,
                "payload": {
                    **(payload or {}),
                    "merge_key": message_id,
                },
                "merge_key": message_id,
            }

        return None

    if event_type == "user":
        tool_result_entry = _build_tool_result_entry(payload or {}, message_id)
        if tool_result_entry is not None:
            return tool_result_entry
        return None

    if event_type == "result" and payload is not None:
        return _build_result_summary_entry(payload)

    if event_type in {"stderr", "error"}:
        return {
            "entry_type": "error",
            "role": "assistant",
            "content": raw_text if isinstance(raw_text, str) else str(raw_text),
            "payload": payload,
        }

    if isinstance(raw_text, str) and raw_text.strip():
        return {
            "entry_type": "assistant_text",
            "role": "assistant",
            "content": raw_text,
            "payload": payload,
        }

    return None
