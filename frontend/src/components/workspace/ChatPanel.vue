<template>
  <section class="chat-pane" aria-label="纯对话区">
    <ActionBar :can-cycle="canCycleSessions" :history-label="historyLabel" @history="$emit('history')" />
    <div class="chat-actions" :class="{ empty: actions.length === 0 }">
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
    <div class="chat-scroll">
      <div class="chat-stack">
        <ResultCard
          v-if="hasResult || processState || canEditAcceptanceSubstate || selectedDiff || diffFiles.length"
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
    <ComposerPanel
      :model-value="composer"
      :disabled="sending"
      :submitting="sending"
      @update:modelValue="$emit('update:composer', $event)"
      @submit="$emit('submit-chat')"
    />
  </section>
</template>

<script setup>
import MessageList from '../../features/workspace-chat/MessageList.vue'
import ComposerPanel from '../../features/workspace-chat/ComposerPanel.vue'
import ActionBar from './ActionBar.vue'
import ResultCard from './ResultCard.vue'

defineProps({
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
</script>

<style scoped>
.chat-pane {
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
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
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  padding: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfbfc 100%);
}

.chat-stack {
  display: grid;
  gap: 12px;
}
</style>


