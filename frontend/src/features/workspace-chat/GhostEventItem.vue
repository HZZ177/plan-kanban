<template>
  <div class="ghost-wrap">
    <div
      class="tool-trigger"
      @click="toggleExpanded"
    >
      <span
        class="tool-trigger-icon"
        :class="{ expanded }"
      >
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
        >
          <path
            d="M4.5 2.5L8 6L4.5 9.5"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </span>
      <span class="tool-trigger-label">
        <template v-if="kind === 'thinking'">
          <span
            class="tool-trigger-text"
            :class="streaming ? 'ghost-pulse' : 'ghost-text'"
          >
            {{ streaming ? '正在思考' : '思考过程' }}
          </span>
        </template>
        <template v-else-if="kind === 'summary'">
          <span class="tool-trigger-text ghost-text">本轮执行摘要</span>
        </template>
        <template v-else>
          <span
            class="tool-trigger-text"
            :class="streaming ? 'ghost-pulse' : 'ghost-text'"
          >
            {{ triggerText }}
          </span>
          <span
            v-if="statusText"
            class="tool-badge"
            :class="statusClass"
          >
            {{ statusText }}
          </span>
        </template>
      </span>
      <span class="tool-trigger-time">{{ time }}</span>
    </div>

    <transition name="fold">
      <div
        v-if="expanded"
        class="tool-detail"
      >
        <div
          v-if="displayContent"
          class="tool-detail-section"
        >
          <div class="tool-detail-label">
            内容
          </div>
          <pre class="tool-detail-code">{{ displayContent }}</pre>
        </div>
        <div
          v-if="toolInputText"
          class="tool-detail-section"
        >
          <div class="tool-detail-label">
            入参
          </div>
          <pre class="tool-detail-code">{{ toolInputText }}</pre>
        </div>
        <div
          v-if="toolResultText"
          class="tool-detail-section"
        >
          <div class="tool-detail-label">
            结果
          </div>
          <pre class="tool-detail-code">{{ toolResultText }}</pre>
        </div>
        <div
          v-if="toolErrorText"
          class="tool-detail-section"
        >
          <div class="tool-detail-label label-error">
            错误
          </div>
          <pre class="tool-detail-code code-error">{{ toolErrorText }}</pre>
        </div>
        <div
          v-if="summaryRows.length"
          class="tool-detail-section"
        >
          <div class="tool-detail-label">
            摘要
          </div>
          <div class="summary-grid">
            <div
              v-for="row in summaryRows"
              :key="row.label"
              class="summary-row"
            >
              <span class="summary-label">{{ row.label }}</span>
              <span class="summary-value">{{ row.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  title: {
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
  kind: {
    type: String,
    default: 'event',
  },
  payload: {
    type: [Object, Array, String, Number, Boolean],
    default: null,
  },
  defaultExpanded: {
    type: Boolean,
    default: false,
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

const expanded = ref(props.defaultExpanded)

const triggerText = computed(() => {
  if (props.kind === 'tool_use') {
    return props.streaming ? `正在调用 ${props.title}` : `已调用 ${props.title}`
  }
  if (props.kind === 'tool_result') {
    return `调用 ${props.title}`
  }
  return props.title || '事件'
})

const statusText = computed(() => {
  if (props.kind === 'tool_use') {
    if (props.streaming) {
      return ''
    }
    if (toolErrorText.value) {
      return '失败'
    }
    return '完成'
  }
  if (props.kind === 'tool_result') {
    return toolErrorText.value ? '失败' : '完成'
  }
  return ''
})

const statusClass = computed(() => {
  if (toolErrorText.value) {
    return 'badge-error'
  }
  return props.streaming ? 'badge-running' : 'badge-ok'
})

const displayContent = computed(() => {
  if (props.kind === 'thinking') {
    return props.content
  }
  if (props.kind === 'summary') {
    const payload = props.payload
    if (payload && typeof payload === 'object' && !Array.isArray(payload) && typeof payload.result_preview === 'string') {
      return payload.result_preview
    }
  }
  return ''
})

const toolInputText = computed(() => {
  if (!props.payload || typeof props.payload !== 'object' || Array.isArray(props.payload)) {
    return ''
  }
  if ('tool_input' in props.payload && props.payload.tool_input) {
    return JSON.stringify(props.payload.tool_input, null, 2)
  }
  return ''
})

const toolResultText = computed(() => {
  if (!props.payload || typeof props.payload !== 'object' || Array.isArray(props.payload)) {
    return ''
  }
  if ('tool_result_content' in props.payload && typeof props.payload.tool_result_content === 'string') {
    return props.payload.tool_result_content
  }
  if ('tool_result' in props.payload && props.payload.tool_result != null) {
    return typeof props.payload.tool_result === 'string'
      ? props.payload.tool_result
      : JSON.stringify(props.payload.tool_result, null, 2)
  }
  return ''
})

const toolErrorText = computed(() => {
  if (!props.payload || typeof props.payload !== 'object' || Array.isArray(props.payload)) {
    return ''
  }
  const hasError = 'tool_result_error' in props.payload ? Boolean(props.payload.tool_result_error) : false
  if (!hasError) {
    return ''
  }
  if ('tool_result_content' in props.payload && typeof props.payload.tool_result_content === 'string') {
    return props.payload.tool_result_content
  }
  if ('tool_result' in props.payload && props.payload.tool_result != null) {
    return typeof props.payload.tool_result === 'string'
      ? props.payload.tool_result
      : JSON.stringify(props.payload.tool_result, null, 2)
  }
  return '工具调用失败'
})

const summaryRows = computed(() => {
  if (props.kind !== 'summary' || !props.payload || typeof props.payload !== 'object' || Array.isArray(props.payload)) {
    return []
  }
  const payload = props.payload
  const rows = []
  if (typeof payload.subtype === 'string' && payload.subtype) {
    rows.push({ label: '结果', value: payload.subtype })
  }
  if (typeof payload.duration_ms === 'number') {
    rows.push({ label: '耗时', value: `${payload.duration_ms} ms` })
  }
  if (typeof payload.num_turns === 'number') {
    rows.push({ label: '轮次', value: String(payload.num_turns) })
  }
  if (typeof payload.stop_reason === 'string' && payload.stop_reason) {
    rows.push({ label: '停止原因', value: payload.stop_reason })
  }
  if (Array.isArray(payload.permission_denials) && payload.permission_denials.length) {
    rows.push({ label: '权限拒绝', value: `${payload.permission_denials.length} 项` })
  }
  return rows
})

const toggleExpanded = () => {
  expanded.value = !expanded.value
}
</script>

<style scoped>
.ghost-wrap {
  width: 100%;
  max-width: 88%;
  margin: 2px 0;
}

.tool-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  cursor: pointer;
  user-select: none;
  transition: opacity 200ms ease;
}

.tool-trigger:hover {
  opacity: 0.75;
}

.tool-trigger-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  color: #b0b0b0;
  transition: transform 200ms ease;
  flex-shrink: 0;
}

.tool-trigger-icon.expanded {
  transform: rotate(90deg);
}

.tool-trigger-label {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.tool-trigger-text {
  font-size: 13px;
  font-weight: 450;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tool-trigger-time {
  flex: 0 0 auto;
  font-size: 11px;
  color: #c0c0c0;
}

.ghost-text {
  color: #b0b0b0;
}

.ghost-pulse {
  color: #a0a0a0;
  animation: ghost-fade 2s ease-in-out infinite;
}

@keyframes ghost-fade {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

.tool-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.badge-ok {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
}

.badge-error {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
}

.badge-running {
  color: #eab308;
  background: rgba(234, 179, 8, 0.08);
}

.tool-detail {
  margin-left: 24px;
  padding-left: 12px;
  border-left: 1.5px solid #ebebeb;
  overflow: hidden;
}

.tool-detail-section {
  margin-bottom: 8px;
}

.tool-detail-section:last-child {
  margin-bottom: 4px;
}

.tool-detail-label {
  font-size: 11px;
  font-weight: 600;
  color: #b0b0b0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
  margin-top: 8px;
}

.tool-detail-label.label-error {
  color: #ef4444;
}

.tool-detail-code {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  max-height: 220px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  color: #6b6b6b;
  background: #fafafa;
  padding: 10px 12px;
  border-radius: 8px;
}

.code-error {
  color: #ef4444;
  background: #fef2f2;
}

.summary-grid {
  display: grid;
  gap: 6px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 12px;
}

.summary-label {
  color: #9aa0a6;
}

.summary-value {
  color: #4f535b;
  text-align: right;
}

.fold-enter-active,
.fold-leave-active {
  transition: all 0.18s ease;
}

.fold-enter-from,
.fold-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
