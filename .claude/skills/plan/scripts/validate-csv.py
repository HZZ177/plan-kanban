#!/usr/bin/env python3
"""Issues CSV 格式校验脚本。

新流程固定 CSV schema：
    id,priority,title,refs,dev_state,test_state,owner,notes

用法: python validate-csv.py <csv_path>
"""

import csv
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "id", "priority", "title", "refs", "dev_state", "test_state", "owner", "notes",
]

VALID_PRIORITY = {"P0", "P1", "P2"}
VALID_DEV_STATE = {"未开始", "进行中", "已完成"}
VALID_TEST_STATE = {"未开始", "进行中", "已完成", "失败"}


def validate(csv_path: str) -> list[str]:
    errors = []
    path = Path(csv_path)

    if not path.exists():
        return [f"文件不存在: {csv_path}"]

    content = path.read_bytes()
    if content.startswith(b"\xef\xbb\xbf"):
        content = content[3:]
    text = content.decode("utf-8")

    reader = csv.DictReader(text.splitlines())

    if reader.fieldnames is None:
        return ["CSV 文件为空或无法解析"]

    actual_headers = list(reader.fieldnames)
    if actual_headers != REQUIRED_HEADERS:
        errors.append(
            "表头不匹配: 期望为 " + ",".join(REQUIRED_HEADERS) + " ; 实际为 " + ",".join(actual_headers)
        )
        return errors

    for i, row in enumerate(reader, start=2):
        row_id = row.get("id", f"第{i}行")

        if not row.get("id", "").strip():
            errors.append(f"第{i}行: id 为空")
        if not row.get("title", "").strip():
            errors.append(f"{row_id}: title 为空")
        if not row.get("refs", "").strip():
            errors.append(f"{row_id}: refs 为空")

        p = row.get("priority", "").strip()
        if p not in VALID_PRIORITY:
            errors.append(f"{row_id}: priority 值非法 '{p}', 应为 {VALID_PRIORITY}")

        ds = row.get("dev_state", "").strip()
        if ds not in VALID_DEV_STATE:
            errors.append(f"{row_id}: dev_state 值非法 '{ds}', 应为 {VALID_DEV_STATE}")

        ts = row.get("test_state", "").strip()
        if ts not in VALID_TEST_STATE:
            errors.append(f"{row_id}: test_state 值非法 '{ts}', 应为 {VALID_TEST_STATE}")

    return errors


def main():
    if len(sys.argv) < 2:
        print("用法: python validate-csv.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    errors = validate(csv_path)

    if not errors:
        print(f"校验通过: {csv_path}")
        sys.exit(0)
    else:
        print(f"校验发现 {len(errors)} 个问题:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
