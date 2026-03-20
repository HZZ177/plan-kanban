---
name: "execute-issues"
description: "基于 Issues CSV 连续执行任务：以 CSV 为状态源、以需求文档和 Plan 为语义源完成所有 issue"
invocation: "manual"
argument-hint: "<issues CSV 文件路径>"
---

你现在处于「Issues 执行模式」。

目标：以 `.dev/issues/*.csv` 为**状态源**，并结合对应的需求文档与 Plan 文件中的 **Review View / Issue Contract**，连续完成所有 issue，最后整体交付给用户验收。

## 一、核心思想

这套新流程中，三类文件职责严格分离：

- **需求文档**：一级设计源，保存时序、逻辑分块、模块边界和主要技术路径
- **Plan**：合同正文
  - `View 1: Review` 负责解释为什么这样做
  - `View 2: Issue Contract` 负责定义每条 issue 的完整执行边界、设计锚点、测试和约束
- **Issues CSV**：状态投影，只负责执行顺序、状态流转和中断恢复

**强制要求**：
- CSV 是**唯一状态源**
- 需求文档 + Plan 是**唯一语义源**
- 执行时绝不能只看 CSV 就直接写代码
- 每条 issue 开始前，必须先深入阅读：
  1. 对应需求文档中的设计段落（`design_refs`）
  2. 对应 Plan 的 `View 1: Review` 中的关键决策 / 覆盖决策 / 执行约束
  3. 对应 Plan 的 `View 2: Issue Contract` 条目
  4. 对应代码 refs
- **不能偏离**需求文档和 Plan 中已经确认的技术路径与约束；如发现冲突、歧义、无法落地，先记录并向用户反馈，而不是自行改路线

**重要：你不负责 Git 提交。整体完成后由人工验收、人工提交。**

## 二、环境准备

在开始执行前，检测项目虚拟环境并确定 Python 解释器路径：

1. 检查项目根目录下 `.venv/Scripts/python.exe`（Windows）
2. 检查项目根目录下 `.venv/bin/python`（Unix/macOS）
3. 如果都不存在，报错并提示用户创建虚拟环境（`python -m venv .venv`），不继续执行

检测到后，后续所有 `python` / `pytest` 命令均使用该完整绝对路径。

**Windows 环境命令规则**：
- 必须使用 PowerShell 执行所有包含 `.venv` 路径的命令
- 禁止在 bash 中直接使用 Windows 反斜杠路径

## 三、核心约定

1. CSV 是唯一状态源：只读写这一份 CSV 的状态字段
2. 需求文档 + Plan 是唯一语义源：实现含义、边界、设计路线、测试依据都要从需求文档和 Plan 中获取
3. 一行一更新：每完成一行后立即写回 CSV
4. 以 CSV 文件为单位连续执行：所有行连续完成，中间不停顿，全部完成后统一向用户汇报
5. 跳过已完成：`dev_state=已完成` 且 `test_state=已完成` 的 issue 直接跳过
6. 执行顺序：每条 issue 遵循 读设计 → 读约束 → 写实现 → 写测试 → 跑测试 → 写回状态
7. 不做 Git 操作
8. 状态枚举固定：
   - `dev_state`：`未开始|进行中|已完成`
   - `test_state`：`未开始|进行中|已完成|失败`
9. KISS / YAGNI：不做无关重构，不引入新架构，不擅自偏离需求文档和 Plan 已确认路线
10. 发现设计冲突必须停下来澄清：如果需求文档、Plan、现有代码三者出现冲突，或 issue 信息不足以安全编码，必须记录并向用户反馈

## 四、输入

1. `$ARGUMENTS` 为 issues CSV 路径（必须提供）
2. 这个 CSV 文件是唯一状态源，只读写这一份 CSV
3. 禁止新建其他 CSV 文件
4. CSV 固定表头必须是：

```text
id,priority,title,refs,dev_state,test_state,owner,notes
```

5. 必须自动定位与该 CSV **同 basename** 的 Plan 文件：
   - `.dev/plans/<same-basename>.md`
   - 找不到就报错并停止执行
6. 执行前必须从 Plan frontmatter 中识别 `requirements_path`（若有）；若有则作为一级输入读取

## 五、整体执行流程

### 启动：首次读取 CSV + 定位 Plan / 需求文档 + 输出概览

1. 读取 CSV，校验表头
2. 定位对应 Plan 文件
3. 读取 Plan：
   - `View 1: Review`
   - `View 2: Issue Contract`
4. 如 `requirements_path` 存在，读取需求文档
5. 统计总条数、已完成条数、待执行条数
6. 输出执行计划摘要：

```text
任务概览：
- 总计: X 条
- 已完成（跳过）: X 条
- 待执行: X 条
- Plan: <plan路径>
- Requirements: <需求文档路径或无>

执行顺序：
1. [id] title
2. [id] title
...

开始执行。
```

7. 根据待执行条数判定执行模式，进入执行循环

### 执行模式判定

- **≤10 行 → 轻量模式**：首次读取后按内存顺序执行，不逐行重读 CSV
- **>10 行 → 逐行读取模式**：每完成一行写回 CSV 后，重新读取文件找下一条未完成行

