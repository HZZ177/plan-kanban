<template>
  <section class="context-pane" aria-label="文件查看器与摘要">
    <section class="pane-section">
      <div class="pane-pad">
        <StageChips :stage-title="stageTitle" :stage-color="stageColor" :priority="priority" :owner="owner" />
        <div class="request-title">{{ title }}</div>
        <div class="request-summary">{{ summary || '暂无摘要' }}</div>
      </div>
    </section>
    <div class="file-scroll">
      <FileList :files="files" :active-file="activeFile" @select="$emit('select-file', $event)" />
      <FilePreview :content="content" :loading="loading" />
    </div>
  </section>
</template>

<script setup>
import FileList from './FileList.vue'
import FilePreview from './FilePreview.vue'
import StageChips from './StageChips.vue'

defineProps({
  title: {
    type: String,
    default: '',
  },
  summary: {
    type: String,
    default: '',
  },
  stageTitle: {
    type: String,
    default: '',
  },
  stageColor: {
    type: String,
    default: '#4c8bf5',
  },
  priority: {
    type: String,
    default: '',
  },
  owner: {
    type: String,
    default: '',
  },
  files: {
    type: Array,
    required: true,
  },
  activeFile: {
    type: String,
    default: '',
  },
  content: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select-file'])
</script>

<style scoped>
.context-pane {
  min-height: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #ddddda;
  background: #fafaf9;
}

.pane-section {
  flex: 0 0 auto;
  border-bottom: 1px solid #ddddda;
  background: #ffffff;
}

.pane-pad {
  padding: 12px 14px;
}

.request-title {
  margin-bottom: 8px;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.45;
  letter-spacing: -0.02em;
  color: #232427;
}

.request-summary {
  font-size: 13px;
  line-height: 1.65;
  color: #6f7279;
}

.file-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  padding: 12px 14px 14px;
  background: #ffffff;
}

@media (max-width: 1100px) {
  .context-pane {
    border-right: 0;
    border-bottom: 1px solid #ddddda;
  }
}
</style>

