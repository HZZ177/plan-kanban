---
name: "plan-to-issues"
description: "将 .dev/plans/ 中的 Plan 文件转换为结构化的 Issues CSV 任务合同"
invocation: "manual"
argument-hint: "<plan 文件路径，默认取 .dev/plans/ 最新>"
---

你现在处于「Plan → Issues CSV 模式」。

目标：把 `.dev/plans/*.md` 转换为 `.dev/issues/*.csv`，作为可协作维护的任务边界合同。

核心原则：**CSV 是任务边界合同，不是 AI 自嗨文档**。每条必须明确「做什么、怎么测、怎么验收」。测试用例是合同的核心部分——它定义了需求的边界和功能形状。

## 一、输入

1. `$ARGUMENTS` 为 Plan 文件路径（相对/绝对均可）
   - 若为空：选择 `.dev/plans/` 下**最新**的 `*.md`
   - 若找不到或内容不足：用 1-2 句话说明，不长篇追问
2. 读取 Plan 文件内容，必要时根据「参考」中的文件路径进一步读取少量上下文（只读、最小必要）

## 二、拆分规则

1. **默认粒度**：一个 Phase 对应一条 issue
2. **允许拆分**：若某 Phase 包含明显独立的多项工作（如前后端两条链路），可拆为多行
3. **规模控制**：一般 5-20 行最易维护；超过 20 行优先合并同类项

## 三、CSV Schema（固定表头）

使用 `templates/issues-template.csv` 中的表头：

```
id,priority,title,description,acceptance_criteria,test_cases,area,refs,dev_state,test_state,owner,notes
```

字段说明：

| 字段 | 含义 | 填写要求 |
|------|------|---------|
| `id` | 唯一标识 | `<PREFIX>-010`、`<PREFIX>-020` 以 10 递增，PREFIX 从 Plan 名提取 |
| `priority` | 优先级 | `P0\|P1\|P2` |
| `title` | 一句话标题 | 短、可读 |
| `description` | 做什么 | 1-2 句，强调边界，不写实现细节 |
| `acceptance_criteria` | 验收标准 | **必填**，可测试可验证，尽量量化 |
| `test_cases` | 测试用例 | **必填**，从 Plan 测试策略中提取。描述具体的测试场景、输入、预期输出。多个用例用 `\|` 分隔 |
| `area` | 领域 | `backend\|frontend\|both\|infra` |
| `refs` | 文件引用 | **必填**，`path:line` 格式，多个用 `;` 分隔 |
| `dev_state` | 开发状态 | 默认 `未开始` |
| `test_state` | 测试状态 | 默认 `未开始` |
| `owner` | 负责人 | 默认留空 |
| `notes` | 备注 | 默认留空 |

## 四、状态枚举（禁止百分比）

- `dev_state`：`未开始|进行中|已完成`
- `test_state`：`未开始|进行中|已完成|失败`

## 五、文件规范

1. **快照文件**（必须创建）：`.dev/issues/YYYY-MM-DD_HH-mm-ss-<slug>.csv`
2. **编码**：UTF-8 with BOM（Excel 友好）
   - Windows PowerShell：使用 `.NET UTF8Encoding($true)` 写文件
   - 或通过 Python 脚本写入
3. **CSV 格式**：所有字段统一双引号包裹，内部 `"` 用 `""` 转义
4. 确保不覆盖已有文件

## 六、校验

生成后使用项目虚拟环境的 Python 运行校验脚本：

1. 检查项目根目录下 `.venv/Scripts/python.exe`（Windows）或 `.venv/bin/python`（Unix/macOS），以 `$VENV_PYTHON` 表示
2. 如果虚拟环境不存在，回退使用 `python`

```bash
$VENV_PYTHON scripts/validate-csv.py <csv路径>
```

校验内容：
- 表头完整性
- 状态字段枚举值合法性
- refs 非空
- acceptance_criteria 非空
- test_cases 非空

## 七、输出格式

完成后在对话中输出：
- 生成的 CSV 路径
- issue 数量统计
- 各优先级分布（P0/P1/P2 各多少条）
- 风险/注意事项（如有）
