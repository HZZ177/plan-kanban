# CRUD Generator FAQ

Frequently asked questions about CRUD Generator and TableLayout usage.

## General Usage

**When should I use CRUD Generator?**
Use for standard CRUD pages with simple forms and tables. It generates boilerplate quickly for common patterns like list pages with add/edit/detail drawers. Avoid for complex nested forms, custom components, or advanced table features like inline editing.

**Can I generate custom components?**
No. The generator only supports components from `componentMap` in `src/components/Form/data.ts`. Custom components require manual modification after generation.

**How do I handle complex business logic?**
The generator provides a template. Complex logic like field dependencies, custom validation, or multi-select conversion must be implemented manually in the generated component. See `patterns.md` for extension points.

**How do I implement detail pages?**
Detail pages use `yc-description` component, not `useForm`. The generator currently does not auto-generate detail pages (generate-detail action is planned but not implemented). Create DetailForm manually following the pattern in `patterns.md` section 7.

**Why is reusing EditForm for detail mode prohibited?**
Reusing EditForm with `disabled: true` violates separation of concerns. Detail pages have different layout needs (multi-column, custom rendering) and performance requirements (no form validation logic). Always create a separate `DetailForm.vue` using `yc-description`. See `patterns.md` section 7 for the full rationale and implementation guide.

**Can I use antd components instead of yc-description in DetailForm?**
Yes. The "Public Components vs Free Implementation" section in `patterns.md` explains when to bypass public components. If `yc-description` cannot meet your layout or interaction needs, directly use ant-design-vue components like `<a-descriptions>`, `<a-timeline>`, or custom combinations. Public components are preferred but not mandatory when they don't serve the requirement.

## Slot Patterns

**How do I add a custom form field that is not in componentMap?**

Use `component: 'Render'` in the schema and provide a named slot matching the field name:

```typescript
// In EditForm.vue schemas
{
  label: '自定义',
  field: 'custom',
  component: 'Render',
}
```

```vue
<!-- In EditForm.vue template -->
<yc-form v-bind="VBind">
  <template #custom>
    <a-input v-model:value="modelRef.custom" />
    <!-- Or any other Vue component -->
  </template>
</yc-form>
```

The slot name must exactly match the `field` value. This pattern allows you to inject arbitrary Vue components into the form while still using `yc-form` for layout and validation integration.

**How do I customize rendering of a single field in yc-description?**

You have two options:

1. **Per-field `customRender` in `detailSchema`** (simple):

```typescript
{ label: '时间', key: 'time', customRender: ({ text }) => `时间：${text}` }
```

2. **`#item` slot in `yc-description`** (when multiple fields share logic):

```vue
<yc-description :data="detail" :schema="detailSchema">
  <template #item="{ key, text, record }">
    <div v-if="key === 'time'">时间：{{ text }}</div>
    <div v-else-if="key === 'status'">
      <a-tag color="blue">{{ text }}</a-tag>
    </div>
    <!-- Let other fields use default rendering -->
  </template>
</yc-description>
```

**When should I use `customRender` vs `#item` slot?**

- Use `customRender` for simple, per-field custom rendering. It's declarative and stays in the schema.
- Use `#item` when you need to customize multiple fields with shared logic, or when rendering requires helper functions (e.g., color mapping, label lookups). Keep in mind `#item` replaces the default renderer, so you must handle all fields you want to customize.

See `patterns.md` Section 12 for detailed patterns and comparison.

## Status Display

**How should I display status values in table cells?**

Use `a-tag` with explicit color values. Define a `color` field in your `statusOptions` that maps to Ant Design's supported color keywords (e.g., `'success'`, `'error'`, `'warning'`, `'default'`).

```typescript
// data.ts
export const statusOptions = [
  { label: '在线', value: 'online', color: 'success' },
  { label: '离线', value: 'offline', color: 'default' },
];
```

```vue
<!-- index.vue -->
<template #bodyCell="{ column: { dataIndex }, record }">
  <template v-if="dataIndex === 'status'">
    <a-tag :color="getLabelByValue(record.status, statusOptions, 'color')">
      {{ getLabelByValue(record.status, statusOptions) }}
    </a-tag>
  </template>
</template>
```

