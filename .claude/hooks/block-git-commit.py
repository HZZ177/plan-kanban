"""
PreToolUse hook: 阻止 Claude 自动执行 git commit/push 等操作
退出码 2 = 阻止操作，stderr 内容会反馈给 Claude
"""
import sys
import json
import re

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

if re.search(r"git\s+(commit|push)", cmd):
    print("Blocked: git commit/push must be done manually after human verification.", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
