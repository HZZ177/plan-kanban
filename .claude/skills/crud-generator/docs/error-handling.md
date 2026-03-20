# 错误处理指南

## 错误处理概述

分层架构确保清晰一致的错误处理：

- **全局拦截器**：处理网络错误和 HTTP 状态码异常
- **业务逻辑层**：处理 API 返回的业务错误（`code !== 200`）
- **UI 反馈层**：使用 `message.success/error` 向用户显示提示

## API 请求错误处理

### 删除操作

使用 `Modal.confirm` 包裹，成功时刷新表格：

```typescript
const handleDel = (row: any) => {
  Modal.confirm({
    title: `确定删除？`,
    onOk: async () => {
      const { code } = await AgentApi.demoDel(row.id);
      if (code === 200) {
        message.success('操作成功');
        await search();
      }
    }
  });
};
```

### 保存操作

使用 `try/finally` 确保加载状态清理：

```typescript
const handleSave = async () => {
  try {
    await editForm.value?.save();
    drawer.close();
    search();
  } finally {
    drawer.hideSpinning();  // ⚠️ 必须执行
  }
};
```

### 表单保存方法

验证后调用 API，检查 `code` 并返回适当的 Promise：

```typescript
const save = async () => {
  await validate();
  drawer.showSpinning();
  
  const api = drawer.mode === 'add' ? AgentApi.demoCreate(modelRef) : AgentApi.demoUpdate(modelRef);
  const { code } = await api;
  
  if (code === 200) {
    message.success(drawer.mode === 'add' ? '新增成功' : '修改成功');
    return Promise.resolve();
  }
  return Promise.reject();  // 阻止抽屉关闭
};
```

## 表单验证

`useForm` 根据 `schemas` 中的 `required` 等规则自动显示验证错误：

```typescript
const { validate } = useForm({ schemas, modelRef });
await validate();  // 失败时抛出异常，错误信息自动显示
```

## 加载状态

### 抽屉

```typescript
const { drawer } = useDrawer(PAGE_NAME);
drawer.showSpinning();   // API 调用前
drawer.hideSpinning();   // finally 中必须调用
```

### 表格

`useTable` 自动管理加载状态：

```typescript
const { VBind, search, dataSource } = useTable(getTableData, tableOptions);
```

## 统一错误处理

在 `src/api/index.ts` 配置 Axios 拦截器处理网络错误：

```typescript
axios.interceptors.response.use(
  (response) => response.data,
  (error) => {
    message.error(`请求失败: ${error.message}`);
    return Promise.reject(error);
  }
);
```

组件中只处理业务错误（`code !== 200`），网络错误由全局拦截器处理。

## 常见错误

### ❌ 忘记隐藏加载状态

```typescript
// ❌ 异常时加载状态不消失
const save = async () => {
  drawer.showSpinning();
  const { code } = await api();
  if (code === 200) {
    drawer.hideSpinning();  // 仅成功时隐藏
  }
};
```

### ✅ 正确模式

```typescript
const handleAction = async () => {
  try {
    await validate();
    drawer.showSpinning();
    const { code } = await api();
    if (code === 200) {
      message.success('成功');
      return Promise.resolve();
    }
    return Promise.reject();
  } finally {
    drawer.hideSpinning();  // 确保执行
  }
};
```

## 关键原则

- 全局拦截器处理网络错误，业务代码只处理 `code !== 200`
- `hideSpinning()` 必须放在 `finally` 中
- 业务错误返回 `Promise.reject()` 阻止抽屉关闭
- 表单验证由 `useForm` 自动处理
