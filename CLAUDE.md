# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 核心约束
所有当前项目中，涉及命令行中调用python的，必须使用当前项目的虚拟环境操作：
传递任务或使用子代理时严格禁止使用 worktree


## 开发规范

### 表设计规范
- 字段必须有 `comment` 参数做说明
- 必须继承自 `common.models.base.BaseModel`（含 created_at、updated_at、is_deleted）
- 禁止外键，在 comment 中说明关联关系
- 索引命名规范：`idx_<字段名>` / `udx_<字段名>`

### API
- 不要用restfulAPI，只用POST方法，通过body传参，不能使用params
- 路径风格不能带变量，严格禁止 `/path/{id}` 的写法
- 统一用pydantic校验请求体

### 代码
- 异步优先，使用统一的异步http客户端（`common.core.http_client`）
- 用 `logger` 不用 `print`
- 密码禁止硬编码