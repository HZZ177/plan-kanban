<template>
  <div v-if="files.length" class="tabs-row">
    <button
      v-for="file in files"
      :key="file.path"
      class="tab-btn"
      :class="{ active: file.path === activeFile }"
      :disabled="!file.exists"
      :title="file.path"
      type="button"
      @click="$emit('select', file.path)"
    >
      {{ formatFileLabel(file) }}
    </button>
  </div>
</template>

<script setup>
const formatFileLabel = (file) => file.name || file.path.split(/[\\/]/).pop() || file.path

defineProps({
  files: {
    type: Array,
    required: true,
  },
  activeFile: {
    type: String,
    default: '',
  },
})

defineEmits(['select'])
</script>

<style scoped>
.tabs-row {
  display: flex;
  gap: 6px;
  padding: 10px 14px 0;
  border-bottom: 1px solid #ddddda;
  background: #fafaf9;
  flex-wrap: wrap;
}

.tab-btn {
  min-height: 32px;
  max-width: 220px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-bottom: 0;
  border-radius: 8px 8px 0 0;
  background: #f2f3f5;
  color: #62666e;
  font-size: 12px;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.tab-btn.active {
  background: #ffffff;
  color: #232427;
}

.tab-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.tab-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}
</style>
