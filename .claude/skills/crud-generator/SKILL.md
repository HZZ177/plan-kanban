---
name: crud-generator
description: CRUD生成器 - 快速生成带有增删改查功能的表格页面和表单组件。当用户请求创建表格页面、表单页面、增删改查功能，或需要生成 Vue 组件时使用此 skill。
---

# CRUD 生成器 Skill

## 技能信息

- **名称**: crud-generator
- **版本**: 1.2.0
- **描述**: 用于快速生成带有增删改查功能的表格页面和表单组件
- **作者**: KT Agent Framework Team
- **标签**: vue, crud, table, form, generator

## 功能描述

- 生成带有增删改查功能的表格页面
- 生成表单组件，支持各种表单控件和验证
- 支持自定义表格列、数据来源、操作按钮等
- 生成完整的 Vue 组件，包括模板、脚本和样式
- 基于 Ant Design Vue 3.2.20 组件库（文档地址：`https://3x.antdv.com/components/overview-cn/`，如不了解组件参数可在此查找）

## 输入参数

### 1. 生成表格 CRUD 页面

- **参数名称**: `action`
- **类型**: string
- **必填**: 是
- **描述**: 操作类型，固定为 `generate-table`

- **参数名称**: `pageName`
- **类型**: string
- **必填**: 是
- **描述**: 页面名称，用于生成文件和路由（需与路由名称一致，全局唯一）

- **参数名称**: `apiModule`
- **类型**: string
- **必填**: 是
- **描述**: API 模块名称，用于导入和调用 API 方法（如 DemoApi）

- **参数名称**: `apiListMethod`
- **类型**: string
- **必填**: 是
- **描述**: 列表接口方法名（如 demoGetTable）

- **参数名称**: `apiCreateMethod`
- **类型**: string
- **必填**: 是
- **描述**: 创建接口方法名

- **参数名称**: `apiUpdateMethod`
- **类型**: string
- **必填**: 是
- **描述**: 更新接口方法名

- **参数名称**: `apiDeleteMethod`
- **类型**: string
- **必填**: 是
- **描述**: 删除接口方法名

- **参数名称**: `apiDetailMethod`
- **类型**: string
- **必填**: 是
- **描述**: 详情接口方法名

- **参数名称**: `columns`
- **类型**: array
- **必填**: 是
- **描述**: 表格列配置
- **子参数**:
  - `title`: 列标题
  - `dataIndex`: 数据字段名
  - `width`: 列宽（可选）
  - `align`: 对齐方式（可选，如：left, right, center）
  - `ellipsis`: 是否显示省略号（可选，默认 false）
  - `fixed`: 固定列（可选，如：right）

- **参数名称**: `route`
- **类型**: object
- **必填**: 否
- **描述**: 路由配置
- **子参数**:
  - `path`: 路由路径（默认与 pageName 相同）
  - `name`: 路由名称（默认与 pageName 相同）
  - `meta`: 路由元信息

- **参数名称**: `searchSchema`
- **类型**: array
- **必填**: 否
- **描述**: 搜索表单配置（页面表头筛选项配置，不需要配置 label）
- **子参数**:
  - `field`: 字段名
  - `component`: 组件类型（对应 `src/components/Form/data.ts` 中 componentMap 的键值）
  - `placeholder`: 占位符（可选）
  - `options`: 选项列表（用于 Select 等类型）
  - `componentProps`: 组件属性配置（可选）
  - `required`: 是否必填（可选，默认 false）
  - `tip`: 提示信息（可选）

> **注意**：searchSchema 是页面表头筛选项配置，不需要配置 `label` 字段（只有表单 fields 需要 label）

### 2. 生成表单组件

- **参数名称**: `action`
- **类型**: string
- **必填**: 是
- **描述**: 操作类型，固定为 `generate-form`

- **参数名称**: `formName`
- **类型**: string
- **必填**: 是
- **描述**: 表单名称，用于生成文件

- **参数名称**: `apiModule`
- **类型**: string
- **必填**: 是
- **描述**: API 模块名称，用于导入和调用 API 方法

