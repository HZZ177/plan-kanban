<template>
  <div v-if="sessions.length" class="history-list">
    <button
      v-for="session in sessions"
      :key="session.id"
      class="history-item"
      :class="{ active: session.id === activeSessionId }"
      type="button"
      @click="$emit('select', session.id)"
    >
      <span class="history-type">{{ formatSessionType(session.session_type) }}</span>
      <span class="history-time">{{ formatTime(session.started_at) }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  sessions: {
    type: Array,
    default: () => [],
  },
  activeSessionId: {
    type: String,
    default: '',
  },
})

defineEmits(['select'])

const formatTime = (value) => {
  if (!value) {
    return '未知时间'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '未知时间'
  }
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

const formatSessionType = (type) => {
  if (type === 'conversation') {
    return '普通对话'
  }
  if (type === 'skill_execute_issues') {
    return '开发执行'
  }
  if (type === 'skill_plan') {
    return '执行合同'
  }
  if (type === 'acceptance_review') {
    return '验收复核'
  }
  return type
}
</script>

<style scoped>
.history-list {
  display: grid;
  gap: 8px;
}

.history-item {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  cursor: pointer;
  color: #4f535b;
  font-size: 12px;
}

.history-item.active {
  border-color: #c8ddff;
  background: #f7fbff;
  color: #2e5fbf;
}

.history-type {
  font-weight: 600;
}

.history-time {
  color: #8a8e96;
}
</style>
