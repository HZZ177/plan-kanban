# TableLayout Component Library

## Introduction

`@kt/unity-table-layout` is a layout component library designed for standardizing CRUD page layouts in Vue 3 applications. It provides a set of composable components (`tl`, `tl-main`, `tl-filter`, `tl-table`, `tl-drawer`, etc.) that enforce consistent layout patterns, responsive behavior, and drawer management.

**Package Location**: `common/unity-plus/packages/table-layout/`  
**Version**: 2.0.20+  
**Used By**: CRUD Generator skill, all admin pages

## Core Components Overview

| Component | Alias | Description |
|-----------|-------|-------------|
| `Tl` | `tl` | Root layout component providing drawer context |
| `TlMain` | `tl-main` | Main content area containing filter and table |
| `TlFilter` | `tl-filter` | Filter/search bar container |
| `TlFilterLeft` | `tl-filter-left` | Left section of filter (form items) |
| `TlFilterRight` | `tl-filter-right` | Right section of filter (action buttons) |
| `TlFilterSecond` | `tl-filter-second` | Collapsible secondary filter bar |
| `TlTable` | `tl-table` | Table container with drawer column visibility control |
| `TlDrawer` | `tl-drawer` | Drawer component for forms/details |
| `TlTableTop` | `tl-table-top` | Table top toolbar slot wrapper |

## Installation & Registration

```typescript
// main.ts
import TableLayout from '@kt/unity-table-layout';
import { setTableLayoutGlobalOptions } from '@kt/unity-table-layout';

// Optional: Global configuration before app.use()
setTableLayoutGlobalOptions({
  drawerStyle: 'custom', // 'custom' | 'ant'
  antDrawer: {
    keyboard: true,
    mask: true,
    maskClosable: true,
    width: '50%',
    placement: 'right'
  },
  loadingFullTableLayout: true
});

app.use(TableLayout);
```

All child components (`TlMain`, `TlFilter`, `TlTable`, `TlDrawer`, etc.) are automatically globally registered.

## Basic Usage

### Standard CRUD Layout

```vue
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
          <!-- table columns -->
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

      <edit-form v-if="['add', 'edit', 'detail'].includes(drawer.mode)" />
    </tl-drawer>
  </tl>
</template>
```

### Filter with Left/Right Layout

```vue
<tl-filter>
  <tl-filter-left>
    <a-form-item>
      <a-input placeholder="姓名" v-model:value="name" />
    </a-form-item>
    <a-form-item>
      <a-select v-model:value="status">
        <a-select-option value="">全部</a-select-option>
      </a-select>
    </a-form-item>
  </tl-filter-left>

  <tl-filter-right>
    <a-button type="primary" @click="search">查询</a-button>
    <a-button type="link" @click="handleExport">导出</a-button>
  </tl-filter-right>
</tl-filter>
```

### Tabs + Secondary Filter Pattern

```vue
<tl-filter role="tabs">
  <a-tabs v-model:activeKey="activeKey">
    <a-tab-pane key="1" tab="Tab 1" />
    <a-tab-pane key="2" tab="Tab 2" />

    <template #rightExtra>
      <a-form-item label="时间范围">
        <a-range-picker />
      </a-form-item>
      <a-input placeholder="搜索" style="width: 200px" />
      <a-button type="primary" @click="search">查询</a-button>
      <a-button @click="filterSecondVisible = !filterSecondVisible">
        {{ filterSecondVisible ? '收起' : '' }}更多条件
      </a-button>
    </template>
  </a-tabs>
</tl-filter>

<tl-filter-second :visible="filterSecondVisible">
  <a-form-item>
    <a-input placeholder="高级搜索条件" size="small" />
  </a-form-item>
</tl-filter-second>
```

## Component API Reference

### Tl (TableLayout)

Root component that provides layout context and drawer state management.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `fixed` | `boolean` | `true` | Enable fixed table layout with scroll handling |
| `drawer` | `boolean` | `false` | Control drawer visibility (v-model) |
| `card` | `boolean` | `true` | Enable card-style padding and background |
| `loading` | `boolean \| object` | `undefined` | Table loading state (syncs with table loading when `loadingFullTableLayout` is true) |
| `loadingFullTableLayout` | `boolean` | `globalOptions.loadingFullTableLayout` | Whether loading overlay covers entire layout |

**Emits**:
- `update:drawer` - Drawer visibility change

