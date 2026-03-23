<template>
  <section
    class="context-pane"
    aria-label="文件查看器与摘要"
  >
    <section class="pane-section">
      <div class="summary-row">
        <div class="summary-preview">
          {{ summaryText }}
        </div>
        <button
          class="summary-toggle"
          type="button"
          @click="summaryModalOpen = true"
        >
          查看摘要
        </button>
      </div>
    </section>
    <div class="file-scroll">
      <FileList
        :files="files"
        :active-file="activeFile"
        @select="$emit('select-file', $event)"
      />
      <FilePreview
        :file-path="activeFile"
        :content="content"
        :loading="loading"
        :deferred="workspace.heavyRenderDeferred || workspace.dragging"
      />
    </div>
    <Transition name="summary-modal-fade">
      <div
        v-if="summaryModalOpen"
        class="summary-modal-mask"
        @click="closeSummaryModal"
      >
        <div
          class="summary-modal-shell"
          role="dialog"
          aria-modal="true"
          aria-label="需求摘要"
          @click.stop
        >
          <div class="summary-modal">
            <div class="summary-modal-header">
              <div class="summary-modal-heading">
                <div class="summary-modal-title">
                  需求摘要
                </div>
                <div class="summary-modal-subtitle">
                  {{ title || '未命名需求' }}
                </div>
              </div>
            </div>
            <div class="summary-modal-body">
              <div class="summary-markdown markdown-body">
                <IncremarkContent
                  :content="summaryText"
                  :is-finished="true"
                />
              </div>
            </div>
            <div class="summary-modal-footer">
              <button
                class="summary-footer-btn"
                type="button"
                @click="closeSummaryModal"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import { IncremarkContent } from '@incremark/vue'
import '@incremark/theme/styles.css'
import FileList from './FileList.vue'
import FilePreview from './FilePreview.vue'

const workspace = useWorkspaceStore()

const props = defineProps({
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

const summaryModalOpen = ref(false)
const summaryText = computed(() => props.summary || '暂无摘要')

const closeSummaryModal = () => {
  summaryModalOpen.value = false
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    closeSummaryModal()
  }
}

watch(summaryModalOpen, (open) => {
  if (open) {
    document.addEventListener('keydown', handleKeydown)
    return
  }
  document.removeEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})
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
  border-bottom: 1px solid #e2e1dc;
  background: #ffffff;
}

.summary-row {
  min-height: 44px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-preview {
  flex: 1;
  min-width: 0;
  color: #6f7279;
  font-size: 12px;
  line-height: 1.6;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.summary-toggle,
.summary-modal-close,
.summary-footer-btn {
  flex: 0 0 auto;
  min-height: 28px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 7px;
  background: #ffffff;
  color: #53575e;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 180ms ease, border-color 180ms ease, color 180ms ease;
}

.summary-toggle:hover,
.summary-modal-close:hover,
.summary-footer-btn:hover {
  background: #f6f6f4;
  border-color: #d3d3cf;
}

.file-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  padding: 10px 12px 12px;
  background: #ffffff;
}

.summary-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(15, 23, 42, 0.32);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.summary-modal-shell {
  width: min(800px, 100%);
  height: min(76vh, 720px);
}

.summary-modal {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddddda;
  border-radius: 12px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.14);
}

.summary-modal-header {
  flex: 0 0 auto;
  min-height: 56px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  border-bottom: 1px solid #e7e6e2;
  background: #fafaf9;
}

.summary-modal-heading {
  min-width: 0;
}

.summary-modal-title {
  color: #2f3237;
  font-size: 15px;
  font-weight: 600;
}

.summary-modal-subtitle {
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #7a7e85;
  font-size: 12px;
}

.summary-modal-body {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 16px;
  background: #ffffff;
}

.summary-modal-body::-webkit-scrollbar {
  width: 10px;
}

.summary-modal-body::-webkit-scrollbar-thumb {
  border: 2px solid transparent;
  border-radius: 999px;
  background: rgba(120, 124, 132, 0.28);
  background-clip: padding-box;
}

.summary-modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.summary-modal-footer {
  flex: 0 0 auto;
  min-height: 48px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #e7e6e2;
  background: #fafaf9;
}


.summary-markdown {
  max-width: 720px;
  color: #4c4f55;
  font-size: 13px;
  line-height: 1.75;
}

.summary-markdown :deep(*) {
  box-sizing: border-box;
}

.summary-markdown :deep(p:first-child) {
  margin-top: 0;
}

.summary-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.summary-markdown :deep(pre) {
  overflow-x: auto;
  padding: 10px 12px;
  border: 1px solid #e7e6e2;
  border-radius: 8px;
  background: #f7f7f5;
}

.summary-markdown :deep(code) {
  font-family: Consolas, 'SFMono-Regular', monospace;
}

.summary-markdown :deep(blockquote) {
  margin-left: 0;
  padding-left: 12px;
  border-left: 3px solid #ddddda;
  color: #666b73;
}

.summary-markdown :deep(ul),
.summary-markdown :deep(ol) {
  padding-left: 20px;
}

.summary-toggle:focus-visible,
.summary-modal-close:focus-visible,
.summary-footer-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.22);
  outline-offset: 1px;
}

.summary-modal-fade-enter-active,
.summary-modal-fade-leave-active {
  transition: opacity 180ms ease;
}

.summary-modal-fade-enter-active .summary-modal-shell,
.summary-modal-fade-leave-active .summary-modal-shell {
  transition: transform 200ms ease, opacity 200ms ease;
}

.summary-modal-fade-enter-from,
.summary-modal-fade-leave-to {
  opacity: 0;
}

.summary-modal-fade-enter-from .summary-modal-shell,
.summary-modal-fade-leave-to .summary-modal-shell {
  opacity: 0;
  transform: translateY(10px);
}

@media (prefers-reduced-motion: reduce) {
  .summary-toggle,
  .summary-modal-close,
  .summary-footer-btn,
  .summary-modal-fade-enter-active,
  .summary-modal-fade-leave-active,
  .summary-modal-fade-enter-active .summary-modal-shell,
  .summary-modal-fade-leave-active .summary-modal-shell {
    transition: none;
  }
}

@media (max-width: 1100px) {
  .context-pane {
    border-right: 0;
    border-bottom: 1px solid #ddddda;
  }
}

@media (max-width: 768px) {
  .summary-row {
    padding: 6px 10px;
    align-items: flex-start;
  }

  .file-scroll {
    padding: 10px;
  }

  .summary-modal-mask {
    padding: 12px;
  }

  .summary-modal-shell {
    height: min(82vh, 720px);
  }

  .summary-modal-header,
  .summary-modal-footer {
    padding: 0 12px;
  }

  .summary-modal-body {
    padding: 14px 12px 16px;
  }
}
</style>