- **参数名称**: `apiCreateMethod`
- **类型**: string
- **必填**: 是
- **描述**: 创建接口方法名

- **参数名称**: `apiUpdateMethod`
- **类型**: string
- **必填**: 是
- **描述**: 更新接口方法名

- **参数名称**: `apiDetailMethod`
- **类型**: string
- **必填**: 是
- **描述**: 详情接口方法名

- **参数名称**: `fields`
- **类型**: array
- **必填**: 是
- **描述**: 表单项配置
- **子参数**:
  - `name`: 字段名
  - `label`: 字段标签
  - `component`: 组件类型（对应 `src/components/Form/data.ts` 中 componentMap 的键值）
  - `required`: 是否必填（可选，默认 false）
  - `tip`: 提示信息（可选）
  - `placeholder`: 占位符（可选）
  - `options`: 选项列表（用于 Select 等类型）
  - `componentProps`: 组件属性配置（可选）

## 输出结果

- 生成的 Vue 组件文件（位于 `src/pages/[pageName]/`）
- 生成的路由配置（如果指定）
- 生成的状态管理文件（如果需要）
- 生成的 API 调用文件（如果需要）

## 文件路径说明

生成的表格 CRUD 页面将放在 `src/pages/` 目录下，与 table-demo 平级：

```
src/pages/
├── table-demo/          # 已有示例
│   ├── index.vue        # 表格页面主组件
│   ├── data.ts          # 列配置、搜索表单配置、枚举定义
│   └── components/
│       └── EditForm.vue # 表单组件
└── [pageName]/          # 新生成的页面
    ├── index.vue
    ├── data.ts
    └── components/
        └── [FormName].vue
```

## 示例使用

### 示例 1: 生成表格 CRUD 页面

```json
{
  "action": "generate-table",
  "pageName": "TablePage",
  "apiModule": "Demo",
  "apiListMethod": "demoGetTable",
  "apiCreateMethod": "demoUpdate",
  "apiUpdateMethod": "demoUpdate",
  "apiDeleteMethod": "demoDel",
  "apiDetailMethod": "demoGetDetail",
  "columns": [
    {
      "title": "姓名",
      "dataIndex": "userName",
      "width": 100,
      "align": "left",
      "ellipsis": true
    },
    {
      "title": "手机号",
      "dataIndex": "phone",
      "width": 100,
      "align": "left",
      "ellipsis": true
    },
    {
      "title": "金额",
      "dataIndex": "amount",
      "width": 100,
      "align": "right",
      "ellipsis": true
    },
    {
      "title": "时间",
      "dataIndex": "time",
      "width": 100,
      "align": "left",
      "ellipsis": true
    },
    {
      "title": "状态",
      "dataIndex": "status",
      "width": 110,
      "align": "left",
      "ellipsis": true
    },
    {
      "title": "操作",
      "dataIndex": "action",
      "width": 120,
      "fixed": "right"
    }
  ],
  "route": {
    "path": "/table",
    "name": "TablePage",
    "meta": {
      "title": "Table Demo"
    }
  },
  "searchSchema": [
    {
      "field": "userName",
      "component": "Input",
      "componentProps": {
        "placeholder": "姓名"
      }
    },
    {
      "field": "status",
      "component": "Select",
      "componentProps": {
        "options": [{ "label": "状态：全部", "value": "" }]
      }
    }
  ]
}
```

### 示例 2: 生成表单组件

