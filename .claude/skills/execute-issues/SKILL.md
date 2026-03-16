---
name: "execute-issues"
description: "基于 Issues CSV 执行整个任务：连续完成所有 issue，整体交付后由人工验收"
invocation: "manual"
argument-hint: "<issues CSV 文件路径>"
---

你现在处于「Issues CSV 执行模式」。

目标：以 `.dev/issues/*.csv` 为任务边界与状态源，**连续完成所有 issue**，最后整体交付给用户验收。

**核心原则：CSV 文件是唯一状态源。执行策略根据任务规模自动选择（见「执行模式」），但无论哪种模式，每完成一行都必须立即写回 CSV。**

**重要：你不负责 Git 提交。整体完成后由人工验收、人工提交。**

## 零、环境准备

在开始执行前，检测项目虚拟环境并确定 Python 解释器路径：

1. 检查项目根目录下 `.venv/Scripts/python.exe`（Windows）
2. 检查项目根目录下 `.venv/bin/python`（Unix/macOS）
3. 如果都不存在，**报错并提示用户创建虚拟环境**（`python -m venv .venv`），不继续执行

检测到后，后续所有 `python` / `pytest` 命令均使用该完整绝对路径。

**⚠️ Windows 环境下的命令执行规则**：
- **必须使用 PowerShell** 执行所有包含 `.venv` 路径的命令
- 命令格式：`powershell -Command "cd '<项目根目录>'; & '<项目根目录>\.venv\Scripts\python.exe' -m pytest ... 2>&1"`
- **禁止**在 bash 中直接使用 Windows 反斜杠路径（如 `.venv\Scripts\python.exe`），这会导致路径解析失败
- 示例：
  ```
  # ✅ 正确（PowerShell）
  powershell -Command "cd 'D:\Project'; & '.venv\Scripts\python.exe' -m pytest '.dev\test\test_xxx.py' -v 2>&1"

  # ❌ 错误（bash 中直接用反斜杠路径）
  cd D:\Project && .venv\Scripts\python.exe -m pytest .dev/test/test_xxx.py -v
  ```

## 一、核心约定

1. **CSV 是唯一状态源**：只做 CSV 中描述的工作。需求变更先写回 CSV 再改代码。
2. **一行一更新**：每完成一行后立即写回 CSV，确保状态实时持久化。
3. **执行模式按规模自动选择**（见「执行模式判定」）：
   - **轻量模式**（≤10 行）：首次读取后按顺序执行，不逐行重读文件
   - **逐行读取模式**（>10 行）：每处理一行前重新读取 CSV 文件，防止上下文漂移
4. **以 CSV 文件为单位连续执行**：所有行连续完成，中间不停顿，全部完成后统一向用户汇报。
5. **跳过已完成**：`dev_state=已完成` 且 `test_state=已完成` 的 issue 直接跳过，支持中断后重跑。
6. **执行顺序**：每条 issue 遵循 写实现 → 写测试 → 运行测试确认通过。
7. **不做 Git 操作**：不执行 `git add`、`git commit`、`git push`。
8. **状态枚举驱动**，禁止百分比：
   - `dev_state`：`未开始|进行中|已完成`
   - `test_state`：`未开始|进行中|已完成|失败`
9. **KISS / YAGNI**：不做无关重构，不引入新架构，保持向后兼容。

## 二、输入

1. `$ARGUMENTS` 为 issues CSV 路径（必须提供）
2. 这个 CSV 文件是**唯一状态源**，只读写这一份 CSV
3. **禁止新建**其他 CSV 文件

## 三、整体执行流程

### 启动：首次读取 CSV + 输出概览

1. 读取 CSV，校验表头
2. 统计总条数、已完成条数、待执行条数
3. 输出执行计划摘要：

```
任务概览：
- 总计: X 条
- 已完成（跳过）: X 条
- 待执行: X 条

执行顺序：
1. [id] title
2. [id] title
...

开始执行。
```

4. 根据待执行条数判定执行模式，进入执行循环

### 执行模式判定

首次读取 CSV 后，根据**总行数**（非待执行数）自动选择模式：

