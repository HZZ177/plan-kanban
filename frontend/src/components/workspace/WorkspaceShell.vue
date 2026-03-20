<template>
  <div class="main" :class="{ expanded: workspace.expanded }" :style="workspace.expanded ? { '--workspace-width': `${workspace.width}px` } : undefined">
    <section class="board-area" aria-label="业务阶段看板">
      <BoardScrollContainer />
    </section>
    <SplitterHandle v-if="workspace.expanded" />
    <aside v-if="workspace.expanded" class="workspace-shell" aria-label="阶段工作区">
      <WorkspaceHeader :stage-title="activeStage?.title ?? ''" :title="activeCard?.title ?? ''" :process-state="store.activeProcessState" @close="closeWorkspace" />
      <div class="workspace-grid">
        <ContextPane
          :title="activeCard?.title ?? ''"
          :summary="activeCard?.summary ?? ''"
          :stage-title="activeStage?.title ?? ''"
          :stage-color="activeStage?.color ?? '#4c8bf5'"
          :priority="activeCard?.priority ?? ''"
          :owner="activeCard?.owner ?? ''"
          :files="store.stageFiles"
          :active-file="store.selectedFilePath"
          :content="store.filePreview"
          :loading="store.loadingFile"
          @select-file="onSelectFile"
        />
        <ChatPanel
          :actions="store.workspaceActions"
          :result="store.workspaceResult"
          :has-result="store.hasWorkspaceResult"
          :messages="store.workspaceMessages"
          :composer="composerValue"
          :sending="store.loadingChat"
          :process-state="store.activeProcessState"
          :loading-action="Boolean(store.runningAction)"
          :history-label="store.workspaceHistoryLabel"
          :can-cycle-sessions="store.hasMultipleSessions"
          :acceptance-summary="store.acceptanceSummary"
          :diff-files="store.diffFiles"
          :selected-diff="store.selectedDiff"
          :can-edit-acceptance-substate="store.canEditAcceptanceSubstate"
          @update:composer="composerValue = $event"
          @submit-chat="onSubmitChat"
          @action="onRunAction"
          @history="onHistory"
          @select-diff="onSelectDiff"
          @change-substate="onChangeSubstate"
        />
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCardStore } from '../../stores/cardStore'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import { showErrorMessage } from '../../utils/message'
import BoardScrollContainer from '../kanban/BoardScrollContainer.vue'
import ChatPanel from './ChatPanel.vue'
import ContextPane from './ContextPane.vue'
import SplitterHandle from './SplitterHandle.vue'
import WorkspaceHeader from './WorkspaceHeader.vue'

const store = useCardStore()
const workspace = useWorkspaceStore()
const { activeCard, activeStage } = storeToRefs(store)
const composerValue = ref('')

watch(
  () => store.activeCardId,
  () => {
    composerValue.value = ''
  }
)

const onSelectFile = async (filePath) => {
  try {
    await store.selectFile(filePath)
  } catch (error) {
    showErrorMessage(error, '读取文件失败')
  }
}

const onSubmitChat = async () => {
  const message = composerValue.value.trim()
  if (!message) {
    return
  }
  try {
    await store.sendChat(message)
    composerValue.value = ''
  } catch (error) {
    showErrorMessage(error, '发送消息失败')
  }
}

const onRunAction = async (actionKey) => {
  try {
    await store.runAction(actionKey)
  } catch (error) {
    showErrorMessage(error, '执行动作失败')
  }
}

const onHistory = async () => {
  if (!store.hasMultipleSessions) {
    return
  }
  try {
    await store.cycleHistorySession()
  } catch (error) {
    showErrorMessage(error, '切换会话失败')
  }
}

const onSelectDiff = async (filePath) => {
  try {
    await store.selectDiffFile(filePath)
  } catch (error) {
    showErrorMessage(error, '加载文件预览失败')
  }
}

const onChangeSubstate = async (value) => {
  try {
    await store.setAcceptanceSubstate(value)
  } catch (error) {
    showErrorMessage(error, '更新验收状态失败')
  }
}

const closeWorkspace = () => {
  composerValue.value = ''
  store.setActiveCard(null)
  workspace.close()
}
</script>

<style scoped>
.main {
  min-height: 0;
  display: grid;
  grid-template-columns: 1fr;
  overflow: hidden;
  background: #f7f7f5;
}

.main.expanded {
  grid-template-columns: minmax(0, calc(100% - var(--workspace-width) - 10px)) 10px var(--workspace-width);
}

.board-area,
.workspace-shell,
.workspace-grid {
  min-height: 0;
}

.board-area {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
}

.workspace-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #fafaf9;
  border-left: 1px solid #ddddda;
}

.workspace-grid {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(300px, 0.95fr) minmax(320px, 1.05fr);
  overflow: hidden;
}

@media (max-width: 1100px) {
  .main.expanded {
    grid-template-columns: 1fr;
  }

  .board-area {
    display: none;
  }

  .workspace-shell {
    border-left: 0;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}
</style>

