#!/usr/bin/env python3
"""
Issues CSV 格式校验脚本
用法: python validate-csv.py <csv_path>
"""

import csv
import sys
from pathlib import Path

REQUIRED_HEADERS = [
    "id", "priority", "title", "description", "acceptance_criteria",
    "test_cases", "area", "refs", "dev_state", "test_state", "owner", "notes"
]

VALID_PRIORITY = {"P0", "P1", "P2"}
VALID_DEV_STATE = {"未开始", "进行中", "已完成"}
VALID_TEST_STATE = {"未开始", "进行中", "已完成", "失败"}
VALID_AREA = {"backend", "admin_frontend", "both", "infra"}


def validate(csv_path: str) -> list[str]:
    errors = []
    path = Path(csv_path)

    if not path.exists():
        return [f"文件不存在: {csv_path}"]

    # 读取时处理 BOM
    content = path.read_bytes()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
    text = content.decode('utf-8')

    reader = csv.DictReader(text.splitlines())

    # 校验表头
    if reader.fieldnames is None:
        return ["CSV 文件为空或无法解析"]

    missing = set(REQUIRED_HEADERS) - set(reader.fieldnames)
    if missing:
        errors.append(f"缺少必需列: {', '.join(sorted(missing))}")
        return errors

    extra = set(reader.fieldnames) - set(REQUIRED_HEADERS)
    if extra:
        errors.append(f"警告 - 存在额外列: {', '.join(sorted(extra))}")

    # 校验每一行
    for i, row in enumerate(reader, start=2):
        row_id = row.get("id", f"第{i}行")

        # id 非空
        if not row.get("id", "").strip():
            errors.append(f"第{i}行: id 为空")

        # priority
        p = row.get("priority", "").strip()
        if p and p not in VALID_PRIORITY:
            errors.append(f"{row_id}: priority 值非法 '{p}', 应为 {VALID_PRIORITY}")

        # acceptance_criteria 必填
        if not row.get("acceptance_criteria", "").strip():
            errors.append(f"{row_id}: acceptance_criteria 为空")

        # refs 必填
        if not row.get("refs", "").strip():
            errors.append(f"{row_id}: refs 为空")

        # test_cases 必填
        if not row.get("test_cases", "").strip():
            errors.append(f"{row_id}: test_cases 为空")

        # area
        a = row.get("area", "").strip()
        if a and a not in VALID_AREA:
            errors.append(f"{row_id}: area 值非法 '{a}', 应为 {VALID_AREA}")

        # dev_state
        ds = row.get("dev_state", "").strip()
        if ds and ds not in VALID_DEV_STATE:
            errors.append(f"{row_id}: dev_state 值非法 '{ds}', 应为 {VALID_DEV_STATE}")

        # test_state
        ts = row.get("test_state", "").strip()
        if ts and ts not in VALID_TEST_STATE:
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
        # 区分警告和错误
        real_errors = [e for e in errors if not e.startswith("警告")]
        sys.exit(1 if real_errors else 0)


if __name__ == "__main__":
    main()
