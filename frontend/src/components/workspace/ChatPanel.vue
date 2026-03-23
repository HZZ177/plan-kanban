<template>
  <section
    ref="chatPaneRef"
    class="chat-pane"
    aria-label="纯对话区"
  >
    <ActionBar
      :can-cycle="canCycleSessions"
      :history-label="historyLabel"
      @history="$emit('history')"
    />
    <div class="chat-main">
      <div
        class="chat-actions"
        :class="{ empty: actions.length === 0 }"
      >
        <button
          v-for="action in actions"
          :key="action.key"
          class="chat-action-btn"
          :class="{ primary: action.primary }"
          :disabled="action.disabled || loadingAction"
          type="button"
          @click="$emit('action', action.key)"
        >
          {{ action.label }}
        </button>
      </div>
      <div
        ref="chatScrollRef"
        class="chat-scroll"
      >
        <div class="chat-stack">
          <ResultCard
            v-if="hasResult || processState || canEditAcceptanceSubstate || selectedDiff || diffFiles.length || acceptanceSummary"
            :body="result"
            :has-body="hasResult"
            :process-state="processState"
            :acceptance-summary="acceptanceSummary"
            :diff-files="diffFiles"
            :selected-diff="selectedDiff"
            :can-edit-acceptance-substate="canEditAcceptanceSubstate"
            @select-diff="$emit('select-diff', $event)"
            @change-substate="$emit('change-substate', $event)"
          />
          <MessageList :messages="messages" />
        </div>
      </div>
    </div>
    <div
      class="composer-resizer"
      :class="{ dragging: composerDragging }"
      role="separator"
      aria-label="调整输入区高度"
      aria-orientation="horizontal"
      tabindex="0"
      @mousedown="startComposerDrag"
      @keydown="onResizerKeydown"
    />
    <div
      class="composer-shell"
      :style="{ flexBasis: `${composerHeight}px`, height: `${composerHeight}px` }"
    >
      <ComposerPanel
        :model-value="composer"
        :disabled="sending"
        :submitting="sending"
        @update:model-value="$emit('update:composer', $event)"
        @submit="$emit('submit-chat')"
      />
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import MessageList from '../../features/workspace-chat/MessageList.vue'
import ComposerPanel from '../../features/workspace-chat/ComposerPanel.vue'
import ActionBar from './ActionBar.vue'
import ResultCard from './ResultCard.vue'

