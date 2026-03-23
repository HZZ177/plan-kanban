<template>
  <div class="result-card">
    <div v-if="hasBody" class="result-block">
      <div class="section-title">运行摘要</div>
      <div class="result-body">{{ body }}</div>
    </div>

    <div v-if="acceptanceSummary" class="result-block">
      <div class="section-title">验收摘要</div>
      <div class="result-body">
        当前状态：{{ acceptanceSummary.acceptance_substate || '未设置' }}
        <template v-if="acceptanceSummary.runtime">
          · 总计 {{ acceptanceSummary.runtime.total }} / 已完成 {{ acceptanceSummary.runtime.completed }} / 失败 {{ acceptanceSummary.runtime.failed }} / 阻塞 {{ acceptanceSummary.runtime.blocked }}
        </template>
      </div>
    </div>

    <div v-if="canEditAcceptanceSubstate || diffFiles.length || selectedDiff" class="acceptance-box">
      <div v-if="canEditAcceptanceSubstate" class="acceptance-section">
        <div class="section-title">验收状态</div>
        <AcceptanceSubstateEditor :value="acceptanceSummary?.acceptance_substate || ''" @change="$emit('change-substate', $event)" />
      </div>

      <div v-if="diffFiles.length" class="acceptance-section">
        <div class="section-title">变更文件</div>
        <DiffFileList :files="diffFiles" :active-path="selectedDiff?.path || ''" @select="$emit('select-diff', $event)" />
      </div>

      <div v-if="selectedDiff" class="acceptance-section">
        <div class="section-title">Diff 预览</div>
        <div class="diff-path">{{ selectedDiff.path }}</div>
        <div v-if="selectedDiff.summary" class="diff-summary">{{ selectedDiff.summary }}</div>
        <pre>{{ selectedDiff.diff }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import AcceptanceSubstateEditor from './AcceptanceSubstateEditor.vue'
import DiffFileList from './DiffFileList.vue'

defineProps({
  body: {
    type: String,
    default: '',
  },
  hasBody: {
    type: Boolean,
    default: false,
  },
  processState: {
    type: Object,
    default: null,
  },
  acceptanceSummary: {
    type: Object,
    default: null,
  },
  diffFiles: {
    type: Array,
    default: () => [],
  },
  selectedDiff: {
    type: Object,
    default: null,
  },
  canEditAcceptanceSubstate: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select-diff', 'change-substate'])
</script>

<style scoped>
.result-card {
  display: grid;
  gap: 12px;
}

.result-block,
.acceptance-box {
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #dde5ef;
  display: grid;
  gap: 8px;
}

.acceptance-section {
  display: grid;
  gap: 8px;
}

.acceptance-section + .acceptance-section {
  padding-top: 8px;
  border-top: 1px solid #e6edf5;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: #3b4d63;
}

.result-body,
.diff-summary {
  font-size: 12px;
  line-height: 1.7;
  color: #46607f;
}

.diff-path {
  font-size: 12px;
  color: #355a9c;
}

pre {
  margin: 0;
  padding: 10px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #d7e1ee;
  color: #445569;
  font-size: 11px;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