```json
{
  "action": "generate-form",
  "formName": "EditForm",
  "apiModule": "Demo",
  "apiCreateMethod": "demoUpdate",
  "apiUpdateMethod": "demoUpdate",
  "apiDetailMethod": "demoGetDetail",
  "fields": [
    {
      "name": "userName",
      "label": "姓名",
      "component": "Input",
      "required": true,
      "tip": "可以设置提示信息",
      "componentProps": {
        "maxlength": 10
      }
    },
    {
      "name": "projectId",
      "label": "项目",
      "component": "Select",
      "required": true,
      "componentProps": {
        "options": [],
        "showSearch": true,
        "mode": "multiple",
        "maxTagCount": "responsive",
        "fieldNames": {
          "label": "name",
          "value": "id"
        }
      }
    },
    {
      "name": "amount",
      "label": "金额",
      "component": "InputNumber",
      "required": true,
      "componentProps": {
        "min": 0,
        "max": 999,
        "precision": 2
      }
    },
    {
      "name": ["startTime", "endTime"],
      "label": "周期",
      "component": "RangePicker",
      "required": true
    },
    {
      "name": "rate",
      "label": "比率",
      "component": "InputNumber",
      "required": true,
      "componentProps": {
        "min": 0,
        "max": 100,
        "precision": 2,
        "addonAfter": "%"
      }
    },
    {
      "name": "annex",
      "label": "附件",
      "component": "UploadFilePro",
      "required": true,
      "componentProps": {
        "packageName": "demo",
        "isSecurity": true,
        "multiple": true
      }
    }
  ]
}
```

## 实现细节

- 基于 Vue 3 + TypeScript + Rsbuild 技术栈
- 使用 Ant Design Vue 作为 UI 库（文档地址：`https://3x.antdv.com/components/overview-cn/`，如不了解组件参数可在此查找）
- 使用 @kt/unity-hooks 的 useTable
- 使用项目本地的 useDrawer、useForm hooks（路径：`@/hooks/useDrawer.ts`、`@/hooks/useForm.ts`）
- 使用 @kt/unity-table-layout 的 tl-\* 布局组件（tl, tl-main, tl-filter, tl-table, tl-drawer）
- 使用 yc-form 组件构建表单
- 表单组件类型取值参考 `src/components/Form/data.ts` 中的 componentMap 键值
- 使用 action-group 组件展示操作按钮
- 生成的代码符合项目规范和最佳实践
- 支持响应式设计和国际化
- 提供完整的错误处理和加载状态

## 关键代码规范

### 1. 导入规范

```typescript
// 使用项目本地的 hooks
import useDrawer from "@/hooks/useDrawer.ts";
import { useForm } from "@/hooks/useForm.ts";

// 使用 @kt/unity-hooks 的 useTable
import { useTable } from "@kt/unity-hooks";
import type { UseTableOptions } from "@kt/unity-hooks/src/useTable/types";

// 使用 API
import { DemoApi } from "@/api";

// 使用工具函数
import { getLabelByValue } from "@/utils";
```

### 2. 组件命名规范

```typescript
// PAGE_NAME 需要与路由名称一致
export const PAGE_NAME = "TablePage";

// 使用 defineOptions 定义组件名称
defineOptions({ name: PAGE_NAME });
```

### 3. 表格配置规范

```typescript
const tableOptions = reactive<UseTableOptions>({
  currentKey: "pageNo", // 当前页字段名
  pageSizeKey: "pageSize", // 每页条数字段名
  dataSourceKey: "records", // 数据源字段名
  totalKey: "total", // 总数字段名
  immediate: false, // 是否立即加载
  columns, // 列配置
  inParams, // 搜索参数
});
```

#### a-table 组件使用规范

**必须使用 `columns` 属性配置表格列，不能使用 `<a-table-column>` 子组件**

**`tl-table` 的 `visibleColumns` 属性说明：**

- `visibleColumns` 用于控制表格列的显示/隐藏功能
- 默认值应配置为 `[0, 1, 2]`，表示默认显示前 3 列
- 数组中的数字对应 `columns` 数组的索引
- 如果表格列数少于 3 列，应根据实际列数调整（如 2 列则配置为 `[0, 1]`）

```vue
<!-- ✅ 正确：使用 columns 属性，visibleColumns 默认 [0, 1, 2] -->
<tl-table :visibleColumns="[0, 1, 2]">
  <a-table v-bind="VBind" :pagination="pagination">
    <template #bodyCell="{ column: { dataIndex }, record }">
      <template v-if="dataIndex === 'action'">
        <ActionGroup>
          <a-button type="link" @click="openDrawer('detail', record)">详情</a-button>
          <a-button type="link" @click="openDrawer('edit', record)">编辑</a-button>
        </ActionGroup>
      </template>
    </template>
  </a-table>
</tl-table>

<!-- ❌ 错误：使用 a-table-column 子组件 -->
<a-table>
  <a-table-column title="姓名" dataIndex="name" />
  <a-table-column title="操作">
    <template #default="{ record }">
      <a-button @click="handleEdit(record)">编辑</a-button>
    </template>
  </a-table-column>
</a-table>
```

