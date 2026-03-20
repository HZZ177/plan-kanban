# CRUD Generator Parameters

## `generate-table`

用于生成完整 CRUD 页面骨架。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | `string` | 是 | 固定为 `generate-table` |
| `pageName` | `string` | 是 | 页面名称 / 目录名称来源 |
| `apiModule` | `string` | 是 | `@/api` 中导出的模块前缀，例如 `Agent`、`Mcp` |
| `apiListMethod` | `string` | 是 | 列表接口方法名 |
| `apiCreateMethod` | `string` | 是 | 创建接口方法名 |
| `apiUpdateMethod` | `string` | 是 | 更新接口方法名 |
| `apiDeleteMethod` | `string` | 是 | 删除接口方法名 |
| `apiDetailMethod` | `string` | 是 | 详情接口方法名 |
| `columns` | `ColumnConfig[]` | 是 | 表格列配置 |
| `searchSchema` | `SearchFieldConfig[]` | 否 | 查询表单配置 |
| `detailSchema` | `DescItem[]` | 是 | 详情组件配置，默认详情抽屉会用到 |
| `currentKey` | `string` | 否 | 分页页码字段，默认 `pageNo` |
| `pageSizeKey` | `string` | 否 | 分页大小字段，默认 `pageSize` |
| `dataSourceKey` | `string` | 否 | 列表字段名，默认 `records` |
| `totalKey` | `string` | 否 | 总数字段名，默认 `total` |
| `recordKey` | `string` | 否 | 记录主键字段名，默认 `id` |
| `route` | `RouteConfig` | 否 | 路由注册信息，仅用于辅助生成说明 |

### 说明

- `detailSchema` 现在和模板一致，主表页会渲染 `DetailForm.vue`。
- 如果你的列表接口返回的是 `items` 或 `list`，请同时传 `dataSourceKey`。
- 如果主键不是 `id`，例如 `task_id`，必须传 `recordKey`。

### 示例

```json
{
  "action": "generate-table",
  "pageName": "ScheduledTaskPage",
  "apiModule": "ScheduledTask",
  "apiListMethod": "scheduledTaskGetTable",
  "apiCreateMethod": "scheduledTaskCreate",
  "apiUpdateMethod": "scheduledTaskUpdate",
  "apiDeleteMethod": "scheduledTaskDelete",
  "apiDetailMethod": "scheduledTaskGetDetail",
  "currentKey": "page",
  "pageSizeKey": "page_size",
  "dataSourceKey": "list",
  "recordKey": "task_id",
  "columns": [],
  "detailSchema": []
}
```

## `generate-form`

用于生成独立表单组件，通常对应 `EditForm.vue`。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `action` | `string` | 是 | 固定为 `generate-form` |
| `formName` | `string` | 是 | 组件名称 |
| `apiModule` | `string` | 是 | `@/api` 中导出的模块前缀 |
| `apiCreateMethod` | `string` | 是 | 创建接口方法名 |
| `apiUpdateMethod` | `string` | 是 | 更新接口方法名 |
| `apiDetailMethod` | `string` | 是 | 详情接口方法名 |
| `fields` | `FormFieldConfig[]` | 是 | 表单字段配置 |
| `recordKey` | `string` | 否 | 详情回填主键字段，默认 `id` |

## 字段配置

### `columns`

常用字段：

- `title`
- `dataIndex`
- `width`
- `align`
- `ellipsis`
- `fixed`

### `searchSchema`

常用字段：

- `field`
- `component`
- `placeholder`
- `componentProps`
- `options`

### `fields`

常用字段：

- `name`
- `label`
- `component`
- `required`
- `tip`
- `placeholder`
- `options`
- `componentProps`

## 类型兼容说明

skill 不再要求调用方必须存在如下命名空间：

```ts
declare namespace XxxGetTableType {}
```

只要 API 方法本身有正确 TypeScript 签名，模板就能推导出请求和响应类型。
