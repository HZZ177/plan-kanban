<template>
  <div class="file-list">
    <button
      v-for="file in files"
      :key="file.path"
      class="file-item"
      :class="{ active: file.path === activeFile, missing: !file.exists }"
      :disabled="!file.exists"
      type="button"
      @click="$emit('select', file.path)"
    >
      <span>{{ file.name }}</span>
      <small v-if="!file.exists">未生成</small>
    </button>
  </div>
</template>

<script setup>
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
.file-list {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.file-item {
  width: 100%;
  text-align: left;
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fafafc;
  font-size: 12px;
  color: #4f535b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.file-item.active {
  background: #f7fbff;
  border-color: #c8ddff;
  color: #2e5fbf;
}

.file-item.missing {
  color: #94979d;
  cursor: not-allowed;
}

.file-item:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}
</style>