The `getLabelByValue` helper finds the matching option and returns its `color` property. For simple statuses, you can also compute color directly: `:color="record.status === 'online' ? 'success' : 'default'"`.

For a complete list of recommended color mappings, see `patterns.md` Section 5.

## Table Configuration

**Why must I use columns prop instead of a-table-column?**
The TableLayout's column visibility feature requires all columns to be defined in the `columns` array. It uses indices to show/hide columns via CSS classes. `<a-table-column>` subcomponents cannot be controlled this way.

```vue
<!-- ✅ Correct -->
<a-table v-bind="VBind">
  <template #bodyCell="{ column: { dataIndex }, record }">
    <!-- Custom cell content -->
  </template>
</a-table>

<!-- ❌ Wrong -->
<a-table>
  <a-table-column title="Name" dataIndex="name" />
</a-table>
```

**What if my table has multi-level headers?**
TableLayout's CSS-based column hiding doesn't work with nested headers. Switch between complex and simple column definitions when drawer opens:

```typescript
watch(() => drawer.visible, (val) => {
  tableOptions.columns = val ? simpleColumns : complexColumns;
});
```

## Layout Architecture

**What is the single tl principle?**
One page = one `<tl>` root = one `useDrawer(PAGE_NAME)` = one `<tl-drawer>`. All drawer content (add, edit, detail, logs) shares the same drawer instance and is distinguished by `drawer.mode`. Multiple `<tl>` or `useDrawer()` on one page breaks the layout.

**When should I nest TableLayout (tl inside tl-drawer)?**
When drawer content itself needs a table layout (master-detail-detail pattern). Each nested `Tl` manages its own drawer context independently:

```vue
<tl v-model:drawer="mainDrawer.visible">
  <tl-main>...</tl-main>
  <tl-drawer>
    <tl v-model:drawer="logDrawer.visible">
      <tl-main>...</tl-main>
      <tl-drawer>...</tl-drawer>
    </tl>
  </tl-drawer>
</tl>
```

## Drawer Patterns

**Why does Drawer component call init() directly instead of watching drawer.visible?**
The drawer's content components (EditForm, DetailForm) need to load data when the drawer opens. Using `init()` directly in the component ensures data loads exactly once when the drawer mode changes, avoiding race conditions from rapid drawer operations. The pattern:

```typescript
const init = async () => {
  drawer.showSpinning();
  await loadData();
  drawer.hideSpinning();
};
init();
```

## Type Definitions

**Where do I put type definitions?**
In the API module directory, not centralized: `src/api/[module]/type.d.ts`. Use namespace pattern `{Module}{Action}Type`:

```typescript
// src/api/agent/type.d.ts
declare namespace AgentGetTableType {
  interface InParams { agentName?: string; }
  interface Req extends InParams { pageNo: number; pageSize: number; }
  interface Res { records: AgentRecord[]; total: number; }
  interface record { id: string; agentName: string; }
}
```

**Why not `src/api/types/`?**
Types should co-locate with the API implementation they describe. This keeps related code together and avoids a monolithic types folder.

## Common Gotchas

**Why does my table column misalign when drawer opens?**
Ensure all columns have explicit `width` properties. The `visibleColumns` feature hides columns via CSS but doesn't recalculate widths. Missing widths cause alignment issues.

**Why does Drawer not show loading state?**
Use `drawer.showSpinning()` and `drawer.hideSpinning()` around async operations. The `:spin="{ spinning: drawer.spinning }"` prop must be bound to the drawer component.

**Can I have multiple drawers on the same page?**
No. Use `drawer.mode` to switch content within one `<tl-drawer>`. Separate drawers require separate `<tl>` roots, violating the single tl principle.

**Why does "More Conditions" button not appear?**
`TlFilterSecond` requires a parent `TlFilter` without `TlFilterLeft` child. The button is auto-injected only in that configuration.

---

💡 **Tip**: For detailed patterns and examples, see `patterns.md`. For unsupported features, see `limitations.md`. For TableLayout component API, see `table-layout.md`.