**Provides** (for child components):
- `drawerKey` - Reactive drawer visibility ref
- `updateDrawerKey` - Function to update drawer state
- `drawerStyleKey` - Drawer style config ref
- `tableLoadingKey` - Table loading state ref
- `mainMountedKey` - Main component mounted flag
- `filterSecondMountedKey` - FilterSecond mounted flag
- `filterSecondOpenKey` - FilterSecond open state
- `filterLeftMountedKey` - FilterLeft mounted flag
- `filterCustomSwitchKey` - Custom switch control flag
- `inDrawerKey` - Whether inside drawer context

---

### TlMain

Main content wrapper that holds filter and table sections.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| *none* | - | - | No props |

**Behavior**:
- Injects `mainMountedKey` and sets it to `true` when mounted
- Provides `tableMountedKey` to child `TlTable`

---

### TlFilter

Filter bar container that conditionally renders based on layout type.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `role` | `'' \| 'tabs'` | `''` | Filter role; `'tabs'` enables tabs + rightExtra pattern |

**Slots**:
- `default` - Filter content (form items, buttons)

**Notes**:
- Automatically detects `TlFilterLeft` child to switch between left/right layout vs. single-column layout
- Hidden when drawer is open (`v-show={!drawer?.value}`)

---

### TlFilterLeft

Left section of filter bar (typically contains form items).

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| *none* | - | - | No props |

**Slots**:
- `default` - Form items and inputs

**Behavior**:
- Sets `filterLeftMounted` to `true` on mount
- Wraps content in `<div class="table-layout__filter-left flex-1">`

---

### TlFilterRight

Right section of filter bar (typically contains action buttons).

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| *none* | - | - | No props |

**Slots**:
- `default` - Buttons (export, etc.)

**Renders**: `<div class="table-layout__filter-right ml-[32px]">`

---

### TlFilterSecond

Collapsible secondary filter bar with automatic "More Conditions" button.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visible` | `boolean` | `undefined` | Controlled visibility (if set, overrides internal state) |

**Slots**:
- `default` - Additional filter form items (use `size="small"`)

**Behavior**:
- If `visible` is not provided, automatically injects "更多条件" (More Conditions) button at the end of the parent form
- Button toggles `filterSecondOpen` state
- Content wrapped in `<Transition name="filter-second-fade">`
- Form uses `layout="inline"` and all items should be `size="small"`

**When to use**:
- For advanced search options that can be collapsed
- Typically paired with `TlFilter` without `role="tabs"`

---

### TlTable

Table container that controls column visibility when drawer opens.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visibleColumns` | `number[]` | `[0, 1, 2]` | Column indices to keep visible when drawer opens (1-based in CSS classes) |
| `visibleAction` | `number \| string \| null` | `undefined` | Action column index to keep visible when drawer opens; use `'last'` for last column |
| `visibleButton` | `number \| null` | `undefined` | Button index within action column to keep visible when drawer opens |

**Slots**:
- `default` - Contains `<a-table>` component

**How it works**:
- When `drawer` opens, `TlTable` adds CSS classes to hide non-visible columns
- Uses CSS selectors like `.tl-visible-column--index-1`, `.tl-visible-action--index-last`, etc.
- Automatically adjusts for scrollbar presence when `visibleAction="last"`

**Important**:
- `visibleColumns` indices are **1-based** in CSS (index 0 → `tl-visible-column--index-1`)
- Default `[0, 1, 2]` shows first 3 columns; adjust based on actual column count
- If you have fewer than 3 columns, change default accordingly

---

### TlDrawer

