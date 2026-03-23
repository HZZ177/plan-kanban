<template>
  <header class="board-header">
    <div class="toolbar-row">
      <HeaderTabbar />
      <HeaderSearch />
      <button
        class="ghost-btn"
        type="button"
        :disabled="refreshing"
        @click="refreshWorkspace"
      >
        {{ refreshing ? '刷新中...' : '刷新' }}
      </button>
      <button
        class="new-btn"
        type="button"
        :disabled="cardStore.creatingCard"
        @click="openModal"
      >
        {{ cardStore.creatingCard ? '创建中...' : '新建' }}
      </button>
    </div>
  </header>
  <NewCardModal
    :form="form"
    :open="modalOpen"
    :submitting="cardStore.creatingCard"
    @update:form="Object.assign(form, $event)"
    @close="closeModal"
    @submit="createCard"
  />
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useCardStore } from '../../stores/cardStore'
import { useProjectStore } from '../../stores/projectStore'
import { showErrorMessage } from '../../utils/message'
import HeaderSearch from './HeaderSearch.vue'
import HeaderTabbar from './HeaderTabbar.vue'
import NewCardModal from './NewCardModal.vue'

const cardStore = useCardStore()
const projectStore = useProjectStore()
const modalOpen = ref(false)
const refreshing = ref(false)
const form = reactive({
  project_id: projectStore.activeProjectId,
  title: '',
  summary: '',
  owner: '',
  priority: 'P1',
  raw_requirement: '',
})

const resetForm = () => {
  form.project_id = projectStore.activeProjectId
  form.title = ''
  form.summary = ''
  form.owner = ''
  form.priority = 'P1'
  form.raw_requirement = ''
}

const closeModal = () => {
  modalOpen.value = false
  resetForm()
}

const openModal = () => {
  form.project_id = projectStore.activeProjectId
  modalOpen.value = true
}

const createCard = async () => {
  try {
    await cardStore.createNewCard({ ...form })
    closeModal()
  } catch (error) {
    showErrorMessage(error, '新建需求失败')
  }
}

const refreshWorkspace = async () => {
  refreshing.value = true
  try {
    await cardStore.refreshBoard()
    if (cardStore.activeCardId) {
      await cardStore.loadCardWorkspace(cardStore.activeCardId)
    }
  } catch (error) {
    showErrorMessage(error, '刷新看板失败')
  } finally {
    refreshing.value = false
  }
}
</script>

<style scoped>
.board-header {
  flex: 0 0 auto;
  padding: 8px 14px;
  border-bottom: 1px solid #e5e4df;
  background: rgba(255, 255, 255, 0.92);
}

.toolbar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.new-btn,
.ghost-btn {
  min-height: 30px;
  padding: 0 11px;
  border-radius: 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
}

.new-btn {
  border: 1px solid #b56018;
  background: #b56018;
  color: #ffffff;
}

.ghost-btn {
  border: 1px solid #ddddda;
  background: #ffffff;
  color: #53575e;
}

.new-btn:disabled,
.ghost-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.new-btn:focus-visible,
.ghost-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.22);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .board-header {
    padding: 8px 10px;
  }

  .toolbar-row {
    gap: 6px;
  }

  .new-btn,
  .ghost-btn {
    flex: 0 0 auto;
  }
}
</style>
