# CRUD Generator Examples

This document provides complete working examples of CRUD Generator usage based on the real `table-demo` implementation.

## Example 1: Generate Table Page

This example shows how to generate a complete table page with search, CRUD operations, and drawer management.

### Configuration

```json
{
  "pageName": "UserPage",
  "apiModule": "user",
  "apiGetTableMethod": "getUserList",
  "apiGetDetailMethod": "getUserDetail",
  "apiUpdateMethod": "saveUser",
  "apiDeleteMethod": "deleteUser",
  "columns": [
    { "title": "姓名", "dataIndex": "userName", "width": 100, "align": "left", "ellipsis": true },
    { "title": "手机号", "dataIndex": "phone", "width": 100, "align": "left", "ellipsis": true },
    { "title": "金额", "dataIndex": "amount", "width": 100, "align": "right", "ellipsis": true },
    { "title": "状态", "dataIndex": "status", "width": 110, "align": "left", "ellipsis": true },
    { "title": "操作", "dataIndex": "action", "width": 120, "fixed": "right" }
  ],
  "route": "/user",
  "searchSchema": [
    { "field": "userName", "component": "Input", "componentProps": { "placeholder": "姓名" } },
    { "field": "status", "component": "Select", "componentProps": { "options": [] } }
  ]
}
```

### Generated File Structure

```
src/pages/user/
├── index.vue              # Main table page component
├── data.ts                # Column config, enums, search schema
└── components/
    └── EditForm.vue       # Form for add/edit operations
```

### Key Generated Files

#### `index.vue` (Main Table Page)

```vue
<script setup lang="ts">
import { columns, PAGE_NAME, searchSchema, statusOptions } from './data';
import EditForm from './components/EditForm.vue';
import DetailForm from './components/DetailForm.vue';
import type { UseTableOptions } from '@kt/unity-hooks/src/useTable/types';
import { useTable } from '@kt/unity-hooks';
import { UserApi } from '@/api';
import { getLabelByValue } from '@/utils';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

defineOptions({ name: PAGE_NAME });

// 搜索表单参数
const inParams = reactive<UserGetTableType.InParams>({
  userName: '',
  status: '',
  startTime: '',
  endTime: '',
});
const { VBind: searchVBind, resetFields: reset } = useForm({
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
  onEnter: () => search(),
});

// 表格配置
const tableOptions = reactive<UseTableOptions>({
  currentKey: 'pageNo',
  pageSizeKey: 'pageSize',
  dataSourceKey: 'records',
  totalKey: 'total',
  immediate: false,
  columns,
  inParams,
});

// 获取表格数据
const getTableData = async (params: UserGetTableType.Req) => {
  const { data } = await UserApi.getUserList(params);
  return data;
};

const { VBind, VOn, search, run, pagination, dataSource } = useTable(
  getTableData,
  tableOptions,
);

// 删除操作
const handleDel = (row: any) => {
  Modal.confirm({
    title: `确定删除？`,
    onOk: async () => {
      const { code } = await UserApi.deleteUser(row.id);
      if (code === 200) {
        message.success('操作成功');
        await search();
      }
    },
    cancelText: '取消',
  });
};

// 抽屉管理
const { drawer } = useDrawer(PAGE_NAME);
const editForm = ref();
const handleSave = async () => {
  try {
    await editForm.value?.save();
    drawer.close();
    search();
  } finally {
    drawer.hideSpinning();
  }
};

// 页面初始化
const init = async () => {
  await search();
};
init();
</script>

<template>
  <tl v-model:drawer="drawer.visible">
    <tl-main>
      <tl-filter>
        <yc-form v-bind="searchVBind" />
        <a-button type="primary" @click="search">查询</a-button>
        <a-button @click="reset">重置</a-button>
        <a-button type="primary" @click="drawer.open('add', '新增')">
          新增
        </a-button>
      </tl-filter>

      <tl-table :visibleColumns="[0, 1, 2]">
        <a-table v-on="VOn" v-bind="VBind">
           <template #bodyCell="{ column: { dataIndex }, record, text }">
             <!-- 状态列自定义渲染 -->
             <template v-if="dataIndex === 'status'">
               <a-tag :color="getLabelByValue(record.status, statusOptions, 'color')">
                 {{ getLabelByValue(record.status, statusOptions) }}
               </a-tag>
             </template>
             <!-- 操作列 -->
            <template v-if="dataIndex === 'action'">
              <action-group>
                <a-button
                  type="link"
                  @click="drawer.open('detail', '详情', record)"
                >
                  详情
                </a-button>
                <a-button
                  type="link"
                  @click="drawer.open('edit', '编辑', record)"
                >
                  编辑
                </a-button>
                <a-button type="link" danger @click="handleDel(record)">
                  删除
                </a-button>
              </action-group>
            </template>
          </template>
        </a-table>
      </tl-table>
    </tl-main>

    <tl-drawer
      :title="drawer.title"
      :spin="{ spinning: drawer.spinning }"
      buttonsPosition="fixed"
    >
      <template #buttons>
        <a-button
          type="primary"
          @click="handleSave"
          v-if="['edit', 'add'].includes(drawer.mode)"
        >
          保存
        </a-button>
        <a-button @click="drawer.close">返回</a-button>
      </template>

      <!-- 详情模式 -->
      <detail-form v-if="drawer.mode === 'detail'" />

      <!-- 编辑/新增模式 -->
      <edit-form ref="editForm" v-if="['edit', 'add'].includes(drawer.mode)" />
    </tl-drawer>
  </tl>
</template>
```