const props = defineProps({
  actions: {
    type: Array,
    default: () => [],
  },
  result: {
    type: String,
    default: '',
  },
  hasResult: {
    type: Boolean,
    default: false,
  },
  messages: {
    type: Array,
    default: () => [],
  },
  composer: {
    type: String,
    default: '',
  },
  sending: {
    type: Boolean,
    default: false,
  },
  processState: {
    type: Object,
    default: null,
  },
  loadingAction: {
    type: Boolean,
    default: false,
  },
  historyLabel: {
    type: String,
    default: '暂无会话',
  },
  canCycleSessions: {
    type: Boolean,
    default: false,
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

defineEmits(['update:composer', 'submit-chat', 'action', 'history', 'select-diff', 'change-substate'])

const COMPOSER_MIN_HEIGHT = 148
const COMPOSER_MAX_HEIGHT = 420
const COMPOSER_KEYBOARD_STEP = 24
const CHAT_MAIN_MIN_HEIGHT = 180
const ACTION_BAR_RESERVE = 46
const RESIZER_HEIGHT = 10

const chatPaneRef = ref(null)
const chatScrollRef = ref(null)
const composerHeight = ref(220)
const composerDragging = ref(false)
const lastMessageSignature = computed(() => {
  const last = props.messages[props.messages.length - 1]
  if (!last) {
    return ''
  }
  return `${last.id}:${last.content?.length || 0}:${last.streaming ? '1' : '0'}`
})

let pendingHeight = composerHeight.value
let frameId = null

function isChatPinnedToBottom() {
  if (!chatScrollRef.value) {
    return false
  }
  const { scrollTop, clientHeight, scrollHeight } = chatScrollRef.value
  return scrollTop + clientHeight >= scrollHeight - 4
}

function pinChatToBottom() {
  nextTick(() => {
    if (!chatScrollRef.value) {
      return
    }
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  })
}

function applyComposerHeight(height) {
  const pinnedToBottom = isChatPinnedToBottom()
  composerHeight.value = clampComposerHeight(height)
  if (pinnedToBottom) {
    pinChatToBottom()
  }
}

function getComposerMaxHeight() {
  if (!chatPaneRef.value) {
    return COMPOSER_MAX_HEIGHT
  }
  const paneHeight = chatPaneRef.value.clientHeight || 0
  const maxByPane = paneHeight - CHAT_MAIN_MIN_HEIGHT - ACTION_BAR_RESERVE - RESIZER_HEIGHT
  return Math.max(COMPOSER_MIN_HEIGHT, Math.min(COMPOSER_MAX_HEIGHT, maxByPane))
}

function clampComposerHeight(height) {
  return Math.max(COMPOSER_MIN_HEIGHT, Math.min(height, getComposerMaxHeight()))
}

function flushComposerHeight() {
  frameId = null
  applyComposerHeight(pendingHeight)
}

function onComposerMouseMove(event) {
  if (!composerDragging.value) {
    return
  }
  pendingHeight = window.innerHeight - event.clientY
  if (frameId !== null) {
    return
  }
  frameId = requestAnimationFrame(flushComposerHeight)
}

function stopComposerDrag() {
  if (!composerDragging.value) {
    return
  }
  if (frameId !== null) {
    cancelAnimationFrame(frameId)
    frameId = null
  }
  applyComposerHeight(pendingHeight)
  composerDragging.value = false
  document.body.style.cursor = ''
}

function startComposerDrag(event) {
  composerDragging.value = true
  pendingHeight = composerHeight.value
  document.body.style.cursor = 'row-resize'
  event.preventDefault()
}

function onResizerKeydown(event) {
  if (event.key === 'ArrowUp') {
    applyComposerHeight(composerHeight.value + COMPOSER_KEYBOARD_STEP)
    pendingHeight = composerHeight.value
    event.preventDefault()
  }

  if (event.key === 'ArrowDown') {
    applyComposerHeight(composerHeight.value - COMPOSER_KEYBOARD_STEP)
    pendingHeight = composerHeight.value
    event.preventDefault()
  }
}

function syncComposerHeight() {
  applyComposerHeight(composerHeight.value)
  pendingHeight = composerHeight.value
}

function onWindowResize() {
  syncComposerHeight()
}


function scrollToBottom() {
  nextTick(() => {
    if (!chatScrollRef.value) {
      return
    }
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  })
}

watch(
  () => props.messages.length,
  () => {
    scrollToBottom()
  },
)

watch(lastMessageSignature, () => {
  const last = props.messages[props.messages.length - 1]
  if (last?.role === 'assistant') {
    scrollToBottom()
  }
})

watch(
  () => [props.actions.length, props.processState, props.acceptanceSummary, props.diffFiles.length],
  () => {
    nextTick(() => {
      syncComposerHeight()
    })
  },
)

nextTick(() => {
  syncComposerHeight()
})

window.addEventListener('mousemove', onComposerMouseMove)
window.addEventListener('mouseup', stopComposerDrag)
window.addEventListener('resize', onWindowResize)

onBeforeUnmount(() => {
  if (frameId !== null) {
    cancelAnimationFrame(frameId)
  }
  window.removeEventListener('mousemove', onComposerMouseMove)
  window.removeEventListener('mouseup', stopComposerDrag)
  window.removeEventListener('resize', onWindowResize)
})
</script>

<style scoped>
.chat-pane {
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
}

.chat-main {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-actions {
  flex: 0 0 auto;
  padding: 10px 14px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  border-bottom: 1px solid #ddddda;
  background: #fcfcfc;
}

.chat-actions.empty {
  display: none;
}

.chat-action-btn {
  min-height: 30px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 999px;
  background: #f3f4f6;
  color: #5b6068;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  cursor: pointer;
}

.chat-action-btn.primary {
  background: #edf4ff;
  border-color: #cfe0ff;
  color: #2f61c2;
}

.chat-action-btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.chat-action-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

.chat-scroll {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  padding: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfc 100%);
}

.chat-stack {
  min-width: 0;
  display: grid;
  gap: 12px;
}

.composer-resizer {
  position: relative;
  flex: 0 0 10px;
  background: #f3f4f6;
  border-top: 1px solid #ddddda;
  border-bottom: 1px solid #ddddda;
  cursor: row-resize;
  user-select: none;
}

.composer-resizer::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 3px;
  border-radius: 999px;
  background: #cfd3d8;
}

.composer-resizer:hover,
.composer-resizer.dragging {
  background: #edf2fb;
}

.composer-resizer:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: -1px;
}

.composer-shell {
  flex: 0 0 auto;
  min-height: 0;
  min-width: 0;
  overflow: hidden;
  display: flex;
}
</style>
