<template>
  <div class="file-preview">
    <template v-if="loading">
      <div class="file-preview-empty">
        正在加载文件内容...
      </div>
    </template>
    <template v-else-if="deferred">
      <div class="file-preview-skeleton" aria-hidden="true">
        <div class="skeleton-line long"></div>
        <div class="skeleton-line mid"></div>
        <div class="skeleton-line short"></div>
        <div class="skeleton-block"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line mid"></div>
      </div>
    </template>
    <template v-else-if="!content">
      <div class="file-preview-empty">
        当前阶段没有可读取的文件内容。
      </div>
    </template>
    <template v-else-if="isMarkdownFile">
      <div
        ref="markdownContainerRef"
        class="markdown-body"
        @click="handleMarkdownClick"
      >
        <IncremarkContent
          :content="content"
          :is-finished="true"
        />
      </div>
    </template>
    <template v-else>
      <pre class="plain-body">{{ content }}</pre>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { IncremarkContent } from '@incremark/vue'
import '@incremark/theme/styles.css'

const props = defineProps({
  filePath: {
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
  deferred: {
    type: Boolean,
    default: false,
  },
})

const markdownContainerRef = ref(null)
const isMarkdownFile = computed(() => /\.(md|markdown)$/i.test(props.filePath || ''))

function normalizeAnchor(value) {
  return decodeURIComponent(String(value || ''))
    .trim()
    .toLowerCase()
    .replace(/[\s_]+/g, '-')
    .replace(/[^\w\-\u4e00-\u9fa5]+/g, '')
}

function buildHeadingIdMap() {
  const container = markdownContainerRef.value
  if (!container) {
    return
  }
  const usedIds = new Set()
  const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6')
  headings.forEach((heading) => {
    const sourceText = heading.textContent || ''
    const baseId = normalizeAnchor(sourceText) || 'section'
    let nextId = baseId
    let index = 1
    while (usedIds.has(nextId)) {
      nextId = `${baseId}-${index}`
      index += 1
    }
    usedIds.add(nextId)
    heading.id = nextId
    heading.setAttribute('data-anchor-id', nextId)
  })
}

function findAnchorTarget(anchor) {
  const container = markdownContainerRef.value
  if (!container) {
    return null
  }
  const normalized = normalizeAnchor(anchor)
  if (!normalized) {
    return null
  }

  const direct = container.querySelector(`#${CSS.escape(normalized)}`)
  if (direct) {
    return direct
  }

  const byDataAnchor = Array.from(container.querySelectorAll('[data-anchor-id]')).find(
    (item) => normalizeAnchor(item.getAttribute('data-anchor-id')) === normalized,
  )
  if (byDataAnchor) {
    return byDataAnchor
  }

  const byName = Array.from(container.querySelectorAll('[name]')).find(
    (item) => normalizeAnchor(item.getAttribute('name')) === normalized,
  )
  if (byName) {
    return byName
  }

  const headingMatch = Array.from(container.querySelectorAll('h1, h2, h3, h4, h5, h6')).find(
    (item) => normalizeAnchor(item.textContent || '') === normalized,
  )
  return headingMatch || null
}

function handleMarkdownClick(event) {
  const target = event.target instanceof Element ? event.target.closest('a') : null
  if (!target) {
    return
  }
  const href = target.getAttribute('href') || ''
  if (!href.startsWith('#')) {
    return
  }
  const anchor = href.slice(1)
  const destination = findAnchorTarget(anchor)
  if (!destination) {
    return
  }
  event.preventDefault()
  destination.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch(
  () => [props.content, props.filePath, props.loading, props.deferred],
  async () => {
    if (!isMarkdownFile.value || props.loading || props.deferred || !props.content) {
      return
    }
    await nextTick()
    buildHeadingIdMap()
  },
  { immediate: true },
)
</script>

<style scoped>
.file-preview {
  padding: 12px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #fcfcfc;
  color: #4c4f55;
  font-size: 12px;
  line-height: 1.7;
}

.file-preview-empty {
  white-space: pre-wrap;
}

.file-preview-skeleton {
  min-height: 160px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line,
.skeleton-block {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
  background: #f0f1f3;
}

.skeleton-line::after,
.skeleton-block::after {
  content: '';
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.75) 50%, transparent 100%);
  animation: skeleton-shimmer 1.2s ease infinite;
}

.skeleton-line {
  height: 12px;
}

.skeleton-line.long {
  width: 92%;
}

.skeleton-line.mid {
  width: 76%;
}

.skeleton-line.short {
  width: 48%;
}

.skeleton-block {
  width: 100%;
  height: 54px;
  margin: 4px 0;
}

.plain-body {
  margin: 0;
  color: #4c4f55;
  font-family: Consolas, 'SFMono-Regular', monospace;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.markdown-body :deep(*) {
  box-sizing: border-box;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(pre) {
  overflow-x: auto;
  padding: 10px;
  border-radius: 8px;
  background: #f3f4f6;
}

.markdown-body :deep(code) {
  font-family: Consolas, 'SFMono-Regular', monospace;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 18px;
}

@keyframes skeleton-shimmer {
  100% {
    transform: translateX(100%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton-line::after,
  .skeleton-block::after {
    animation: none;
  }
}
</style>