#### `data.ts` (Configuration)

```typescript
/**
 * 页面名称，必须与路由名称一致且全局唯一
 */
export const PAGE_NAME = 'UserPage';

/** 表格列配置 */
export const columns = [
  {
    title: '姓名',
    dataIndex: 'userName',
    width: 100,
    align: 'left',
    ellipsis: true,
  },
  {
    title: '手机号',
    dataIndex: 'phone',
    width: 100,
    align: 'left',
    ellipsis: true,
  },
  {
    title: '金额',
    dataIndex: 'amount',
    width: 100,
    align: 'right',
    ellipsis: true,
  },
  {
    title: '状态',
    dataIndex: 'status',
    width: 110,
    align: 'left',
    ellipsis: true,
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: 120,
    fixed: 'right',
  },
];

/** 状态枚举 */
export enum statusEnum {
  INITIALIZATION = 0,
  PENDING_START = 1,
  OPERATING = 2,
  ENDED = 3,
}

export const statusOptions = [
  { label: '初始化', value: statusEnum.INITIALIZATION, color: 'default' },
  { label: '待开始', value: statusEnum.PENDING_START, color: 'warning' },
  { label: '运营中', value: statusEnum.OPERATING, color: 'success' },
  { label: '已结束', value: statusEnum.ENDED, color: 'error' },
];

/** 搜索表单配置 */
export const searchSchema: YcForm.Schema[] = [
  {
    field: 'userName',
    component: 'Input',
    componentProps: {
      placeholder: '姓名',
    },
  },
  {
    field: 'status',
    component: 'Select',
    componentProps: {
      options: [{ label: '状态：全部', value: '' }, ...statusOptions],
    },
  },
];
```

#### `components/EditForm.vue` (Form Component)