**说明：**

- 表格列配置在 `data.ts` 文件的 `columns` 数组中定义
- 使用 `<template #bodyCell>` 插槽自定义单元格内容
- `dataIndex` 用于区分不同列并渲染对应内容

### 4. 表单配置规范

```typescript
const { validate, VBind, setFields } = useForm({
  schemas, // 表单字段配置
  modelRef, // 表单数据
  labelCol: { style: { width: "70px" } }, // 标签宽度
});
```

### 5. 抽屉使用规范

```typescript
const { drawer } = useDrawer(PAGE_NAME);

// 打开抽屉 - 通过 mode 区分不同操作
drawer.open("add", "新增");
drawer.open("edit", "编辑", record);
drawer.open("detail", "详情", record);

// 加载状态
drawer.showSpinning();
drawer.hideSpinning();
```

### 6. tl 布局规范（重要）

**核心原则：一个页面只能有一个 `<tl>`（tableLayout）根布局组件；所有抽屉（含主表单、详情、日志等）必须放在同一个 `<tl>` 下，通过同一个 `drawer` 的 `mode` 区分内容。**

```vue
<template>
  <tl v-model:drawer="drawer.visible">
    <tl-main>
      <!-- 筛选、表格 -->
    </tl-main>

    <!-- 只有一个 tl-drawer，通过 drawer.mode 区分内容 -->
    <tl-drawer
      :title="drawer.title"
      :spin="{ spinning: drawer.spinning }"
      buttonsPosition="fixed"
      :width="drawer.mode === 'logs' ? 800 : undefined"
    >
      <template #buttons>
        <a-button
          v-if="['add', 'edit'].includes(drawer.mode)"
          type="primary"
          @click="handleSave"
          >保存</a-button
        >
        <a-button @click="drawer.close">返回</a-button>
      </template>

      <EditForm v-if="['add', 'edit', 'detail'].includes(drawer.mode)" />
      <LogDrawer v-if="drawer.mode === 'logs'" :taskId="drawer.record?.task_id" />
    </tl-drawer>
  </tl>
</template>
```

**错误示例（应避免）：**

```vue
<!-- ❌ 错误：页面内存在多个 <tl> -->
<tl v-model:drawer="drawer.visible">
  <tl-main>...</tl-main>
  <tl-drawer>...</tl-drawer>
</tl>
<tl v-model="logDrawer.visible">
  <tl-drawer>...</tl-drawer>
</tl>

<!-- ❌ 错误：为“执行日志”等副抽屉单独使用 useDrawer 和第二个 tl -->
const logDrawer = useDrawer(PAGE_NAME + 'Log');
```

**正确示例：**

```vue
<!-- ✅ 正确：全页仅一个 <tl>，多个抽屉内容用 mode 区分 -->
const { drawer } = useDrawer(PAGE_NAME);
const openLog = (row) => drawer.open('logs', '执行日志', row);

<tl v-model:drawer="drawer.visible">
  <tl-main>...</tl-main>
  <tl-drawer>
    <EditForm v-if="['add','edit','detail'].includes(drawer.mode)" />
    <LogDrawer v-if="drawer.mode === 'logs'" :taskId="drawer.record?.id" />
  </tl-drawer>
</tl>
```

**注意事项：**

- `drawer.mode` 由 `drawer.open(mode, title, record)` 的第一个参数决定
- 常见 mode：`add`、`edit`、`detail`、`logs`（执行日志）等
- 若某 mode 需要不同抽屉宽度，可用 `:width="drawer.mode === 'logs' ? 800 : undefined"` 等形式绑定

### 7. tl-drawer 组件使用规范（重要）

**核心原则：一个页面只能有一个 `<tl-drawer>`，通过 `drawer.mode` 来区分不同的显示内容**

