<template>
  <div class="message-item thinking">
    <div class="message-head"><span>{{ label }}</span><span>{{ time }}</span></div>
    <div class="message-body">
      <span class="thinking-row">
        <span>{{ content }}</span>
        <span class="thinking-dots"><span></span><span></span><span></span></span>
      </span>
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
.message-item {
  padding: 10px;
  border: 1px solid #f2df9f;
  border-radius: 8px;
  background: #fffdf7;
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
}

.thinking-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #8a6b12;
}

.thinking-dots {
  display: inline-flex;
  gap: 4px;
}

.thinking-dots span {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #d6a31d;
  opacity: 0.85;
  animation: pulseDot 1.2s infinite;
}

.thinking-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.thinking-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes pulseDot {
  0%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }

  50% {
    opacity: 1;
    transform: translateY(-1px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .thinking-dots span {
    animation: none !important;
  }
}
</style>