```vue
<script setup lang="ts">
import { UserApi } from '@/api';
import { PAGE_NAME } from '../data';
import useDrawer from '@/hooks/useDrawer.ts';
import { useForm } from '@/hooks/useForm.ts';

const { drawer } = useDrawer(PAGE_NAME);

// 远程选项数据
const projectList = ref<Array<{ id: number; name: string }>>([]);
const getProjectList = async () => {
  projectList.value = await UserApi.getProjectList();
};

// 表单模型
const modelRef = reactive<Partial<UserEditType.Req>>({ annex: [] });

// 表单字段配置
const schemas = computed<YcForm.Schema[]>(() => [
  {
    label: '姓名',
    field: 'userName',
    component: 'Input',
    required: true,
    tip: '可以设置提示信息',
    componentProps: {
      maxlength: 10,
    },
  },
  {
    label: '项目',
    component: 'Select',
    field: 'projectId',
    required: true,
    componentProps: {
      options: projectList.value,
      showSearch: true,
      mode: 'multiple',
      maxTagCount: 'responsive',
      fieldNames: {
        label: 'name',
        value: 'id',
      },
    },
  },
  {
    label: '金额',
    field: 'amount',
    component: 'InputNumber',
    required: true,
    componentProps: {
      min: 0,
      max: 999,
      precision: 2,
    },
  },
  {
    label: '周期',
    field: ['startTime', 'endTime'],
    component: 'RangePicker',
    required: true,
    componentProps: {
      disabledDate: (current: Dayjs) =>
        current.startOf('day') >= dayjs().startOf('day'),
    },
  },
  {
    label: '附件',
    field: 'annex',
    component: 'UploadFilePro',
    required: true,
    componentProps: {
      packageName: 'user',
      isSecurity: true,
      multiple: true,
    },
  },
]);

const { validate, VBind, setFields } = useForm({
  schemas,
  modelRef,
  labelCol: { style: { width: '70px' } },
});

// 获取详情（编辑模式）
const getDetail = async () => {
  const { data } = await UserApi.getUserDetail(drawer.record?.id || '');
  setFields(data || {});
};

// 保存方法（供父组件调用）
const save = async () => {
  await validate();
  drawer.showSpinning();
  if (drawer.mode === 'add') {
    const { code } = await UserApi.saveUser(modelRef);
    if (code === 200) {
      message.success('新增成功');
    } else return Promise.reject();
  }
  if (drawer.mode === 'edit') {
    const { code } = await UserApi.saveUser(modelRef);
    if (code === 200) {
      message.success('修改成功');
      return Promise.resolve();
    } else return Promise.reject();
  }
};

// 初始化
const init = async () => {
  try {
    drawer.showSpinning();
    const promises = [getProjectList()];
    if (drawer.mode === 'edit') {
      promises.push(getDetail());
    }
    await Promise.all(promises);
  } finally {
    drawer.hideSpinning();
  }
};
init();

defineExpose({ save });
</script>

<template>
  <div>
    <yc-form v-bind="VBind"></yc-form>
  </div>
</template>
```

---

## Example 2: Generate Form Only

This example shows how to generate just a form component (without the table page) for scenarios like standalone create/edit pages.

### Configuration

```json
{
  "formName": "UserForm",
  "apiModule": "user",
  "apiMethod": "saveUser",
  "fields": [
    {
      "label": "姓名",
      "field": "userName",
      "component": "Input",
      "required": true,
      "componentProps": { "maxlength": 10 }
    },
    {
      "label": "项目",
      "field": "projectId",
      "component": "Select",
      "required": true,
      "componentProps": {
        "options": [],
        "showSearch": true,
        "mode": "multiple"
      }
    },
    {
      "label": "金额",
      "field": "amount",
      "component": "InputNumber",
      "required": true,
      "componentProps": { "min": 0, "max": 999, "precision": 2 }
    }
  ],
  "hasDetail": false,
  "apiGetDetailMethod": "getUserDetail"
}
```

### Generated File Structure

```
src/pages/user-edit/
└── index.vue
```

### Key Generated File

#### `index.vue` (Standalone Form Page)

```vue
<script setup lang="ts">
import { UserApi } from '@/api';
import { useForm } from '@/hooks/useForm.ts';
import { useRoute } from 'vue-router';

const route = useRoute();
const isEdit = computed(() => !!route.params.id);

// 表单模型
const modelRef = reactive<Partial<UserEditType.Req>>({});

// 字段配置（从配置生成）
const schemas = computed<YcForm.Schema[]>(() => [
  {
    label: '姓名',
    field: 'userName',
    component: 'Input',
    required: true,
    componentProps: { maxlength: 10 },
  },
  {
    label: '项目',
    field: 'projectId',
    component: 'Select',
    required: true,
    componentProps: {
      options: projectList.value,
      showSearch: true,
      mode: 'multiple',
    },
  },
  {
    label: '金额',
    field: 'amount',
    component: 'InputNumber',
    required: true,
    componentProps: { min: 0, max: 999, precision: 2 },
  },
]);

const { validate, VBind, setFields } = useForm({
  schemas,
  modelRef,
  labelCol: { style: { width: '70px' } },
});

// 获取详情（编辑模式）
const getDetail = async () => {
  const { data } = await UserApi.getUserDetail(route.params.id as string);
  setFields(data || {});
};

// 保存
const handleSubmit = async () => {
  await validate();
  try {
    const { code } = await UserApi.saveUser(modelRef);
    if (code === 200) {
      message.success('保存成功');
      // 跳转回列表页或详情页
    }
  } catch (error) {
    // 错误处理
  }
};

// 初始化
const init = async () => {
  if (isEdit.value) {
    await getDetail();
  }
};
init();
</script>

<template>
  <div class="form-page">
    <yc-form v-bind="VBind" />
    <div class="form-actions">
      <a-button type="primary" @click="handleSubmit">保存</a-button>
      <a-button @click="router.back()">返回</a-button>
    </div>
  </div>
</template>
```