```vue
<template>
  <tl v-model:drawer="drawer.visible">
    <tl-main>
      <!-- 表格内容 -->
    </tl-main>

    <!-- 只有一个 tl-drawer，通过 drawer.mode 区分内容 -->
    <tl-drawer
      :title="drawer.title"
      :spin="{ spinning: drawer.spinning }"
      buttonsPosition="fixed"
    >
      <template #buttons>
        <a-button
          v-if="['add', 'edit'].includes(drawer.mode)"
          type="primary"
          @click="handleSave"
          >保存</a-button
        >
        <a-button @click="drawer.close">返回</a-button>
      </template>

      <!-- 使用 v-if 根据 drawer.mode 渲染不同组件 -->
      <AgentForm v-if="drawer.mode === 'add'" />
      <AgentForm v-if="drawer.mode === 'edit'" :data="drawer.record" />
      <AgentDetail v-if="drawer.mode === 'detail'" :data="drawer.record" />
    </tl-drawer>
  </tl>
</template>
```

**错误示例（应避免）：**

```vue
<!-- ❌ 错误：多个 tl-drawer -->
<tl-drawer>...</tl-drawer>
<tl-drawer>...</tl-drawer>
<!-- 不应该存在多个 -->

<!-- ❌ 错误：没有使用 drawer.mode 区分 -->
<tl-drawer>
  <AgentForm />
</tl-drawer>
```

**正确示例：**

```vue
<!-- ✅ 正确：只有一个 tl-drawer，通过 mode 区分 -->
<tl-drawer>
  <AgentForm v-if="drawer.mode === 'add' || drawer.mode === 'edit'" />
  <AgentDetail v-if="drawer.mode === 'detail'" />
</tl-drawer>
```

**注意事项：**

- `drawer.mode` 的值由 `drawer.open()` 方法的第一个参数决定
- 常见的 mode 值：`add`（新增）、`edit`（编辑）、`detail`（详情）、`apps`（关联应用）等
- 关闭抽屉后会自动清空 `drawer.mode` 和 `drawer.record`

## 注意事项

- **布局**：一个页面只能有一个 `<tl>`（tableLayout）根组件；若有多个抽屉内容（如主表单 + 执行日志），使用同一个 `drawer` 和同一个 `tl-drawer`，通过 `drawer.mode` 区分，不得使用多个 `useDrawer` 或多个 `<tl>`。
- 生成的代码需要根据实际项目情况进行适当调整
- 确保 API 接口符合生成代码的预期格式
- 对于复杂的业务逻辑，可能需要手动修改生成的代码
- 使用项目本地的 useDrawer 和 useForm hooks，而不是从 @kt/unity-hooks 导入
- PAGE_NAME 必须与路由名称一致，且全局唯一


## 类型定义生成说明

### 命名空间规范

类型定义使用命名空间组织，命名规范为：`{Module}{Action}Type`

例如：
- `AgentGetTableType` - Agent 获取表格数据类型
- `AgentEditType` - Agent 编辑类型
- `AgentGetDetailType` - Agent 获取详情类型

### 接口定义规范

每个命名空间包含三个核心接口：

```typescript
declare namespace AgentGetTableType {
  /** 输入参数（搜索表单） */
  interface InParams {
    name?: string;
    status?: string;
  }
  
  /** 请求参数（包含分页） */
  interface Req extends InParams {
    pageNum: number;
    pageSize: number;
  }
  
  /** 响应数据 */
  interface Res {
    records: AgentRecord[];
    total: number;
  }
  
  /** 记录类型 */
  interface AgentRecord {
    id: string;
    name: string;
    description: string;
  }
}
```

### 文件位置

类型定义文件放在 API 模块目录下，命名为 `type.d.ts`：

```
src/api/agent/
├── index.ts        # API 实现
└── type.d.ts       # 类型定义
```

## 下拉选项加载说明

### 静态选项

对于固定的枚举值，直接在 `data.ts` 中定义：

```typescript
export const statusOptions = [
  { label: '初始化', value: 0, status: 'default' },
  { label: '待开始', value: 1, status: 'warning' },
  { label: '运营中', value: 2, status: 'success' },
  { label: '已结束', value: 3, status: 'danger' },
];
```

