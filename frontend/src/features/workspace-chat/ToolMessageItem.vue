<template>
  <div class="message-item tool">
    <div class="message-head"><span>{{ label }}</span><span>{{ time }}</span></div>
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
  padding: 10px;
  border: 1px dashed #ddddda;
  border-radius: 8px;
  background: #ffffff;
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
  font-size: 12px;
  line-height: 1.7;
  color: #4f535b;
  white-space: pre-wrap;
}

.tool-output {
  margin-top: 8px;
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fafafc;
  font-family: Consolas, 'SFMono-Regular', monospace;
}
</style>
