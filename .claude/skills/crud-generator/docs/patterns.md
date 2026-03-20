# CRUD Generator Patterns

## 页面结构

标准 CRUD 页面保持一个 `<tl>` 根节点，在同一个 `tl-drawer` 中切换：

- `add`
- `edit`
- `detail`

不要为同一页面创建多个 drawer 状态源。

## 类型使用模式

优先从 API 方法签名推导，而不是直接写死类型命名空间：

```ts
type ListReq = Parameters<typeof AgentApi.agentGetTable>[0];
type CreateReq = Parameters<typeof AgentApi.agentCreate>[0];
type DetailRes = Awaited<ReturnType<typeof AgentApi.agentGetDetail>>['data'];
```

这个模式比直接写：

```ts
type ListReq = AgentGetTableType.Req;
```

更适合当前仓库。

## 详情视图模式

详情必须使用独立 `DetailForm.vue`：

- `EditForm.vue` 负责输入与保存
- `DetailForm.vue` 负责只读展示

推荐实现：

```vue
<DetailForm v-if="drawer.mode === 'detail'" />
<EditForm v-if="['edit', 'add'].includes(drawer.mode)" />
```

## 分页键模式

不同模块的分页字段并不统一，常见组合包括：

- `pageNo` + `pageSize`
- `pageNum` + `pageSize`
- `page` + `size`
- `page` + `page_size`

因此生成前应确认：

- 当前页字段名
- 每页条数字段名
- 列表字段名
- 总数字段名

## 删除接口模式

模板默认按“删除接口直接接收主键”处理：

```ts
await AgentApi.agentDelete(row.id);
```

如果真实接口要求对象形式：

```ts
await SomeApi.deleteItem({ id: row.id });
```

则需要在生成后手动调整。
