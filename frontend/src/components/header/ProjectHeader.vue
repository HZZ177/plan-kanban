<template>
  <header class="board-header">
    <div class="project-row">
      <div class="project-title-wrap">
        <div class="project-title">Plan Kanban</div>
      </div>
    </div>
    <div class="toolbar-row">
      <HeaderTabbar />
      <HeaderSearch />
      <button class="new-btn" type="button" :disabled="cardStore.creatingCard" @click="modalOpen = true">{{ cardStore.creatingCard ? '创建中...' : '新建需求 +' }}</button>
      <button v-if="workspace.expanded" class="ghost-btn" type="button" @click="closeWorkspace">收起工作区</button>
    </div>
  </header>
  <NewCardModal :form="form" :open="modalOpen" :submitting="cardStore.creatingCard" @update:form="Object.assign(form, $event)" @close="closeModal" @submit="createCard" />
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useCardStore } from '../../stores/cardStore'
import { useWorkspaceStore } from '../../stores/workspaceStore'
import { showErrorMessage } from '../../utils/message'
import HeaderSearch from './HeaderSearch.vue'
import HeaderTabbar from './HeaderTabbar.vue'
import NewCardModal from './NewCardModal.vue'

const cardStore = useCardStore()
const workspace = useWorkspaceStore()
const modalOpen = ref(false)
const form = reactive({
  project_id: '',
  title: '',
  summary: '',
  owner: '',
  priority: 'P1',
  raw_requirement: '',
})

const resetForm = () => {
  form.project_id = ''
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

const createCard = async () => {
  try {
    await cardStore.createNewCard({ ...form })
    closeModal()
  } catch (error) {
    showErrorMessage(error, '新建需求失败')
  }
}

const closeWorkspace = () => {
  cardStore.setActiveCard(null)
  workspace.close()
}
</script>


<style scoped>
.board-header {
  flex: 0 0 auto;
  padding: 18px 18px 10px;
  border-bottom: 1px solid #ddddda;
  background: #ffffff;
}

.project-row {
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.project-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.project-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.toolbar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.new-btn,
.ghost-btn {
  min-height: 34px;
  padding: 0 12px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 13px;
  white-space: nowrap;
  cursor: pointer;
}

.new-btn {
  border: 1px solid #b56018;
  background: #b56018;
  color: #ffffff;
}

.new-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.ghost-btn {
  border: 1px solid #ddddda;
  background: #ffffff;
  color: #53575e;
}

.new-btn:focus-visible,
.ghost-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
