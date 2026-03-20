<template>
  <div v-if="label" class="process-badge" :class="statusClass">
    <span class="process-dot"></span>
    <span>{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  processType: {
    type: String,
    default: '',
  },
  processStatus: {
    type: String,
    default: '',
  },
})

const processTypeLabelMap = {
  conversation: '对话协作',
  skill_plan: '生成执行合同',
  skill_execute_issues: '开发执行',
}

const processStatusLabelMap = {
  idle: '待命',
  running: '执行中',
  finished: '已完成',
  failed: '失败',
}

const label = computed(() => {
  if (!props.processType || !props.processStatus) {
    return ''
  }
  const typeLabel = processTypeLabelMap[props.processType] || props.processType
  const statusLabel = processStatusLabelMap[props.processStatus] || props.processStatus
  return `${typeLabel} · ${statusLabel}`
})

const statusClass = computed(() => (props.processStatus ? `status-${props.processStatus}` : ''))
</script>

<style scoped>
.process-badge {
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #d7dbe2;
  background: #ffffff;
  color: #5a5f68;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  white-space: nowrap;
}

.process-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
}

.status-running {
  background: #edf4ff;
  border-color: #cfe0ff;
  color: #2f61c2;
}

.status-finished {
  background: #eefbf1;
  border-color: #cdeed6;
  color: #2d8a4f;
}

.status-failed {
  background: #fff1f2;
  border-color: #ffd4d7;
  color: #c33b4b;
}
</style>