### 远程选项

从 API 加载的选项，使用 `fieldNames` 配置字段映射：

```typescript
// data.ts
export const projectSchema: YcForm.Schema[] = [
  {
    label: '项目',
    field: 'projectId',
    component: 'Select',
    required: true,
    componentProps: {
      options: [], // 初始为空，在组件中加载
      showSearch: true,
      fieldNames: { label: 'name', value: 'id' },
    },
  },
];
```

```typescript
// EditForm.vue
const projectOptions = ref([]);

const loadProjects = async () => {
  const { data } = await ProjectApi.getList();
  projectOptions.value = data || [];
};

// 修改 schema 使用动态选项
const schemas = computed<YcForm.Schema[]>(() => [
  {
    label: '项目',
    field: 'projectId',
    component: 'Select',
    componentProps: {
      options: projectOptions.value,
      fieldNames: { label: 'name', value: 'id' },
    },
  },
]);
```

## 错误处理说明

### API 请求错误

使用统一的错误处理：

```typescript
const save = async () => {
  try {
    await validate();
    drawer.showSpinning();
    const { code, message: msg } = await AgentApi.agentUpdate(modelRef);
    if (code === 200) {
      message.success('保存成功');
      return Promise.resolve();
    } else {
      message.error(msg || '保存失败');
      return Promise.reject();
    }
  } catch (error) {
    console.error('保存失败:', error);
    return Promise.reject();
  } finally {
    drawer.hideSpinning();
  }
};
```

### 表单验证错误

表单验证失败时会自动显示错误提示：

```typescript
const { validate, VBind } = useForm({
  schemas,
  modelRef,
});

// 验证失败时，useForm 会自动处理错误显示
await validate();
```

### 全局错误处理

请求库已配置全局错误拦截，无需在每个请求中处理网络错误。

## 已知限制说明

### 当前版本限制

1. **不支持复杂嵌套表单**
   - 不支持动态增减的表单字段
   - 不支持嵌套对象表单（如 `user.name`）
   - 需要手动实现复杂表单逻辑

2. **不支持自定义组件**
   - 只能使用 `componentMap` 中预定义的组件
   - 自定义组件需要手动修改生成的代码

3. **不支持复杂表格操作**
   - 不支持行内编辑
   - 不支持拖拽排序
   - 不支持复杂列头（多级表头）

4. **API 格式限制**
   - 假设 API 返回格式为 `{ code: number, data: any, message: string }`
   - 假设列表接口返回格式为 `{ records: [], total: number }`
   - 不符合此格式需要手动调整

5. **API 返回类型**：接口返回类型统一使用 `CommonRes<T>`，不要写 `Promise<CommonRes<T>>`；项目中 `CommonRes` 已在 global.d.ts 中定义为 Promise 类型。

### 需要手动修改的场景

以下场景生成后需要手动调整：

1. **多选关联** - 需要手动处理多选值的转换
2. **文件上传** - 需要配置上传参数和回显逻辑
3. **联动表单** - 如选择省份后加载城市列表
4. **自定义验证** - 复杂的表单验证规则
5. **权限控制** - 按钮级别的权限显示控制

## 类型定义生成说明

生成的代码会自动使用 TypeScript 类型定义，确保类型安全。

### 命名空间命名规范

API 类型定义使用命名空间方式组织，命名规则如下：

- **列表接口类型**: `{apiModule}GetTableType`
  - `InParams`: 筛选项参数类型（对应 `inParams`）
  - `Req`: 请求参数类型（包含分页参数）
  - `record`: 单条记录类型（用于表格行数据）

- **详情接口类型**: `{apiModule}GetDetailType`
  - `Req`: 请求参数类型（通常是 id）
  - `Res`: 响应数据类型

- **编辑/创建类型**: `{apiModule}EditType`
  - `Req`: 表单数据模型类型

### 类型定义文件位置

**规范：类型定义放在对应 API 模块目录下，文件名固定为 `type.d.ts`，不要放在 `src/api/types/` 下。**

