#!/usr/bin/env python3
"""
Issues CSV 状态检查脚本
用法: python check-states.py <csv_path>
输出当前 CSV 的进度概览
"""

import csv
import sys
from pathlib import Path


def check(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        print(f"文件不存在: {csv_path}")
        sys.exit(1)

    content = path.read_bytes()
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
    text = content.decode('utf-8')

    reader = csv.DictReader(text.splitlines())
    rows = list(reader)

    if not rows:
        print("CSV 为空")
        sys.exit(0)

    total = len(rows)
    dev_done = sum(1 for r in rows if r.get("dev_state", "").strip() == "已完成")
    test_done = sum(1 for r in rows if r.get("test_state", "").strip() == "已完成")
    test_failed = sum(1 for r in rows if r.get("test_state", "").strip() == "失败")
    blocked = [r for r in rows if "blocked:" in r.get("notes", "")]

    print(f"Issues 进度概览: {csv_path}")
    print(f"  总计: {total} 条")
    print(f"  开发完成: {dev_done}/{total}")
    print(f"  测试通过: {test_done}/{total}")
    if test_failed:
        print(f"  测试失败: {test_failed}/{total}")
    if blocked:
        print(f"  阻塞: {len(blocked)} 条")
        for r in blocked:
            print(f"    - [{r.get('id')}] {r.get('title')}")


def main():
    if len(sys.argv) < 2:
        print("用法: python check-states.py <csv_path>")
        sys.exit(1)
    check(sys.argv[1])


if __name__ == "__main__":
    main()
