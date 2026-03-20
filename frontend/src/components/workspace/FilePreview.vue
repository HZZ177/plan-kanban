<template>
  <div class="file-preview">{{ loading ? '正在加载文件内容...' : content || '当前阶段没有可读取的文件内容。' }}</div>
</template>

<script setup>
defineProps({
  content: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})
</script>

<style scoped>
.file-preview {
  padding: 12px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fcfcfc;
  color: #4c4f55;
  font-family: Consolas, 'SFMono-Regular', monospace;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>
