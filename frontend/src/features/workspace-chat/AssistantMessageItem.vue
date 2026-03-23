<template>
  <div
    class="assistant-entry"
    :class="{ streaming }"
  >
    <div
      v-if="content"
      class="assistant-body markdown-body"
    >
      <IncremarkContent
        :content="content"
        :is-finished="isFinished"
      />
    </div>
    <div
      v-else-if="streaming"
      class="assistant-thinking"
    >
      <span class="thinking-dot" />
      <span class="thinking-dot" />
      <span class="thinking-dot" />
    </div>
    <div class="assistant-meta">
      <span>{{ label }}</span>
      <span>{{ time }}</span>
    </div>
  </div>
</template>

<script setup>
import { IncremarkContent } from '@incremark/vue'
import '@incremark/theme/styles.css'

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
  streaming: {
    type: Boolean,
    default: false,
  },
  isFinished: {
    type: Boolean,
    default: true,
  },
})
</script>

<style scoped>
.assistant-entry {
  min-width: 0;
  max-width: min(820px, 100%);
  display: grid;
  gap: 8px;
}

.assistant-body {
  min-width: 0;
  max-width: 100%;
  font-size: 13px;
  line-height: 1.8;
  color: #1f2937;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.assistant-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: #9aa0a6;
}

.markdown-body :deep(*) {
  box-sizing: border-box;
  max-width: 100%;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(pre) {
  max-width: 100%;
  overflow-x: auto;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f5f7fa;
  border: 1px solid #e5e7eb;
}

.markdown-body :deep(code) {
  font-family: Consolas, 'SFMono-Regular', monospace;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 18px;
}

.assistant-thinking {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  min-height: 22px;
}

.thinking-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: #8fa4c5;
  animation: blink 1.2s infinite ease-in-out;
}

.thinking-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.thinking-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-1px);
  }
}
</style>
