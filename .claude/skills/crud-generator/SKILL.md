---
name: crud-generator
description: 快速生成 Vue 3 CRUD 页面骨架，包含表格页、编辑表单和详情组件模板。
---

# CRUD Generator Skill

## 适用范围

这个 skill 用于当前仓库 `admin_frontend` 的标准 CRUD 页面脚手架生成，目标是：

- 生成基于 `tl` 布局的表格页
- 生成基于 `useForm` + `useDrawer` 的编辑组件
- 生成独立的 `DetailForm.vue` 详情组件
- 尽量复用现有 API 模块，而不是重新约定一套类型体系

## 当前能力

- `generate-table`
  - 生成 `index.vue`
  - 生成 `components/EditForm.vue`
  - 生成 `components/DetailForm.vue`
- `generate-form`
  - 生成独立表单组件

## 关键约束

- 页面仍然遵循单个 `<tl>` 根布局。
- 表格仍然通过 `columns` 驱动，不使用 `<a-table-column>`。
- 详情视图必须使用独立 `DetailForm.vue`，不要把 `EditForm` 强行改成只读。
- 模板优先通过 API 方法签名推导类型，因此同时兼容两类模块：
  - `declare namespace XxxGetTableType`
  - `export interface XxxGetTableReq / XxxDetailRes`
- skill 不再假定路由名、页面名、`Page` 后缀在仓库里绝对统一；这些只作为推荐命名，不作为硬性事实。
- `CommonRes<T>` 在当前仓库等价于 `Promise<{ code; msg; isSuccessful; data: T }>`。不要再把“必须返回 `Promise<CommonRes<T>>`”写成规范。

## 推荐参数

生成表格页时，至少提供：

```json
{
  "action": "generate-table",
  "pageName": "AgentPage",
  "apiModule": "Agent",
  "apiListMethod": "agentGetTable",
  "apiCreateMethod": "agentCreate",
  "apiUpdateMethod": "agentUpdate",
  "apiDeleteMethod": "agentDelete",
  "apiDetailMethod": "agentGetDetail",
  "columns": [],
  "detailSchema": []
}
```

补充建议：

- 当分页字段不是默认值时，显式传入：
  - `currentKey`
  - `pageSizeKey`
  - `dataSourceKey`
  - `totalKey`
- 当表格主键不是 `id` 时，显式传入 `recordKey`

默认值：

- `currentKey`: `pageNo`
- `pageSizeKey`: `pageSize`
- `dataSourceKey`: `records`
- `totalKey`: `total`
- `recordKey`: `id`

## 工作方式

1. 先对照目标 API 模块，确认分页字段、返回列表字段、主键字段。
2. 再生成 `index.vue` / `EditForm.vue` / `DetailForm.vue`。
3. 最后补齐 `data.ts`、路由和必要的 API 类型定义。

## 参考来源

- `admin_frontend/src/pages/table-demo/`
- `admin_frontend/src/pages/agent/`
- `admin_frontend/src/pages/mcp/`

## 注意

- 这个 skill 生成的是高质量骨架，不是零改动即上线的完整业务页。
- 如果目标 API 的删除接口不是“直接接收主键”，生成后需要手动调整删除调用。
- 如果搜索字段、分页字段或返回列表键名不符合默认值，必须在参数里显式给出。
