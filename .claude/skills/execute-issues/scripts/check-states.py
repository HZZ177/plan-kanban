#!/usr/bin/env python3
"""Issues CSV 状态检查脚本。

新流程固定 CSV schema：
    id,priority,title,refs,dev_state,test_state,owner,notes

用法: python check-states.py <csv_path>
输出当前 CSV 的进度概览。
"""

import csv
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "id", "priority", "title", "refs", "dev_state", "test_state", "owner", "notes",
]


def _read_rows(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        print(f"文件不存在: {csv_path}")
        sys.exit(1)

    content = path.read_bytes()
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]
    text = content.decode("utf-8")

    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        print("CSV 为空或无法解析")
        sys.exit(1)

    actual_headers = list(reader.fieldnames)
    if actual_headers != REQUIRED_HEADERS:
        print("CSV 表头不匹配")
        print("  期望:", ",".join(REQUIRED_HEADERS))
        print("  实际:", ",".join(actual_headers))
        sys.exit(1)

    return list(reader)


def check(csv_path: str):
    rows = _read_rows(csv_path)

    if not rows:
        print(f"Issues 进度概览: {csv_path}")
        print("  总计: 0 条")
        return

    total = len(rows)
    dev_not_started = sum(1 for r in rows if r.get("dev_state", "").strip() == "未开始")
    dev_in_progress = sum(1 for r in rows if r.get("dev_state", "").strip() == "进行中")
    dev_done = sum(1 for r in rows if r.get("dev_state", "").strip() == "已完成")

    test_not_started = sum(1 for r in rows if r.get("test_state", "").strip() == "未开始")
    test_in_progress = sum(1 for r in rows if r.get("test_state", "").strip() == "进行中")
    test_done = sum(1 for r in rows if r.get("test_state", "").strip() == "已完成")
    test_failed = sum(1 for r in rows if r.get("test_state", "").strip() == "失败")

    finished = [
        r for r in rows
        if r.get("dev_state", "").strip() == "已完成" and r.get("test_state", "").strip() == "已完成"
    ]
    blocked = [r for r in rows if "blocked:" in (r.get("notes") or "")]
    next_candidates = [
        r for r in rows
        if not (r.get("dev_state", "").strip() == "已完成" and r.get("test_state", "").strip() == "已完成")
    ]

    print(f"Issues 进度概览: {csv_path}")
    print(f"  总计: {total} 条")
    print(f"  已整体完成: {len(finished)}/{total}")
    print()
    print("  开发状态:")
    print(f"    - 未开始: {dev_not_started}")
    print(f"    - 进行中: {dev_in_progress}")
    print(f"    - 已完成: {dev_done}")
    print()
    print("  测试状态:")
    print(f"    - 未开始: {test_not_started}")
    print(f"    - 进行中: {test_in_progress}")
    print(f"    - 已完成: {test_done}")
    print(f"    - 失败: {test_failed}")

    if blocked:
        print()
        print(f"  阻塞: {len(blocked)} 条")
        for r in blocked:
            print(f"    - [{r.get('id')}] {r.get('title')}")

    if next_candidates:
        print()
        print("  下一条候选:")
        first = next_candidates[0]
        print(f"    - [{first.get('id')}] {first.get('title')}")
        print(f"      refs: {first.get('refs')}")


def main():
    if len(sys.argv) < 2:
        print("用法: python check-states.py <csv_path>")
        sys.exit(1)
    check(sys.argv[1])


if __name__ == "__main__":
    main()