Drawer component for displaying forms or detail views. Supports two styles: `custom` (custom implementation) and `ant` (Ant Design Drawer wrapper).

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string \| slot` | `''` | Drawer header title |
| `spin` | `object` | `{ spinning: false }` | Spin props (passed to `<a-spin>`) |
| `buttonsPosition` | `'append' \| 'fixed' \| 'auto'` | `'auto'` | Button position strategy |
| `drawerStyle` | `'custom' \| 'ant'` | `globalOptions.drawerStyle` | Drawer style variant |
| `antDrawer` | `object` | `globalOptions.antDrawer` | Additional props for Ant Drawer (when `drawerStyle="ant"`) |

**Events**:
- `close` - Emitted when drawer closes
- `after-visible-change` - Emitted with `boolean` after transition ends

**Slots**:
- `title` - Custom title content
- `buttons` - Action buttons (save, cancel, etc.)
- `default` - Main drawer content (form, detail view, etc.)

**Buttons Position Logic** (`buttonsPosition="auto"`):
1. Initially sets `buttonsPosition = 'append'`
2. After drawer opens and content renders (220ms delay), calculates scroll height
3. If `drawerMain.scrollHeight > drawerMain.clientHeight`, switches to `'fixed'` (buttons stick to bottom)
4. Otherwise keeps `'append'` (buttons at bottom of content)

**Global Config** (`setTableLayoutGlobalOptions`):
```typescript
{
  drawerStyle: 'custom', // or 'ant'
  antDrawer: {
    keyboard: true,
    mask: true,
    maskClosable: true,
    width: '50%',
    placement: 'right' // 'top' | 'right' | 'bottom' | 'left'
  },
  loadingFullTableLayout: true
}
```

**When to use `drawerStyle="ant"`**:
- When you need Ant Design's built-in drawer features (keyboard escape, mask click, width presets)
- For simpler implementations without custom scroll handling

---

### TlTableTop

Simple wrapper component for adding content above the table (rarely used).

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| *none* | - | - | No props |

**Slots**:
- `default` - Toolbar content

**Renders**: `<div class="table-layout__table-top">`

---

## Advanced Usage Patterns

### 1. Complex Header Switching

When using multi-level table headers, CSS-based column hiding doesn't work properly. Solution: switch between complex and simple column definitions when drawer opens.

```typescript
// Define both column configurations
const complexColumns = [
  { title: 'ID', dataIndex: 'id' },
  {
    title: 'Other',
    children: [
      { title: '标题', dataIndex: 'title' },
      { title: '用户名', dataIndex: ['user', 'name'] }
    ]
  },
  { title: '操作', dataIndex: 'action' }
];

const simpleColumns = [
  { title: 'ID', dataIndex: 'id' },
  { title: '标题', dataIndex: 'title' },
  { title: '用户名', dataIndex: ['user', 'name'] },
  { title: '操作', dataIndex: 'action' }
];

// Initialize with complex columns
const tableOptions = reactive<UseTableOptions>({
  columns: complexColumns,
  // ...
});

// Switch on drawer open/close
watch(() => drawer.visible, (val) => {
  tableOptions.columns = val ? simpleColumns : complexColumns;
});
```

### 2. Nested Tl (TableLayout inside Drawer)

When the drawer content itself needs a table layout (master-detail-detail pattern), nest another `Tl` inside `TlDrawer`.

```vue
<tl v-model:drawer="mainDrawer.visible">
  <tl-main>
    <!-- Main table -->
  </tl-main>

  <tl-drawer :title="'执行日志'">
    <tl v-model:drawer="logDrawer.visible">
      <tl-main>
        <tl-filter>...</tl-filter>
        <tl-table>...</tl-table>
      </tl-main>
      <tl-drawer>...</tl-drawer>
    </tl>
  </tl-drawer>
</tl>
```

**Important**: Each nested `Tl` manages its own drawer context independently.

### 3. Request Cancellation Pattern

To prevent race conditions when rapidly opening drawers, cancel previous requests:

```typescript
let controller: AbortController;

const handleRowClick = async (record: any) => {
  // Cancel any pending request from previous drawer
  controller?.abort();
  controller = new AbortController();

  drawer.showSpinning();
  try {
    const { data } = await Api.getDetail(record.id, {
      signal: controller.signal
    });
    // Handle data
  } catch (error) {
    // If cancelled, keep drawer spinning to prevent stale data
    if (error.name === 'AbortError') {
      drawer.spinning = true;
      return;
    }
    // Handle other errors
  } finally {
    drawer.hideSpinning();
  }
};
```

### 4. Scrollbar Handling

The layout automatically handles scrollbar width adjustments when `fixed={true}`. The `useGetScrollBarWidth` hook sets CSS variables for proper column alignment.

**No manual intervention needed** unless you override default styles.

---

## Important Notes

### Single Tl Principle

**Every page must have exactly ONE `<tl>` root component.** All drawers (add, edit, detail, logs) must share the same `<tl-drawer>` and be distinguished by `drawer.mode`. Never use multiple `<tl>` components or multiple `useDrawer()` instances on a single page.

✅ **Correct**:
```vue
<tl v-model:drawer="drawer.visible">
  <tl-main>...</tl-main>
  <tl-drawer>
    <edit-form v-if="drawer.mode === 'edit'" />
    <detail-form v-if="drawer.mode === 'detail'" />
  </tl-drawer>
</tl>
```

❌ **Wrong**:
```vue
<!-- Multiple tl -->
<tl>...</tl>
<tl>...</tl>

<!-- Multiple useDrawer -->
const drawer1 = useDrawer('Page1');
const drawer2 = useDrawer('Page2');
```

### Form Item Labels in Filter

`TlFilter` supports adding `label` to `<a-form-item>` when you need to explain the input purpose:

```vue
<tl-filter>
  <a-form-item label="支付时间">
    <a-range-picker />
  </a-form-item>
