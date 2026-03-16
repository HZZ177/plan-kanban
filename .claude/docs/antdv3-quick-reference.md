# Ant Design Vue 3.x 常用组件 API 快速参考

> **版本**: 3.2.20  
> **官方文档**: https://3x.antdv.com/components/overview-cn/  
> **重要**: 本项目使用 3.x 版本，与 4.x 有 API 差异，请勿参考 4.x 文档

---

## Table 表格

### 基础用法

```vue
<a-table
  :columns="columns"
  :data-source="dataSource"
  :pagination="pagination"
  :loading="loading"
  @change="handleTableChange"
>
  <template #bodyCell="{ column, record, text, index }">
    <!-- 自定义单元格 -->
  </template>
</a-table>
```

### columns 配置

```typescript
const columns = [
  {
    title: '姓名',           // 列标题
    dataIndex: 'name',       // 数据字段名
    key: 'name',             // Vue 需要的 key（dataIndex 相同时可省略）
    width: 100,              // 列宽
    align: 'left',           // 对齐方式: left | center | right
    ellipsis: true,          // 超长自动省略
    fixed: 'left',           // 固定列: left | right
    sorter: true,            // 启用排序
    filters: [],             // 筛选选项
    customRender: ({ text, record, index }) => text, // 自定义渲染
  },
];
```

### pagination 配置

```typescript
const pagination = reactive({
  current: 1,              // 当前页
  pageSize: 10,            // 每页条数
  total: 0,                // 总条数
  showSizeChanger: true,   // 显示页大小选择器
  showQuickJumper: true,   // 显示快速跳转
  showTotal: (total) => `共 ${total} 条`,
});
```

### 常用事件

| 事件 | 参数 | 说明 |
|------|------|------|
| change | (pagination, filters, sorter, { currentDataSource }) | 分页、排序、筛选变化 |
| resizeColumn | (w, col) | 列宽调整 |

---

## Form 表单

### 基础用法

```vue
<a-form
  ref="formRef"
  :model="formState"
  :rules="rules"
  :label-col="{ span: 4 }"
  :wrapper-col="{ span: 20 }"
>
  <a-form-item label="姓名" name="name">
    <a-input v-model:value="formState.name" />
  </a-form-item>
</a-form>
```

### 表单验证

```typescript
const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 10, message: '长度在 2 到 10 个字符', trigger: 'blur' },
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
};

// 手动验证
const formRef = ref();
const onSubmit = async () => {
  try {
    await formRef.value.validate();
    // 验证通过
  } catch (error) {
    // 验证失败
  }
};

// 重置表单
formRef.value.resetFields();
```

### Form.Item 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| name | string | 字段名，用于验证 |
| label | string | 标签文本 |
| rules | Rule[] | 验证规则 |
| required | boolean | 是否必填（自动添加样式） |
| help | string | 提示信息 |
| validateStatus | string | 校验状态: success | warning | error | validating |

---

## Input 输入框

```vue
<!-- 基础输入框 -->
<a-input v-model:value="value" placeholder="请输入" />

<!-- 带前后缀 -->
<a-input v-model:value="value">
  <template #prefix>
    <UserOutlined />
  </template>
  <template #suffix>
    <Tooltip title="提示信息">
      <InfoCircleOutlined />
    </Tooltip>
  </template>
</a-input>

<!-- 密码输入框 -->
<a-input-password v-model:value="password" />

<!-- 文本域 -->
<a-textarea v-model:value="value" :rows="4" :maxlength="200" show-count />

<!-- 搜索框 -->
<a-input-search v-model:value="value" placeholder="搜索" @search="onSearch" />
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| value | string | - | 输入值（v-model:value） |
| placeholder | string | - | 占位符 |
| disabled | boolean | false | 禁用 |
| maxlength | number | - | 最大长度 |
| allowClear | boolean | false | 允许清除 |
| prefix | slot | - | 前缀图标 |
| suffix | slot | - | 后缀图标 |

---

## Select 选择器

```vue
<a-select
  v-model:value="selected"
  :options="options"
  placeholder="请选择"
  allow-clear
  show-search
/>
```

### options 格式

```typescript
const options = [
  { label: '选项1', value: '1' },
  { label: '选项2', value: '2', disabled: true },
];

// 或使用 fieldNames 映射
const options = [
  { name: '选项1', id: '1' },
];
// <a-select :options="options" :field-names="{ label: 'name', value: 'id' }" />
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| value | string\|string[] | - | 选中值 |
| options | Option[] | [] | 选项数据 |
| mode | string | - | 模式: multiple \| tags |
| allowClear | boolean | false | 允许清除 |
| showSearch | boolean | false | 可搜索 |
| filterOption | boolean\|Function | true | 筛选选项 |
| fieldNames | object | - | 字段映射 |
| maxTagCount | number\|'responsive' | - | 最多显示标签数 |

### 多选模式

```vue
<a-select
  v-model:value="selected"
  mode="multiple"
  :options="options"
  :max-tag-count="3"
  :max-tag-text-length="10"
/>
```

---

## Button 按钮