```
src/api/
├── agent/
│   ├── index.ts        # API 实现
│   └── type.d.ts       # 该模块的类型定义
├── demo/
│   ├── index.ts
│   └── type.d.ts
└── [module]/
    ├── index.ts
    └── type.d.ts
```

### 类型定义示例

```typescript
// src/api/agent/type.d.ts
declare namespace AgentGetTableType {
  /** 筛选项参数 */
  interface InParams {
    agentName?: string;  // 智能体名称
    status?: string;     // 状态
  }
  
  /** 请求参数（包含分页） */
  interface Req extends InParams {
    pageNo: number;
    pageSize: number;
  }
  
  /** 单条记录类型 */
  interface record {
    id: string;
    agentName: string;
    status: string;
    // ... 其他字段
  }
}

declare namespace AgentGetDetailType {
  interface Req {
    id: string;
  }
  interface Res {
    id: string;
    agentName: string;
    // ... 详情字段
  }
}

declare namespace AgentEditType {
  interface Req {
    id?: string;        // 编辑时必填
    agentName: string;
    status?: string;
    // ... 其他字段
  }
}
```

### 使用示例

```typescript
// 筛选项参数类型
const inParams = reactive<AgentGetTableType.InParams>({});

// 表格数据获取函数
const getTableData = async (params: AgentGetTableType.Req) => {
  const { data } = await AgentApi.demoGetTable(params);
  return data;
};

// 表单数据模型
const modelRef = reactive<Partial<AgentEditType.Req>>({ annex: [] });

// 详情数据类型
const detail = ref<Partial<AgentGetDetailType.Res>>({});
```

## 下拉选项加载说明

表单和搜索表单中的 Select 组件需要配置选项数据源。

### options 配置方式

#### 1. 静态选项（适用于固定选项）

```typescript
// data.ts 中定义
export const statusOptions = [
  { label: '启用', value: '1', status: 'success' },
  { label: '禁用', value: '0', status: 'default' }
];

// 表单字段配置
{
  name: 'status',
  label: '状态',
  component: 'Select',
  componentProps: {
    options: statusOptions
  }
}
```

#### 2. 动态加载选项（适用于远程数据）

在表单组件中通过异步函数加载：

```vue
<script setup lang="ts">
// 定义选项数据
const projectList = ref<Array<{ id: number; name: string }>>([]);

// 加载函数
const getProjectList = async () => {
  const { data } = await ProjectApi.getList();
  projectList.value = data;
};

// 表单字段配置
const schemas = computed<YcForm.Schema[]>(() => [
  {
    label: '项目',
    field: 'projectId',
    component: 'Select',
    componentProps: {
      options: projectList.value,
      showSearch: true,
      fieldNames: {
        label: 'name',
        value: 'id'
      }
    }
  }
]);

// 初始化时加载
const init = async () => {
  await getProjectList();
};
init();
</script>
```

### fieldNames 配置

当 API 返回的数据字段名与组件需要的 `{ label, value }` 格式不一致时，使用 `fieldNames` 映射：

```typescript
{
  componentProps: {
    options: projectList.value,
    fieldNames: {
      label: 'name',    // 将 name 映射为 label
      value: 'id'       // 将 id 映射为 value
    }
  }
}
```

### 常用配置项

```typescript
componentProps: {
  options: [],              // 选项列表
  showSearch: true,         // 显示搜索框
  mode: 'multiple',         // 多选模式
  maxTagCount: 'responsive',// 标签数量自适应
  fieldNames: {             // 字段映射
    label: 'name',
    value: 'id'
  },
  allowClear: true,         // 允许清空
  placeholder: '请选择'      // 占位符
}
```

## 错误处理说明

### API 请求错误处理

#### 1. 删除操作错误处理

```typescript
const handleDel = (row: any) => {
  Modal.confirm({
    title: `确定删除？`,
    onOk: async () => {
      const { code } = await AgentApi.demoDel(row.id);
      if (code === 200) {
        message.success('操作成功');
        await search();  // 刷新表格
      }
      // code !== 200 时，错误由 API 拦截器统一处理
    },
    cancelText: '取消'
  });
};
```

