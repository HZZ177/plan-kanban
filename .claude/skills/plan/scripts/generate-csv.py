#!/usr/bin/env python3
"""Issues CSV 生成脚本 — 从 JSON 数据生成 UTF-8 BOM 的标准 CSV。

新流程固定 CSV schema：
    id,priority,title,refs,dev_state,test_state,owner,notes

用法:
    python generate-csv.py <json_input> <csv_output>
"""

import csv
import json
import sys
from pathlib import Path

FIELDNAMES = [
    "id", "priority", "title", "refs", "dev_state", "test_state", "owner", "notes",
]

DEFAULTS = {
    "dev_state": "未开始",
    "test_state": "未开始",
    "owner": "",
    "notes": "",
}


def generate(json_path: str, csv_path: str) -> int:
    raw = Path(json_path).read_text(encoding="utf-8")
    rows = json.loads(raw)

    if not isinstance(rows, list):
        print(f"错误: JSON 根元素应为数组，实际为 {type(rows).__name__}", file=sys.stderr)
        sys.exit(1)

    for row in rows:
        for key, default in DEFAULTS.items():
            if key not in row or row[key] is None:
                row[key] = default

    for i, row in enumerate(rows):
        missing = [f for f in FIELDNAMES if f not in row]
        if missing:
            print(f"错误: 第{i+1}条缺少字段: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    output = Path(csv_path)
    if output.exists():
        print(f"错误: 输出文件已存在: {csv_path}", file=sys.stderr)
        sys.exit(1)

    with open(output, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
            quoting=csv.QUOTE_ALL,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main():
    if len(sys.argv) != 3:
        print("用法: python generate-csv.py <json_input> <csv_output>")
        sys.exit(1)

    json_path, csv_path = sys.argv[1], sys.argv[2]

    if not Path(json_path).exists():
        print(f"错误: 输入文件不存在: {json_path}", file=sys.stderr)
        sys.exit(1)

    count = generate(json_path, csv_path)
    print(f"生成成功: {csv_path} ({count} 条 issue)")


if __name__ == "__main__":
    main()