```vue
<a-button type="primary">主要按钮</a-button>
<a-button>默认按钮</a-button>
<a-button type="dashed">虚线按钮</a-button>
<a-button type="text">文本按钮</a-button>
<a-button type="link">链接按钮</a-button>
<a-button danger>危险按钮</a-button>
<a-button type="primary" danger>危险主要按钮</a-button>
<a-button type="link" danger>危险链接按钮</a-button>
<a-button loading>加载中</a-button>
<a-button disabled>禁用</a-button>
<a-button ghost>幽灵按钮</a-button>
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| type | string | default | 类型: primary \| dashed \| text \| link |
| danger | boolean | false | 危险样式 |
| ghost | boolean | false | 幽灵样式（背景透明） |
| loading | boolean | false | 加载状态 |
| disabled | boolean | false | 禁用 |
| icon | VNode | - | 图标 |
| href | string | - | 链接地址（type=link 时） |

---

## Modal 对话框

### 基础用法

```vue
<a-modal
  v-model:open="visible"
  title="标题"
  @ok="handleOk"
  @cancel="handleCancel"
>
  <p>内容</p>
</a-modal>
```

### 确认对话框

```typescript
import { Modal } from 'ant-design-vue';

Modal.confirm({
  title: '确认删除',
  content: '删除后不可恢复，确定要删除吗？',
  okText: '确定',
  cancelText: '取消',
  okType: 'danger',
  onOk: async () => {
    // 确认操作
  },
  onCancel: () => {
    // 取消操作
  },
});

Modal.info({ title: '信息', content: '这是一条信息' });
Modal.success({ title: '成功', content: '操作成功' });
Modal.error({ title: '错误', content: '操作失败' });
Modal.warning({ title: '警告', content: '请注意' });
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| open | boolean | false | 是否显示 |
| title | string\|slot | - | 标题 |
| width | string\|number | 520 | 宽度 |
| centered | boolean | false | 垂直居中 |
| closable | boolean | true | 显示关闭按钮 |
| maskClosable | boolean | true | 点击遮罩关闭 |
| okText | string | 确定 | 确认按钮文字 |
| cancelText | string | 取消 | 取消按钮文字 |
| confirmLoading | boolean | false | 确认按钮加载状态 |

---

## Drawer 抽屉

```vue
<a-drawer
  v-model:open="visible"
  title="标题"
  placement="right"
  :width="500"
  @close="handleClose"
>
  <p>内容</p>
  
  <template #footer>
    <a-button @click="visible = false">取消</a-button>
    <a-button type="primary" @click="handleOk">确定</a-button>
  </template>
</a-drawer>
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| open | boolean | false | 是否显示 |
| title | string\|slot | - | 标题 |
| placement | string | right | 位置: top \| right \| bottom \| left |
| width | string\|number | 256 | 宽度（左右抽屉） |
| height | string\|number | 256 | 高度（上下抽屉） |
| closable | boolean | true | 显示关闭按钮 |
| maskClosable | boolean | true | 点击遮罩关闭 |
| destroyOnClose | boolean | false | 关闭时销毁子元素 |

---

## Message 全局提示

```typescript
import { message } from 'ant-design-vue';

message.success('操作成功');
message.error('操作失败');
message.warning('警告信息');
message.info('提示信息');
message.loading('加载中...');

// 带持续时间
message.success('操作成功', 5); // 5秒后关闭

// 手动关闭
const hide = message.loading('加载中...');
hide(); // 手动关闭
```

### 配置

```typescript
message.config({
  top: '100px',
  duration: 3,
  maxCount: 3,
});
```

---

## Notification 通知提醒框

```typescript
import { notification } from 'ant-design-vue';

notification.success({
  message: '操作成功',
  description: '这是一条成功通知',
  duration: 4.5,
  placement: 'topRight', // topLeft | topRight | bottomLeft | bottomRight
});

notification.error({
  message: '操作失败',
  description: '这是一条错误通知',
});
```

---

## DatePicker 日期选择器

```vue
<!-- 日期选择 -->
<a-date-picker v-model:value="date" format="YYYY-MM-DD" />

<!-- 日期时间选择 -->
<a-date-picker v-model:value="datetime" show-time format="YYYY-MM-DD HH:mm:ss" />

<!-- 日期范围选择 -->
<a-range-picker v-model:value="dateRange" format="YYYY-MM-DD" />

<!-- 周选择 -->
<a-week-picker v-model:value="week" />

<!-- 月选择 -->
<a-month-picker v-model:value="month" />
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| value | Dayjs | - | 选中值 |
| format | string | YYYY-MM-DD | 日期格式 |
| showTime | boolean\|object | false | 显示时间选择 |
| disabledDate | Function | - | 禁用日期 |
| disabled | boolean | false | 禁用 |
| allowClear | boolean | true | 允许清除 |
| placeholder | string | - | 占位符 |

### 禁用日期示例

```typescript
import dayjs from 'dayjs';

const disabledDate = (current: Dayjs) => {
  // 禁用今天之前的日期
  return current && current < dayjs().startOf('day');
};
```

---

## Upload 上传