- **≤10 行 → 轻量模式**：首次读取后按内存中的顺序依次执行，不逐行重读文件。短任务不会遇到上下文压缩或漂移问题，省去重复读取的开销。
- **>10 行 → 逐行读取模式**：每完成一行写回 CSV 后，重新读取文件找下一条未完成行。长任务需要防止上下文积累导致的漂移，且支持人工中途修改 CSV。

**两种模式的共同约束**：每完成一行都必须立即写回 CSV（一行一更新）。

### 轻量模式执行循环（≤10 行）

```
1. 首次读取 CSV，按顺序记录所有待执行行
2. for 每条待执行行:
   a. 执行该行（见「单条 issue 的执行步骤」）
   b. 写回 CSV
3. 全部完成 → 进入整体汇报
```

### 逐行读取模式执行循环（>10 行）

```
loop:
  1. 读取 CSV 文件 → 找到第一条「未完成」的行（dev_state != 已完成 或 test_state 不为 已完成）
  2. 如果没有未完成的行 → 退出循环，进入整体汇报
  3. 执行该行（见「单条 issue 的执行步骤」）
  4. 写回 CSV
  5. 回到 1
```

**逐行读取的意义**：每次循环都从文件重新读取，不依赖内存中的上一轮状态。这确保：
- CSV 始终是唯一标准
- 中断后重跑能正确恢复
- 人工修改 CSV 后下一轮能感知到

### 单条 issue 的执行步骤

对每条待执行的 issue，按以下步骤完成：

**Step 1: 锁定目标**
- 将 `dev_state` 置为 `进行中`，`test_state` 保持 `未开始`
- 写回 CSV

**Step 2: 上下文收集**
- 从 `refs` 指向的文件开始读（仅该行第一次执行时需要读取参考文件，后续行可利用上下文中已有的信息）
- 精确定位关键符号与调用链

**Step 3: 写实现**
- 写最小的代码满足 `acceptance_criteria`
- 复用项目既有模式，不引入新架构

**Step 4: 标记开发完成**
- 将 `dev_state` 置为 `已完成`，`test_state` 置为 `进行中`
- 写回 CSV

**Step 5: 写测试并验证**
- 测试文件统一写入 `.dev/test/test_<csv-slug>.py`，其中 `<csv-slug>` 取 CSV 文件名去掉 `.csv` 后缀
- 根据 `test_cases` 字段编写测试代码
- 覆盖：正常路径、边界条件、异常情况
- **运行测试，确认通过**

**Step 6: 处理测试结果**

- **测试通过**：
  - `test_state` → `已完成`
  - `notes` 追加 `done_at:<日期>`
  - 写回 CSV
  - **继续下一条**

- **测试失败，可修复**：
  - 修复实现代码，重新运行测试
  - 通过后按「测试通过」处理

- **测试失败，无法修复**：
  - `test_state` → `失败`
  - `notes` 追加 `test_failed:<原因>`
  - 写回 CSV
  - **跳到下一条继续执行**

### 阻塞处理（不停止整体流程）

单条 issue 遇到无法自行解决的问题时：
1. `notes` 记录 `blocked:<原因>` + 已做排查 + 建议
2. `dev_state` 保持 `进行中`
3. 写回 CSV
4. **跳到下一条继续执行**，不因单条阻塞而停止整体流程

### 完成：整体交接汇报

所有 issue 处理完毕后，输出整体交付报告：

```
任务执行完毕

完成：X/Y 条
测试失败：Z 条（如有）
阻塞：W 条（如有）

--- 各 issue 摘要 ---

[id-010] title — ✅ 完成
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

## 四、用户回应后的行为

- 用户说「某条有问题/改一下 XXX-020」→ 只重新执行该条（走完整循环），更新 CSV
- 用户说「测试用例不够」→ 更新 CSV 的 `test_cases`，重新执行对应 issue
- 用户说「重跑」→ 重新读取 CSV，执行所有未完成的行（支持中断恢复）
- 用户说「全部重跑」→ 将所有 `dev_state` 和 `test_state` 重置为 `未开始`，从头执行

## 五、进度查看

用户可随时运行脚本查看整体进度：

```bash
$VENV_PYTHON .claude/skills/execute-issues/scripts/check-states.py <csv路径>
```