#### 2. 保存操作错误处理

```typescript
const handleSave = async () => {
  try {
    await editForm.value?.save();  // 调用表单保存方法
    drawer.close();
    search();  // 刷新表格
  } finally {
    drawer.hideSpinning();  // 关闭加载状态
  }
};
```

#### 3. 表单保存方法内部错误处理

```typescript
const save = async () => {
  await validate();  // 表单验证
  drawer.showSpinning();
  
  if (drawer.mode === 'add') {
    const { code } = await AgentApi.demoCreate(modelRef);
    if (code === 200) {
      message.success('新增成功');
    } else {
      return Promise.reject();  // 拒绝 Promise，阻止关闭抽屉
    }
  }
  
  if (drawer.mode === 'edit') {
    const { code } = await AgentApi.demoUpdate(modelRef);
    if (code === 200) {
      message.success('修改成功');
      return Promise.resolve();
    } else {
      return Promise.reject();
    }
  }
};
```

### 表单验证错误

表单验证错误会自动显示在对应字段下方：

```typescript
const { validate, VBind, setFields } = useForm({
  schemas,      // 包含 required 等验证规则
  modelRef,     // 表单数据
  labelCol: { style: { width: '70px' } }
});

// 调用 validate() 时会触发验证
await validate();  // 验证失败会抛出异常
```

### 加载状态管理

```typescript
// 显示加载状态
drawer.showSpinning();

// 隐藏加载状态（建议在 finally 中调用）
drawer.hideSpinning();

// 表格加载状态由 useTable 自动管理
const { VBind, VOn, search, run, pagination, dataSource } = useTable(
  getTableData,
  tableOptions
);
```

### 统一错误处理建议

1. **API 层**: 在 `src/api/index.ts` 中配置 Axios 拦截器，统一处理 HTTP 错误
2. **业务层**: 只处理业务逻辑错误（code !== 200）
3. **UI 层**: 使用 `message.success/error` 提示用户

## 已知限制说明

### 当前模板不支持的功能

1. **不支持自定义验证规则**
   - 模板只支持 `required` 必填验证
   - 复杂验证规则（如正则、自定义函数）需要手动修改

2. **不支持联动字段**
   - 字段之间的联动逻辑（如选择省市区）需要手动实现
   - 需要在表单组件中添加 `watch` 监听

3. **不支持复杂的表格操作列**
   - 模板只支持基础的增删改查按钮
   - 自定义操作按钮需要手动添加

4. **不支持树形表格**
   - 模板只支持扁平数据结构
   - 树形表格需要手动配置 `childrenColumnName` 等属性

5. **不支持批量操作**
   - 模板不包含批量删除、批量导出等功能
   - 需要手动添加选择框和批量操作逻辑

6. **不支持高级搜索**
   - 搜索表单只支持基础字段
   - 复杂搜索条件（如日期范围、多条件组合）需要手动扩展

### 需要手动修改的场景

1. **需要自定义 API 类型定义**
   - 模板使用占位符类型（如 `{{apiModule}}GetTableType`）
   - 需在**对应 API 模块目录下的 `type.d.ts`** 中定义（如 `src/api/agent/type.d.ts`），不要放在 `src/api/types/` 下

2. **需要自定义数据字典**
   - 模板中的 `statusOptions` 等枚举需要手动定义
   - 建议在 `src/utils/enum.ts` 中统一管理

3. **需要自定义路由权限**
   - 模板生成的路由配置不包含权限信息
   - 需要在路由配置中添加 `meta.permissions`

4. **需要自定义表单布局**
   - 模板使用默认的单列表单布局
   - 多列布局、分组等需要手动调整 `schemas` 配置

5. **需要自定义表格列渲染**
   - 模板只支持基础的 `bodyCell` 插槽
   - 自定义渲染（如图片、富文本）需要手动添加插槽

### 注意事项

- 生成的代码是基础模板，实际使用时需要根据业务需求调整
- 确保 API 接口返回的数据格式与类型定义匹配
- 复杂的业务逻辑建议在 service 层封装
- 使用项目统一的错误处理和消息提示机制