```vue
<a-upload
  v-model:file-list="fileList"
  :action="uploadUrl"
  :headers="headers"
  @change="handleChange"
  @preview="handlePreview"
>
  <a-button>
    <UploadOutlined /> 点击上传
  </a-button>
</a-upload>
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| fileList | object[] | [] | 文件列表 |
| action | string | - | 上传地址 |
| headers | object | - | 请求头 |
| multiple | boolean | false | 多选 |
| accept | string | - | 接受的文件类型 |
| disabled | boolean | false | 禁用 |
| listType | string | text | 列表样式: text \| picture \| picture-card |
| beforeUpload | Function | - | 上传前钩子，返回 false 阻止上传 |
| customRequest | Function | - | 自定义上传实现 |

### 手动上传

```typescript
const beforeUpload = (file) => {
  // 返回 false 阻止自动上传
  return false;
};

// 手动触发上传
const handleUpload = () => {
  const formData = new FormData();
  fileList.value.forEach(file => {
    formData.append('files[]', file);
  });
  // 发送请求...
};
```

---

## Tabs 标签页

```vue
<a-tabs v-model:activeKey="activeKey">
  <a-tab-pane key="1" tab="标签1">
    内容1
  </a-tab-pane>
  <a-tab-pane key="2" tab="标签2">
    内容2
  </a-tab-pane>
  <a-tab-pane key="3" tab="标签3" disabled>
    内容3
  </a-tab-pane>
</a-tabs>
```

### 常用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| activeKey | string | - | 当前激活的 tab |
| type | string | line | 页签类型: line \| card \| editable-card |
| tabPosition | string | top | 页签位置: top \| right \| bottom \| left |
| size | string | default | 大小: default \| small |

---

## Tooltip 文字提示

```vue
<a-tooltip title="提示文字">
  <a-button>悬停显示</a-button>
</a-tooltip>

<a-tooltip>
  <template #title>
    <span>多行提示<br />第二行</span>
  </template>
  <a-button>自定义内容</a-button>
</a-tooltip>
```

---

## Popconfirm 气泡确认框

```vue
<a-popconfirm
  title="确定要删除吗？"
  ok-text="确定"
  cancel-text="取消"
  @confirm="handleDelete"
>
  <a-button danger>删除</a-button>
</a-popconfirm>
```

---

## Spin 加载中

```vue
<!-- 容器内加载 -->
<a-spin :spinning="loading">
  <div>内容区域</div>
</a-spin>

<!-- 独立加载指示器 -->
<a-spin />

<!-- 自定义描述 -->
<a-spin tip="加载中...">
  <div>内容区域</div>
</a-spin>

<!-- 自定义指示器 -->
<a-spin :indicator="indicator" />
```

---

## 常见问题

### 1. v-model 用法

Ant Design Vue 3.x 使用 `v-model:value` 而非 `v-model`：

```vue
<!-- 正确 -->
<a-input v-model:value="text" />
<a-select v-model:value="selected" />

<!-- 错误（Vue 3 会警告） -->
<a-input v-model="text" />
```

### 2. 图标使用

```typescript
// 按需导入
import { UserOutlined, SettingOutlined } from '@ant-design/icons-vue';

// 在模板中使用
<UserOutlined />
<SettingOutlined />
```

### 3. 表格自定义单元格

```vue
<a-table :columns="columns" :data-source="data">
  <template #bodyCell="{ column, record, text }">
    <template v-if="column.dataIndex === 'action'">
      <a-button type="link" @click="handleEdit(record)">编辑</a-button>
    </template>
    <template v-if="column.dataIndex === 'status'">
      <a-tag :color="text === 1 ? 'green' : 'red'">
        {{ text === 1 ? '启用' : '禁用' }}
      </a-tag>
    </template>
  </template>
</a-table>
```

### 4. 表单动态校验

```typescript
// 动态修改校验规则
const updateRules = () => {
  rules.password = [
    { required: isRegister.value, message: '请输入密码' },
  ];
};

// 清除校验结果
formRef.value?.clearValidate();
formRef.value?.clearValidate(['name']); // 清除指定字段
```

### 5. Select 远程搜索

```vue
<a-select
  v-model:value="value"
  show-search
  :filter-option="false"
  :not-found-content="fetching ? undefined : null"
  @search="handleSearch"
>
  <template v-if="fetching" #notFoundContent>
    <a-spin size="small" />
  </template>
  <a-select-option v-for="item in options" :key="item.value" :value="item.value">
    {{ item.label }}
  </a-select-option>
</a-select>
```

---

## 版本差异提醒

### Ant Design Vue 3.x vs 4.x 主要差异

| 特性 | 3.x | 4.x |
|------|-----|-----|
| 弹窗显示属性 | `v-model:visible` | `v-model:open` |
| 表单字段前缀 | `v-decorator` | `name` 属性 |
| 图标导入 | `@ant-design/icons-vue` | 内置图标组件 |
| 日期组件 | Moment.js | Day.js |
| 全局配置 | `ConfigProvider` | `ConfigProvider` (API 有变化) |

> **本项目使用 3.x，请勿使用 4.x 的 API！**
