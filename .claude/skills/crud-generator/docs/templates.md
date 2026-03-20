# CRUD Generator Templates

## 生成文件

`generate-table` 默认生成：

```text
src/pages/[pageName]/
  index.vue
  data.ts
  components/
    EditForm.vue
    DetailForm.vue
```

`generate-form` 默认生成：

```text
src/pages/[pageName]/components/
  [FormName].vue
```

## 模板职责

### `table-crud-template.vue`

负责主表页：

- 搜索表单
- 表格渲染
- 抽屉状态管理
- 编辑与详情组件切换
- 删除动作和基础刷新

### `form-template.vue`

负责编辑表单：

- 根据 `fields` 生成 `schemas`
- 在编辑模式下拉取详情并回填
- 在新增 / 编辑模式调用不同 API

### `detail-form-template.vue`

负责详情页：

- 调用详情接口
- 使用 `detailSchema` + `yc-description` 渲染只读视图

## 类型策略

模板默认通过 API 函数签名推导类型，例如：

```ts
type ListReq = Parameters<typeof AgentApi.agentGetTable>[0];
type DetailRes = Awaited<ReturnType<typeof AgentApi.agentGetDetail>>['data'];
```

这样做的原因：

- 兼容 namespace 类型风格
- 兼容直接导出 interface/type 风格
- 降低对单一命名规范的耦合

## 可配置占位符

除基础方法名外，模板还支持这些关键占位符：

- `{{currentKey}}`
- `{{pageSizeKey}}`
- `{{dataSourceKey}}`
- `{{totalKey}}`
- `{{recordKey}}`

建议在以下情况显式提供：

- 分页字段不是 `pageNo/pageSize`
- 列表字段不是 `records`
- 主键字段不是 `id`

## 手工补充项

模板生成后通常还需要人工补齐：

- `data.ts` 中的 `columns`、`searchSchema`、`detailSchema`
- 远程下拉选项加载逻辑
- 路由注册
- 删除接口参数如果不是直接主键，需要手动调整
