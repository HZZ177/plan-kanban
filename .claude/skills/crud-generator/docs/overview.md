# CRUD Generator Overview

## 定位

`crud-generator` 是当前仓库前端 CRUD 页面骨架生成 skill。它的职责是统一页面结构和常见交互，不是替代业务建模。

生成目标：

- `index.vue` 表格页
- `components/EditForm.vue` 编辑表单
- `components/DetailForm.vue` 详情视图

## 设计原则

- 对齐仓库现有模式：`tl`、`useTable`、`useForm`、`useDrawer`
- 以真实 API 模块为中心，不再额外发明一套必须遵守的旧命名空间规则
- 优先通过 API 方法签名推导类型，兼容 namespace 风格和 direct-export 风格
- 详情页必须独立组件，避免文档和模板互相打架

## 仓库事实

当前仓库并不存在完全统一的一套 API 类型风格，至少同时存在：

1. `declare namespace AgentGetTableType`
2. `export interface McpGetTableReq`

因此生成模板不应把 `{{apiModule}}GetTableType.*` 作为唯一真相。现在的模板通过如下方式适配：

```ts
type ListReq = Parameters<typeof AgentApi.agentGetTable>[0];
type DetailRes = Awaited<ReturnType<typeof AgentApi.agentGetDetail>>['data'];
```

这使模板对 API 风格更稳健。

## 什么时候适合用

- 新建标准后台 CRUD 页
- 在已有 API 基础上快速搭骨架
- 需要统一搜索、分页、抽屉编辑、详情查看的实现方式

## 什么时候不适合直接用

- 表格行为很复杂，例如树表格、行内编辑、拖拽排序
- 表单包含高度动态的联动逻辑
- 删除、详情或分页接口签名明显异于普通 CRUD

这类情况仍然可以生成基础结构，但需要手工调整。

## 推荐流程

1. 先确认 API 模块导出的方法名。
2. 确认分页字段、列表字段、主键字段。
3. 使用 skill 生成页面骨架。
4. 回填 `data.ts`、远程选项、路由和业务逻辑。