---

## Example 3: DetailForm Usage (Standalone)

This example shows how to use the `DetailForm` component to display read-only detail information. The DetailForm is a simple component that uses `yc-description` to render a detail view.

### Configuration

```json
{
  "detailSchema": [
    { "label": "姓名", "key": "userName", "tip": "用户真实姓名" },
    { "label": "手机号", "key": "phone" },
    { "label": "金额", "key": "amount", "customRender": "{ text } + '元'" },
    { "label": "时间", "key": "time" }
  ]
}
```

### Generated File Structure

```
src/pages/user-detail/
└── index.vue
```

### Key Generated File

#### `index.vue` (Detail Page)

```vue
<script setup lang="ts">
import { UserApi } from '@/api';
import { detailSchema } from './data';

const detail = reactive<Partial<UserGetDetailType.Res>>({});
const route = useRoute();

// 获取详情
const getDetail = async () => {
  const { data } = await UserApi.getUserDetail(route.params.id);
  Object.assign(detail, data || {});
};

// 初始化
const init = async () => {
  await getDetail();
};
init();
</script>

<template>
  <div class="detail-page">
    <yc-description
      title="基本信息"
      :data="detail"
      :schema="detailSchema"
    />
  </div>
</template>
```

#### `data.ts` (Detail Schema)

```typescript
export const detailSchema: DescItem[] = [
  {
    label: '姓名',
    key: 'userName',
    tip: '可以设置提示信息',
  },
  {
    label: '手机号',
    key: 'phone',
  },
  {
    label: '金额',
    key: 'amount',
    customRender: ({ text }) => text + '元',
  },
  {
    label: '时间',
    key: 'time',
  },
];
```

**Note:** The `DetailForm` component from `table-demo` is designed to be used inside a drawer. For standalone detail pages, you can directly use `yc-description` with the schema as shown above.

---

## Example 4: Full Integration (Table + Form + Detail)

This example demonstrates the complete integration of all three components working together in a single page with full CRUD functionality.

### Complete Configuration

```json
{
  "pageName": "UserPage",
  "apiModule": "user",
  "apiGetTableMethod": "getUserList",
  "apiGetDetailMethod": "getUserDetail",
  "apiUpdateMethod": "saveUser",
  "apiDeleteMethod": "deleteUser",
  "columns": [ ... ],
  "searchSchema": [ ... ],
  "detailSchema": [ ... ],
  "formFields": [ ... ]
}
```

### Generated File Structure

```
src/pages/user/
├── index.vue              # Table page with drawer
├── data.ts                # All configs (columns, searchSchema, detailSchema, form schemas)
└── components/
    ├── EditForm.vue       # Add/Edit form
    └── DetailForm.vue     # Detail view (inside drawer)
```

### Integration Pattern

The key integration pattern is the **single tl principle**:

1. **One `<tl>` root** for the entire page
2. **One `<tl-drawer>`** that handles all modes (add/edit/detail)
3. **Drawer mode switching** via `drawer.open(mode, title, record)`
4. **Conditional rendering** inside drawer using `v-if="drawer.mode === 'xxx'"`
5. **Parent controls save** via `ref` to child form component

#### `index.vue` Integration Highlights

