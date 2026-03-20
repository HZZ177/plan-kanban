<template>
  <div class="workspace-header">
    <div class="workspace-title-wrap">
      <div class="workspace-title">{{ stageTitle }}</div>
      <div class="workspace-subtitle">{{ title }}</div>
    </div>
    <div class="workspace-actions">
      <ProcessStatusBadge
        v-if="processState"
        :process-type="processState.active_process_type"
        :process-status="processState.active_process_status"
      />
      <button class="ghost-btn" type="button" @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script setup>
import ProcessStatusBadge from './ProcessStatusBadge.vue'

defineProps({
  processState: {
    type: Object,
    default: null,
  },
  stageTitle: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
})

defineEmits(['close'])
</script>

<style scoped>
.workspace-header {
  flex: 0 0 auto;
  min-height: 44px;
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid #ddddda;
  background: #fafaf9;
}

.workspace-title-wrap {
  min-width: 0;
}

.workspace-title {
  margin-bottom: 2px;
  font-size: 12px;
  color: #94979d;
}

.workspace-subtitle {
  overflow: hidden;
  font-size: 13px;
  font-weight: 600;
  color: #44474d;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.workspace-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ghost-btn {
  min-height: 34px;
  padding: 0 12px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  color: #53575e;
  cursor: pointer;
}

.ghost-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}
</style>
