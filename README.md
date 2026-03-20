# Plan Kanban

Plan Kanban 是一个围绕**需求澄清 → 方案生成 → 执行合同 → 开发推进 → 验收闭环**构建的同仓工作台项目。

它把需求文档、Plan 合同、Issues CSV、执行过程、阶段文件、Diff、验收结果和前端工作区统一在一个平台中，目标是让需求从澄清到交付形成可追踪、可恢复、可审阅的完整链路。

---

## 项目目标

本项目主要解决以下问题：

- 用 **5 个主阶段** 管理需求生命周期
- 用 **Plan + Issues CSV** 建立可执行合同
- 用 **普通对话 / plan / execute-issues** 区分阶段与过程
- 用 **后端状态模型 + WebSocket / Patch / 恢复能力** 支撑长时执行
- 用 **前端看板 + 工作区** 承载文件、对话和结果协作

---

## 当前技术栈

### 前端

- Vue 3
- Rsbuild
- Ant Design Vue
- Pinia
- Vue Router

### 后端

- FastAPI
- SQLAlchemy
- SQLite
- WebSocket

### 目录契约

```text
frontend/   前端工作台
backend/    FastAPI 应用、REST API、WebSocket、runtime
common/     共享基础设施、配置、ORM 模型、异常定义
.dev/       Plans、Issues CSV、测试文件
scripts/    本地开发脚本
.claude/    skills、执行约束、生成脚本
docs/       需求文档、原型、设计说明
```

---

## 生命周期模型

前台只有 5 个主阶段：

1. `raw`：原始需求澄清
2. `plan`：方案生成
3. `contract`：澄清 & 拆解执行合同
4. `developing`：开发推进
5. `acceptance`：待验收

### 关键原则

- **阶段** 不是 skill 名称
- **过程** 不是页面列
- `plan` 和 `execute-issues` 是阶段转换背后的执行器
- `acceptance_substate` 只表达待验收内部状态，不新增主列

---

## 核心文件契约

### 1. 需求文档

一级设计源，保存：

- 时序
- 逻辑分块
- 模块边界
- 技术路径

### 2. Plan

合同正文，包含两个视图：

- `View 1: Review`
- `View 2: Issue Contract`

### 3. Issues CSV

状态投影，固定表头：

```text
id,priority,title,refs,dev_state,test_state,owner,notes
```

---

## 当前已落地能力

### 后端基础能力

- Card 查询 / 创建 / 更新
- 阶段流转校验与切换
- acceptance 子状态
- process 状态读取与更新
- Kanban 聚合投影

### 普通对话流

- session 创建
- 阶段感知上下文构造
- 普通对话发送
- conversation entries 写入
- session 历史查询

### Plan 合同落盘

- generate-contract precheck
- Plan prompt builder
- Plan 文件写入
- CSV 生成与校验封装
- plan 成功后 card 路径写回与阶段推进
- plan 失败回滚

### execute-issues 过程

- start-development precheck
- execute-issues session 创建
- execute prompt builder
- runtime coordinator
- CSV 状态投影读取
- execute 完成后 acceptance 推进
- execute 停止 / 失败处理

### runtime / execution_process

- Claude executor bootstrap
- Claude protocol adapter
- interrupt 控制能力
- execution manager
- execution_process 持久化
- raw log writer
- log normalizer
- session / execution 绑定

### WebSocket / Patch / 恢复

- event schema
- conversation / process / issues / files / kanban WS
- patch stream batcher
- history recovery service
- 前端 reconnect manager / patch client / patch hook 骨架

### 文件 / Diff / acceptance

- 阶段文件定位
- 文件监听轮询
- worktree create / restore / cleanup / recovery
- changed files / single file diff
- acceptance summary 聚合
- acceptance rollback
- acceptance API

### 前端工作台骨架

- 前端入口与路由
- 看板页面骨架
- header / tabbar / search
- stage columns / stage column / request card / empty state
- workspace shell / context pane / chat pane
- file tabs / file list / file preview
- action bar / result card
- message list / user / assistant / tool / thinking message
- composer panel / meta tags / submit row
- card store / workspace store

---

## 重要路径

### 需求与合同

- 需求文档：`docs/Plan-Kanban-需求与架构设计文档.md`
- Plan：`.dev/plans/2026-03-20_02-10-07-plan-kanban-full-platform.md`
- Issues CSV：`.dev/issues/2026-03-20_02-10-07-plan-kanban-full-platform.csv`
- 统一测试：`.dev/test/test_plan-kanban-full-platform.py`

### 后端入口

- 应用入口：`backend/app/main.py`
- API 汇总：`backend/app/api/__init__.py`
- WS 汇总：`backend/app/ws/__init__.py`

### 前端入口

- 应用入口：`frontend/src/main.ts`
- App 壳层：`frontend/src/App.vue`
- 路由：`frontend/src/router/index.ts`
- 工作台页面：`frontend/src/pages/kanban/WorkbenchPage.vue`

---

## 本地运行

## 1. 准备虚拟环境并安装依赖

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如需进入激活状态，也可以执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 2. 启动后端

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

如果你刚安装完依赖，推荐先运行一次测试确认环境正常：

```powershell
.\.venv\Scripts\python.exe -m pytest .dev/test/test_plan-kanban-full-platform.py -v
```
'}]}♀♀♀assistant to=functions.Edit মন্তব্য ็ตทรู  彩经彩票  天天中彩票中 error  অপেক্ষমাণ 在天天中彩票 code 400: {
---

## 3. 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

---

## 常用命令

### 前端 lint

```bash
cd frontend && pnpm lint
```

### 前端 format

```bash
cd frontend && pnpm format
```

### 统一测试

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pytest .dev/test/test_plan-kanban-full-platform.py -v
```

---

## 当前测试状态

当前主测试文件已覆盖：

- 数据库初始化
- cards / process
- 普通对话流
- Plan / CSV 落盘
- execute-issues 流程
- runtime smoke
- WS / patch / 恢复
- 文件 / Worktree / Diff / acceptance
- 前端骨架文件契约

当前回归结果：

```text
17 passed
```

---

## 设计约束

开发时应始终遵守：

- CSV 是唯一状态源
- 需求文档 + Plan 是唯一语义源
- 不把 skill 名称直接暴露成页面阶段
- 不偏离需求文档与 Plan 的技术路径
- 优先保持 KISS / YAGNI
- 测试统一放在 `.dev/test/`

---

## 后续可继续扩展的方向

虽然当前骨架与主流程已打通，但仍可以继续补齐：

- 更真实的 Claude runtime 对接
- 更完整的 WS 推送与重连策略
- 文件监听从轮询升级到真实 watch
- 前端状态与后端 API/WS 的真实联动
- Diff / acceptance UI 深化
- 更完整的前端组件测试与交互测试

---

## 验收建议

建议验收顺序：

1. 跑统一测试
2. 启动后端与前端
3. 检查 5 阶段看板骨架
4. 检查工作区展开、文件区、对话区
5. 检查 Plan / execute / acceptance 相关 API 行为
6. 检查 `.dev/plans`、`.dev/issues`、`.dev/test` 文件契约

统一验证命令：

```powershell
.\.venv\Scripts\python.exe -m pytest .dev/test/test_plan-kanban-full-platform.py -v
```