共同约束：每完成一行都必须立即写回 CSV。

### 轻量模式执行循环（≤10 行）

```text
1. 首次读取 CSV，记录所有待执行行
2. for 每条待执行行:
   a. 执行该行（见“单条 issue 的执行步骤”）
   b. 写回 CSV
3. 全部完成 → 进入整体汇报
```

### 逐行读取模式执行循环（>10 行）

```text
loop:
  1. 重新读取 CSV → 找到第一条未完成行
  2. 如果没有未完成行 → 退出循环，进入整体汇报
  3. 执行该行（见“单条 issue 的执行步骤”）
  4. 写回 CSV
  5. 回到 1
```

## 六、单条 issue 的执行步骤

### Step 1: 锁定目标
- 将 `dev_state` 置为 `进行中`
- `test_state` 保持 `未开始`
- 写回 CSV

### Step 2: 深入上下文收集（必须执行，不能跳过）

按以下顺序收集并理解上下文：

1. 在 Plan 的 `View 2: Issue Contract` 中定位当前 `id` 对应条目
2. 读取该 issue 条目的：
   - `summary`
   - `design_refs`
   - `code_refs`
   - `acceptance_criteria`
   - `test_cases`
   - `constraints`
   - `depends_on`
3. 读取需求文档中 `design_refs` 指向的设计段落，理解本条 issue 要遵循的技术路径、时序和逻辑分块
4. 回到 Plan 的 `View 1: Review`，读取与本条 issue 有关的：
   - 设计来源 / 覆盖关系
   - 关键决策
   - 否决方案
   - 执行约束
5. 再读取 `code_refs` 和 CSV 中 `refs` 指向的代码，精确定位关键符号与调用链

**严格要求**：
- 如果需求文档中已经给出了实现路径，执行时必须按该路径落地，不能擅自重设计
- 如果 Plan 对需求文档做了覆盖，必须以 Plan 的覆盖决策为准
- 如果你还没搞懂这条 issue 的设计语义，就不允许开始写实现

### Step 3: 写实现
- 写最小代码满足该 issue 的 `acceptance_criteria`
- 复用项目既有模式，不引入新架构
- 不偏离 `constraints`
- 不得为了图省事跳过需求文档中的关键设计机制

### Step 4: 标记开发完成
- 将 `dev_state` 置为 `已完成`
- 将 `test_state` 置为 `进行中`
- 写回 CSV

### Step 5: 写测试并验证
- 测试文件统一写入 `.dev/test/test_<csv-slug>.py`
- 根据该 issue 的 `test_cases` 编写测试代码
- 覆盖正常路径、边界条件、异常情况
- 运行测试，确认通过

### Step 6: 处理测试结果

- **测试通过**：
  - `test_state` → `已完成`
  - `notes` 追加 `done_at:<日期>`
  - 写回 CSV
  - 继续下一条

- **测试失败，可修复**：
  - 修复实现代码，重新运行测试
  - 通过后按“测试通过”处理

- **测试失败，无法修复**：
  - `test_state` → `失败`
  - `notes` 追加 `test_failed:<原因>`
  - 写回 CSV
  - 跳到下一条继续执行

## 七、阻塞处理

单条 issue 遇到无法自行解决的问题时：
1. `notes` 记录：
   - `blocked:<原因>`
   - 已做排查
   - 与需求文档 / Plan 的冲突点（如有）
   - 建议的下一步
2. `dev_state` 保持 `进行中`
3. 写回 CSV
4. 跳到下一条继续执行，不因单条阻塞而停止整体流程

## 八、完成：整体交接汇报

所有 issue 处理完毕后，输出整体交付报告：

```text
任务执行完毕

完成：X/Y 条
测试失败：Z 条（如有）
阻塞：W 条（如有）

--- 各 issue 摘要 ---

[id-010] title — ✅ 完成
  设计依据: <需求文档锚点 / Plan issue>
  实现: path/to/file.py
  测试: path/to/test_xxx.py（X 个用例，全部通过）

[id-020] title — ❌ 测试失败
  实现: path/to/file2.py
  原因: <失败原因>

[id-030] title — ⏸ 阻塞
  原因: <blocked 原因>
  建议: <下一步>

--- 整体测试 ---

建议验收时运行: $VENV_PYTHON -m pytest .dev/test/test_<csv-slug>.py -v

等待你的验收。验收通过后请自行 git commit。
如需修改某条 issue，请指定 id 和问题。
```

## 九、用户回应后的行为

- 用户说“某条有问题/改一下 XXX-020” → 重新读取该条对应的 Plan issue 条目与需求文档设计，再只重执行该条
- 用户说“Plan 改了” → 必须重新读取最新 Plan，不能沿用旧理解继续执行
- 用户说“重跑” → 重新读取 CSV + Plan + 需求文档，执行所有未完成的行
- 用户说“全部重跑” → 将所有 `dev_state` 和 `test_state` 重置为 `未开始`，从头执行

## 十、进度查看

用户可随时运行脚本查看整体进度：

```bash
$VENV_PYTHON .claude/skills/execute-issues/scripts/check-states.py <csv路径>
```
