# CRUD Generator Limitations

This document outlines the known limitations of the CRUD Generator and scenarios that require manual developer intervention.

## Unsupported Features

The CRUD Generator cannot handle the following scenarios out of the box:

### Complex Forms
- **Dynamic form fields** - Forms with fields that can be added/removed dynamically
- **Nested object forms** - Form fields for nested objects like `user.name` or `address.city`
- **Complex form logic** - Requires manual implementation of custom form behavior

### Custom Components
- **Only predefined components** - Generator only uses components from `componentMap` in `src/components/Form/data.ts`
- **Custom UI components** - Any component not in the predefined map requires manual code modification

### Advanced Table Features
- **Inline row editing** - Editing directly within table rows
- **Drag-and-drop sorting** - Reordering rows via drag-and-drop
- **Multi-level headers** - Complex column headers with multiple levels
- **Tree tables** - Hierarchical data display with expandable rows
- **Batch operations** - Bulk delete, bulk export, or other multi-select operations

### Advanced Search
- **Complex search conditions** - Beyond simple field matching (e.g., date ranges, OR conditions)
- **Dynamic search forms** - Search form that changes based on selections
- **Multi-condition combinations** - Requires manual extension of search logic

### Validation & Dependencies
- **Custom validation rules** - Only `required` validation is generated; regex, custom functions need manual addition
- **Field dependencies/linkage** - Cascading selects (e.g., province → city) require manual `watch` implementation

## Manual Modification Required

After generation, the following scenarios require developer attention:

### Type Definitions
**Critical**: Type definition files must be created in the API module directory, NOT in `src/api/types/`.

```
✅ Correct: src/api/[module]/type.d.ts
❌ Wrong: src/api/types/
```

Create namespace-based types matching your actual API response structure:
```typescript
// src/api/agent/type.d.ts
declare namespace AgentGetTableType {
  interface InParams { /* ... */ }
  interface Req { /* ... */ }
  interface Res { /* ... */ }
  interface record { /* ... */ }
}
```

### Data Dictionaries & Enums
Define options for Select components and other enum-based fields:
```typescript
// In data.ts or src/utils/enum.ts
export const statusOptions = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 },
];
```

### Route Registration
Add generated pages to your router configuration with proper meta information, including permissions if needed.

### File Upload Configuration
Configure Upload component props in `componentProps`:
```typescript
{
  component: 'UploadFilePro',
  componentProps: {
    packageName: 'your-module',  // Required: upload package name
    isSecurity: true,            // Optional: security scan
    multiple: false,             // Optional: allow multiple files
  }
}
```

### Multi-Select Association Conversion
For multi-select fields (e.g., `mode: 'multiple'`), handle array value conversion between API and form:
```typescript
// Manual conversion needed for array values
const modelRef = reactive<{ projectIds: number[] }>({ projectIds: [] });
```

### Custom Table Column Rendering
For images, rich text, or custom cell content, add `bodyCell` slot logic:
```vue
<template #bodyCell="{ column: { dataIndex }, record }">
  <template v-if="dataIndex === 'avatar'">
    <a-image :src="record.avatar" />
  </template>
</template>
```

### Permission Control
Add button-level visibility checks using route meta permissions or custom logic:
```vue
<ActionGroup>
  <a-button v-if="hasPermission('agent:edit')" type="link">编辑</a-button>
</ActionGroup>
```

### Form Layout Customization
Modify `schemas` configuration for multi-column layouts, field grouping, or custom form structure.

### API Implementation
Generated code references API methods (e.g., `AgentApi.agentGetTable`) but does not create the actual backend endpoints. Implement these in your API layer.

## Critical Reminders

### API Response Format Assumptions
The generator assumes these API response formats:

**Single record operations** (create, update, detail):
```typescript
{ code: 200, data: T, message: string }
```

**List operations**:
```typescript
{ records: T[], total: number }
```

Adjust generated code if your API uses different field names.

### CommonRes Type Usage
- Use `CommonRes<T>` directly, NOT `Promise<CommonRes<T>>`
- The project's `CommonRes` is already typed as a Promise in `global.d.ts`
- Example: `const { data } = await AgentApi.method()` where `data` is `CommonRes<T>`

### Type Definition Placement
Always place type definitions in the same directory as the API implementation:
```
src/api/
├── agent/
│   ├── index.ts        # API methods
│   └── type.d.ts       # Types for this module ✅
└── demo/
    ├── index.ts
    └── type.d.ts
```

### Generated Code is a Template
The output provides a solid foundation but requires adaptation to your specific business requirements. Always review and test generated code before deployment.

## Related Documentation

- For parameter reference: See `parameters.md`
- For usage examples: See `examples.md`
- For error handling patterns: See `error-handling.md`
- For extending the generator: See `patterns.md`
