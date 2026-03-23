<template>
  <div class="workspace-header">
    <div class="workspace-main">
      <span
        v-if="stageTitle"
        class="stage-badge"
      >
        {{ stageTitle }}
      </span>
      <div class="workspace-title">
        {{ title || '未选择需求' }}
      </div>
      <div class="workspace-meta">
        <span
          v-if="priority"
          class="meta-item"
        >
          {{ priority }}
        </span>
        <span
          v-if="owner"
          class="meta-item"
        >
          {{ owner }}
        </span>
        <span class="meta-item">
          文件数: {{ fileCount }}
        </span>
      </div>
    </div>
    <div class="workspace-actions">
      <ProcessStatusBadge
        v-if="processState"
        :process-type="processState.active_process_type"
        :process-status="processState.active_process_status"
      />
      <button
        class="ghost-btn"
        type="button"
        @click="$emit('close')"
      >
        关闭
      </button>
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
  priority: {
    type: String,
    default: '',
  },
  owner: {
    type: String,
    default: '',
  },
  fileCount: {
    type: Number,
    default: 0,
  },
})

defineEmits(['close'])
</script>

<style scoped>
.workspace-header {
  flex: 0 0 auto;
  min-height: 40px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-bottom: 1px solid #e2e1dc;
  background: #fafaf9;
}

.workspace-main {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.stage-badge {
  flex: 0 0 auto;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-height: 24px;
  padding: 0 8px;
  border: 1px solid #e1dfda;
  border-radius: 999px;
  background: #f3f2ef;
  color: #6b7078;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
}

.workspace-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: #34373d;
}

.workspace-meta {
  flex: 0 1 auto;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.meta-item {
  flex: 0 0 auto;
  min-height: 22px;
  padding: 0 7px;
  border-radius: 999px;
  background: #f1f2f4;
  color: #686d75;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  white-space: nowrap;
}

.workspace-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ghost-btn {
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 7px;
  background: #ffffff;
  color: #53575e;
  font-size: 12px;
  cursor: pointer;
}

.ghost-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.22);
  outline-offset: 1px;
}

@media (max-width: 900px) {
  .workspace-meta {
    display: none;
  }
}

@media (max-width: 768px) {
  .workspace-header {
    padding: 0 10px;
  }

  .stage-badge {
    max-width: 96px;
  }
}
</style>
