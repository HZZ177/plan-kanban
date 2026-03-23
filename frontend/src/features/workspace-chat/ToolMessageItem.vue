<template>
  <div class="message-item tool">
    <div class="message-head">
      <span>{{ label }}</span>
      <span>{{ time }}</span>
    </div>
    <div class="message-body">{{ content }}</div>
    <div class="tool-output">{{ output }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: '',
  },
  time: {
    type: String,
    default: '',
  },
  content: {
    type: String,
    default: '',
  },
  output: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.message-item {
  min-width: 0;
  max-width: 100%;
  padding: 10px;
  border: 1px dashed #ddddda;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
}

.message-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
  font-size: 11px;
  color: #94979d;
}

.message-body,
.tool-output {
  min-width: 0;
  max-width: 100%;
  font-size: 12px;
  line-height: 1.7;
  color: #4f535b;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.tool-output {
  margin-top: 8px;
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fafafc;
  font-family: Consolas, 'SFMono-Regular', monospace;
  overflow-x: auto;
}
</style>
