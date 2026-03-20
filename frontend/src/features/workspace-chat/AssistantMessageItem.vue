<template>
  <div class="message-item">
    <div class="message-head"><span>{{ label }}</span><span>{{ time }}</span></div>
    <div class="message-body">{{ content }}</div>
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
})
</script>

<style scoped>
.message-item {
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fbfbfc;
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

.message-body {
  font-size: 12px;
  line-height: 1.7;
  color: #4f535b;
  white-space: pre-wrap;
}
</style>