</tl-filter>
```

By default, the project uses placeholder-only style, but labels are allowed when needed.

### Loading State Management

- Use `drawer.showSpinning()` and `drawer.hideSpinning()` to control drawer loading
- Table loading is managed by `useTable` hook and can be synced with layout via `loadingFullTableLayout`
- When `loadingFullTableLayout=true`, the entire layout shows loading overlay, not just the table

### Card Mode

`Tl` uses `card` mode by default (`card={true}`), which adds white background, padding, and rounded corners. Set `card={false}` for full-width layouts without card styling.

**Note**: When `Tl` is nested inside `TlDrawer`, card mode is automatically disabled.

---

## FAQ

### When should I use TableLayout?

Use `TableLayout` for any page that has:
- A filter/search bar at the top
- A data table with pagination
- Drawer-based create/edit/detail operations

It provides consistent spacing, responsive behavior, and handles scroll synchronization automatically.

### Can I use TableLayout for detail popups instead of drawers?

No. The current design standard uses drawers for all detail/edit operations. If you need a modal dialog, use `a-modal` separately, but this breaks the layout pattern and is not recommended.

### What if my drawer needs another table with its own interactions?

Use nested `Tl` inside the drawer. Each `Tl` manages its own drawer state, so you can have a table-within-drawer-with-drawer pattern.

### Why does my table column misalign when drawer opens?

Ensure:
1. All columns have explicit `width` properties
2. You're using `TlTable` with proper `visibleColumns` configuration
3. No CSS overrides breaking the layout

### Can I have multiple drawers on the same page?

No. Follow the single drawer principle: use `drawer.mode` to switch between different content types (add/edit/detail/logs) within the same `<tl-drawer>`.

### How do I customize the "More Conditions" button text?

The button text is internationalized via `@kt/unity-locale`. Override the translation key `KTUnity.TableLayout.moreConditions` in your locale files.

---

## Migration from Manual Layouts

If you're converting an existing page to use `TableLayout`:

1. Wrap the entire page in `<tl v-model:drawer="drawer.visible">`
2. Move filter section into `<tl-filter>` (remove extra wrappers)
3. Move table section into `<tl-table>` (keep `<a-table>` inside)
4. Replace any custom drawer implementation with `<tl-drawer>`
5. Move drawer content into the `default` slot of `TlDrawer`
6. Remove any manual drawer state management - use `useDrawer()` hook instead
7. Update `visibleColumns` to match your table's important columns (usually first 3)

See `admin_frontend/src/pages/table-demo/` for a complete working example.

---

## TypeScript Support

All components are fully typed. Import types when needed:

```typescript
import type { GlobalOptions } from '@kt/unity-table-layout';
import type { ButtonsPosition } from '@kt/unity-table-layout';
```

---

## CSS Customization

The library uses Tailwind CSS utility classes. To customize:

1. Override CSS variables in your global styles
2. Use deeper selectors to override component styles
3. Avoid modifying library source - use `!important` sparingly

Key CSS classes:
- `.table-layout` - Root container
- `.table-layout__main` - Main content area
- `.table-layout__filter` - Filter bar
- `.table-layout__table` - Table wrapper
- `.table-layout__drawer` - Drawer container

---

## Performance Considerations

- `Tl` uses `provide/inject` for state sharing - minimal overhead
- Column visibility toggling uses CSS classes (no re-renders)
- Drawer transitions use Vue `<Transition>` with optimized CSS
- `loadingFullTableLayout` adds a single overlay element

No special performance tuning needed for typical use cases.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Drawer doesn't open | Check `drawer.visible` binding and `useDrawer()` initialization |
| Table columns misalign | Ensure all columns have `width`; check `visibleColumns` matches column count |
| Filter not showing | Verify `TlFilter` is inside `TlMain` and `drawer` is closed |
| "More Conditions" button missing | `TlFilterSecond` requires `TlFilter` parent with no `TlFilterLeft` child |
| Nested drawer doesn't work | Ensure nested `Tl` is inside `TlDrawer` of parent `Tl` |
| Buttons not fixed at bottom | Check `buttonsPosition="fixed"` and drawer content height exceeds viewport |

---

## Version History

| Version | Changes |
|---------|---------|
| 2.0.20 | Initial documented version |
| Future | See `common/unity-plus/packages/table-layout/CHANGELOG.md` |

---

**Related**: [CRUD Generator Overview](../overview.md) | [Code Patterns](../patterns.md)
