<template>
  <div class="chat-head">
    <button v-if="canCycle" class="ghost-btn" type="button" @click="$emit('history')">{{ historyLabel }}</button>
    <div v-else class="history-state">{{ historyLabel }}</div>
  </div>
</template>

<script setup>
defineProps({
  canCycle: {
    type: Boolean,
    default: false,
  },
  historyLabel: {
    type: String,
    default: '暂无会话',
  },
})

defineEmits(['history'])
</script>

<style scoped>
.chat-head {
  flex: 0 0 auto;
  padding: 10px 14px;
  border-bottom: 1px solid #ddddda;
  display: flex;
  justify-content: flex-end;
  background: #ffffff;
}

.ghost-btn,
.history-state {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  font-size: 12px;
}

.ghost-btn {
  border: 1px solid #ddddda;
  background: #ffffff;
  color: #53575e;
  cursor: pointer;
}

.history-state {
  border: 1px solid #eeeeeb;
  background: #f7f7f5;
  color: #7a7e85;
}

.ghost-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}
</style>