```vue
<!-- 抽屉内根据 mode 显示不同内容 -->
<tl-drawer :title="drawer.title" :spin="{ spinning: drawer.spinning }">
  <template #buttons>
    <!-- 仅在编辑/新增模式显示保存按钮 -->
    <a-button
      type="primary"
      @click="handleSave"
      v-if="['edit', 'add'].includes(drawer.mode)"
    >
      保存
    </a-button>
    <a-button @click="drawer.close">返回</a-button>
  </template>

  <!-- 详情模式 -->
  <detail-form v-if="drawer.mode === 'detail'" />

  <!-- 编辑/新增模式 -->
  <edit-form ref="editForm" v-if="['edit', 'add'].includes(drawer.mode)" />
</tl-drawer>
```

#### `handleSave` Pattern (Parent Component)

```typescript
const editForm = ref();
const handleSave = async () => {
  try {
    // 调用子组件的 save 方法
    await editForm.value?.save();
    drawer.close();
    // 刷新表格
    search();
  } finally {
    drawer.hideSpinning();
  }
};
```

#### `save` Pattern (Child Form Component)

```typescript
// 暴露 save 方法给父组件
defineExpose({ save });

const save = async () => {
  await validate();
  drawer.showSpinning();
  if (drawer.mode === 'add') {
    const { code } = await Api.saveUser(modelRef);
    if (code === 200) {
      message.success('新增成功');
    } else return Promise.reject();
  }
  if (drawer.mode === 'edit') {
    const { code } = await Api.saveUser(modelRef);
    if (code === 200) {
      message.success('修改成功');
      return Promise.resolve();
    } else return Promise.reject();
  }
};
```

#### `init` Pattern (Child Component)

```typescript
const init = async () => {
  try {
    drawer.showSpinning();
    // 并行加载所有数据
    const promises = [getProjectList(), getLotList()];
    // 编辑模式加载详情
    if (drawer.mode === 'edit') {
      promises.push(getDetail());
    }
    await Promise.all(promises);
  } finally {
    drawer.hideSpinning();
  }
};
init();
```

---

## Key Takeaways

### 1. Single Tl Principle
- Only one `<tl>` component per page
- All drawers share the same `useDrawer(PAGE_NAME)`
- Use `drawer.mode` to distinguish between add/edit/detail/logs

### 2. Drawer Component Lifecycle
- Drawer content components are created/destroyed with `v-if` on mode
- Components call `init()` at top level (not in watcher)
- Parent uses `ref` to call child's `save()` method

### 3. Form Component Structure
- Use `useForm` hook for form registration and validation
- Expose `save()` method that returns `Promise.resolve()` or `Promise.reject()`
- Call `drawer.showSpinning()`/`hideSpinning()` for loading state
- Load remote options and detail data in `init()`

### 4. Table Component Structure
- Use `useTable` hook for data and pagination
- Use `useForm` hook for search form
- Action buttons in `bodyCell` slot call `drawer.open(mode, title, record)`
- Handle delete with `Modal.confirm`

### 5. Configuration Files
- `data.ts` exports: `PAGE_NAME`, `columns`, `searchSchema`, `statusOptions`, `detailSchema`
- Keep all configs in one file for small pages, split if large
- Use TypeScript namespaces for API type definitions

### 6. Mode Handling
- `drawer.open('add', '新增')` - opens form in add mode
- `drawer.open('edit', '编辑', record)` - opens form in edit mode with record data
- `drawer.open('detail', '详情', record)` - opens detail view
- Child components use `v-if="['edit', 'add'].includes(drawer.mode)"` to show/hide

### 7. Save Flow
1. User clicks "保存" button in drawer
2. Parent `handleSave` calls `editForm.value.save()`
3. Child `save()` validates form, calls API
4. Child returns `Promise.resolve()` on success, `Promise.reject()` on failure
5. Parent closes drawer and refreshes table on resolve
6. Parent shows error message on reject (child already showed success message)

### 8. Detail Form Pattern
- Use `yc-description` component with `schema` prop
- `schema` defines field labels, keys, and optional `customRender`
- DetailForm component is minimal: just fetch data and bind to `yc-description`
- Can be used standalone (detail page) or inside drawer (table detail mode)
