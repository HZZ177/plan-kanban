<template>
  <div class="user-row">
    <div class="user-bubble">
      <div class="user-body">
        {{ content }}
      </div>
      <div class="user-meta">
        <span>{{ label }}</span>
        <span>{{ time }}</span>
      </div>
    </div>
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
.user-row {
  display: flex;
  justify-content: flex-end;
  margin: 10px 0 14px;
}

.user-bubble {
  max-width: min(70%, 720px);
  min-width: 0;
  padding: 12px 16px;
  border-radius: 18px 18px 6px 18px;
  background: #edf3ff;
  border: 1px solid #d5e3ff;
  color: #1f2937;
  display: grid;
  gap: 8px;
}

.user-body {
  min-width: 0;
  font-size: 13px;
  line-height: 1.75;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.user-meta {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  font-size: 11px;
  color: #8a93a0;
}
</style>
