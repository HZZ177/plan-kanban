<template>
  <div v-if="files.length" class="diff-list">
    <button
      v-for="file in files"
      :key="file.path"
      class="diff-item"
      :class="{ active: file.path === activePath }"
      type="button"
      @click="$emit('select', file.path)"
    >
      {{ file.name || file.path }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  files: {
    type: Array,
    default: () => [],
  },
  activePath: {
    type: String,
    default: '',
  },
})

defineEmits(['select'])
</script>

<style scoped>
.diff-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.diff-item {
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #d9e7ff;
  border-radius: 999px;
  background: #ffffff;
  color: #46607f;
  font-size: 12px;
  cursor: pointer;
}

.diff-item.active {
  background: #edf4ff;
  border-color: #cfe0ff;
  color: #2f61c2;
}
</style>
