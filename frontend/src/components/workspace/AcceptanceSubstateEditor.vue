<template>
  <div class="acceptance-editor">
    <span class="editor-label">验收子状态</span>
    <select :value="value || ''" @change="$emit('change', $event.target.value || null)">
      <option value="">未设置</option>
      <option value="测试中">测试中</option>
      <option value="测试失败">测试失败</option>
      <option value="审查中">审查中</option>
      <option value="已验收">已验收</option>
      <option value="已打回">已打回</option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  value: {
    type: String,
    default: '',
  },
})

defineEmits(['change'])
</script>

<style scoped>
.acceptance-editor {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.editor-label {
  font-size: 12px;
  color: #60718b;
}

select {
  min-width: 160px;
  border: 1px solid #d7dbe2;
  border-radius: 8px;
  padding: 8px 10px;
  background: #ffffff;
  color: #232427;
}
</style>
