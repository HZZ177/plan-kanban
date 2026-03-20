import { defineStore } from 'pinia'
import { getAcceptanceSummary, rollbackAcceptance } from '../services/api/acceptance'
import { generateContract, precheckGenerateContract, precheckStartDevelopment, startDevelopment } from '../services/api/actions'
import { createCard, getCard, updateAcceptanceSubstate } from '../services/api/cards'
import { getCardSessions, getSessionEntries, sendCardMessage } from '../services/api/chat'
import { getDiffFile, getDiffFiles } from '../services/api/diff'
import { getStageFileContent, getStageFiles } from '../services/api/files'
import { getKanban } from '../services/api/kanban'
import { getCardProcess } from '../services/api/process'
import type {
  AcceptanceSummary,
  CardDetail,
  ConversationEntry,
  DiffPreview,
  KanbanStage,
  ProcessState,
  SessionRecord,
  StageFileItem,
  StageKey,
} from '../services/api/types'
import { useWorkspaceStore } from './workspaceStore'

export type PriorityKey = 'P0' | 'P1' | 'P2'

export type StageInfo = {
  key: StageKey
  title: string
  color: string
}

export type CardItem = {
  id: string
  title: string
  summary: string
  owner: string
  priority: PriorityKey
  currentStage: StageKey
  acceptanceSubstate: string | null
  activeProcessType: string
  activeProcessStatus: string
  activeProcessSessionId: string | null
}

export type WorkspaceMessage = {
  role: 'user' | 'assistant' | 'tool' | 'thinking'
  label: string
  time: string
  content: string
  output?: string
}

export type StageAction = {
  key: string
  label: string
  primary?: boolean
  disabled?: boolean
}

export const stageDefinitions: StageInfo[] = [
  { key: 'raw', title: '原始需求澄清', color: '#4c8bf5' },
  { key: 'plan', title: '方案生成', color: '#f59e0b' },
  { key: 'contract', title: '澄清&拆解执行合同', color: '#8b5cf6' },
  { key: 'developing', title: '开发中', color: '#2563eb' },
  { key: 'acceptance', title: '待验收', color: '#22c55e' },
]

function toCardItem(card: CardDetail): CardItem {
  return {
    id: card.id,
    title: card.title,
    summary: card.summary,
    owner: card.owner as string,
    priority: (card.priority || 'P1') as PriorityKey,
    currentStage: card.current_stage,
    acceptanceSubstate: card.acceptance_substate,
    activeProcessType: card.active_process_type,
    activeProcessStatus: card.active_process_status,
    activeProcessSessionId: card.active_process_session_id,
  }
}

function formatTime(value: string | null): string {
  if (!value) {
    return 'now'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'now'
  }
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function mapEntryToMessage(entry: ConversationEntry): WorkspaceMessage {
  const time = formatTime(entry.created_at)

  if (entry.entry_type === 'tool_use' || entry.entry_type === 'tool_result') {
    return {
      role: 'tool',
      label: entry.role || '工具',
      time,
      content: entry.content || '',
      output: JSON.stringify(entry.payload ?? {}, null, 2),
    }
  }

  if (entry.entry_type === 'thinking') {
    return {
      role: 'thinking',
      label: entry.role || 'Claude Code',
      time,
      content: entry.content || '正在整理中...',
    }
  }

  return {
    role: entry.role === 'user' ? 'user' : 'assistant',
    label: entry.role === 'user' ? '用户' : 'Claude Code',
    time,
    content: entry.content || '',
  }
}

function buildStageActions(stage: StageKey, processState: ProcessState | null): StageAction[] {
  const running = processState?.active_process_status === 'running'
  if (stage === 'plan') {
    return [{ key: 'generate-contract', label: '生成执行合同', primary: true, disabled: running }]
  }
  if (stage === 'contract') {
    return [{ key: 'start-development', label: '开始开发', primary: true, disabled: running }]
  }
  if (stage === 'acceptance') {
    return [{ key: 'rollback-acceptance', label: '打回开发', primary: true, disabled: running }]
  }
  return []
}

export const useCardStore = defineStore('cardStore', {
  state: () => ({
    stages: [] as KanbanStage[],
    cards: [] as CardItem[],
    boardFilter: 'all' as 'all' | 'in-progress' | 'acceptance',
    searchQuery: '',
    activeCardId: null as string | null,
    activeCardDetail: null as CardDetail | null,
    activeProcessState: null as ProcessState | null,
    activeSessions: [] as SessionRecord[],
    activeSessionId: null as string | null,
    activeEntries: [] as ConversationEntry[],
    stageFiles: [] as StageFileItem[],
    selectedFilePath: '',
    selectedFileContent: '',
    acceptanceSummary: null as AcceptanceSummary | null,
    diffFiles: [] as StageFileItem[],
    selectedDiff: null as DiffPreview | null,
    loadingCards: false,
    loadingWorkspace: false,
    loadingFile: false,
    loadingChat: false,
    runningAction: '',
    boardError: '',
    workspaceError: '',
    actionError: '',
    creatingCard: false,
  }),
  getters: {
    filteredCards(state): CardItem[] {
      const keyword = state.searchQuery.trim().toLowerCase()
      return state.cards.filter((card) => {
        if (state.boardFilter === 'in-progress' && !['plan', 'contract', 'developing'].includes(card.currentStage)) {
          return false
        }
        if (state.boardFilter === 'acceptance' && card.currentStage !== 'acceptance') {
          return false
        }
        if (!keyword) {
          return true
        }
        return [card.title, card.summary, card.owner, card.id].some((field) => field.toLowerCase().includes(keyword))
      })
    },
    columns(state): Array<{ key: StageKey; title: string; color: string; cards: CardItem[] }> {
      return stageDefinitions.map((stage) => ({
        key: stage.key,
        title: state.stages.find((item) => item.key === stage.key)?.title ?? stage.title,
        color: stage.color,
        cards: this.filteredCards.filter((card) => card.currentStage === stage.key),
      }))
    },
    activeCard(state): CardItem | null {
      if (!state.activeCardId) {
        return null
      }
      return state.cards.find((card) => card.id === state.activeCardId) ?? null
    },
    activeStage(): StageInfo | null {
      if (!this.activeCard) {
        return null
      }
      return stageDefinitions.find((stage) => stage.key === this.activeCard.currentStage) ?? null
    },
    filePreview(state): string {
      if (state.loadingFile) {
        return '正在加载文件内容...'
      }
      if (state.selectedFileContent) {
        return state.selectedFileContent
      }
      return '当前阶段没有可读取的文件内容。'
    },
    workspaceMessages(state): WorkspaceMessage[] {
      return state.activeEntries.map(mapEntryToMessage)
    },
    workspaceResult(): string {
      return ''
    },
    hasWorkspaceResult(): boolean {
      return false
    },
    canEditAcceptanceSubstate(): boolean {
      return this.activeCard?.currentStage === 'acceptance' && Boolean(this.acceptanceSummary)
    },
    workspaceHistoryLabel(state): string {
      if (!state.activeSessions.length) {
        return '暂无会话'
      }
      if (state.activeSessions.length === 1) {
        return `当前会话 · ${formatTime(state.activeSessions[0].started_at)}`
      }
      return `切换会话 · ${formatTime(state.activeSessions[0].started_at)}`
    },
    hasMultipleSessions(state): boolean {
      return state.activeSessions.length > 1
    },
    workspaceActions(): StageAction[] {
      if (!this.activeCard) {
        return []
      }
      return buildStageActions(this.activeCard.currentStage, this.activeProcessState)
    },
  },
  actions: {
    setActiveCard(cardId: string | null) {
      this.activeCardId = cardId
    },
    setBoardFilter(filter: 'all' | 'in-progress' | 'acceptance') {
      this.boardFilter = filter
    },
    setSearchQuery(query: string) {
      this.searchQuery = query
    },
    async cycleHistorySession() {
      if (!this.activeSessions.length) {
        return
      }
      const currentIndex = this.activeSessions.findIndex((item) => item.id === this.activeSessionId)
      const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % this.activeSessions.length : 0
      await this.loadSessionEntries(this.activeSessions[nextIndex].id)
    },
    async createNewCard(form: {
      project_id: string
      title: string
      summary: string
      owner: string
      priority: string
      raw_requirement: string
    }) {
      const projectId = form.project_id.trim()
      const title = form.title.trim()
      const summary = form.summary.trim()
      const owner = form.owner.trim()
      const priority = form.priority.trim()
      const rawRequirement = form.raw_requirement.trim()

      if (!projectId || !title || !summary || !owner || !priority || !rawRequirement) {
        this.actionError = '请完整填写 project_id、标题、摘要、负责人、优先级和原始需求。'
        throw new Error(this.actionError)
      }

      this.creatingCard = true
      this.actionError = ''
      try {
        const payload = await createCard({
          project_id: projectId,
          title,
          summary,
          owner,
          priority,
          raw_requirement: rawRequirement,
        })
        await this.refreshBoard()
        await this.selectCard(payload.id)
      } catch (error) {
        this.actionError = error instanceof Error ? error.message : '新建需求失败'
        throw error
      } finally {
        this.creatingCard = false
      }
    },
    async loadKanban() {
      this.loadingCards = true
      this.boardError = ''
      try {
        const payload = await getKanban()
        this.stages = payload.stages
        this.cards = payload.stages.flatMap((stage) => stage.items.map(toCardItem))
      } catch (error) {
        this.boardError = error instanceof Error ? error.message : '加载看板失败'
        throw error
      } finally {
        this.loadingCards = false
      }
    },
    async refreshBoard() {
      await this.loadKanban()
      if (this.activeCardId) {
        const exists = this.cards.some((card) => card.id === this.activeCardId)
        if (!exists) {
          this.activeCardId = null
        }
      }
    },
    async selectCard(cardId: string) {
      const workspace = useWorkspaceStore()
      this.activeCardId = cardId
      this.loadingWorkspace = true
      this.workspaceError = ''
      this.actionError = ''
      try {
        await this.loadCardWorkspace(cardId)
        workspace.open(this.selectedFilePath)
      } catch (error) {
        this.workspaceError = error instanceof Error ? error.message : '加载工作区失败'
        workspace.open('')
        throw error
      } finally {
        this.loadingWorkspace = false
      }
    },
    async loadCardWorkspace(cardId: string) {
      const [card, processState, files, sessions] = await Promise.all([
        getCard(cardId),
        getCardProcess(cardId),
        getStageFiles(cardId),
        getCardSessions(cardId),
      ])

      this.activeCardDetail = card
      this.activeProcessState = processState
      this.activeSessions = sessions
      this.activeSessionId = sessions[0]?.id ?? processState.active_process_session_id ?? null
      this.stageFiles = files
      this.cards = this.cards.map((item) => (item.id === card.id ? toCardItem(card) : item))

      if (this.activeSessionId) {
        this.activeEntries = await getSessionEntries(this.activeSessionId)
      } else {
        this.activeEntries = []
      }

      if (files.length) {
        const defaultFile = files.find((item) => item.exists)?.path ?? files[0].path
        await this.selectFile(defaultFile)
      } else {
        this.selectedFilePath = ''
        this.selectedFileContent = ''
      }

      if (card.current_stage === 'acceptance') {
        this.acceptanceSummary = await getAcceptanceSummary(cardId)
        this.diffFiles = await getDiffFiles(cardId)
        if (this.acceptanceSummary.preview?.path) {
          this.selectedDiff = await getDiffFile(cardId, this.acceptanceSummary.preview.path)
        } else {
          this.selectedDiff = null
        }
      } else {
        this.acceptanceSummary = null
        this.diffFiles = []
        this.selectedDiff = null
      }
    },
    async selectFile(filePath: string) {
      if (!this.activeCardId || !filePath) {
        return
      }
      const workspace = useWorkspaceStore()
      this.loadingFile = true
      try {
        const payload = await getStageFileContent(this.activeCardId, filePath)
        this.selectedFilePath = payload.path
        this.selectedFileContent = payload.content
        workspace.setActiveFile(payload.path)
      } catch (error) {
        this.selectedFilePath = filePath
        this.selectedFileContent = error instanceof Error ? error.message : '读取文件失败'
        workspace.setActiveFile(filePath)
      } finally {
        this.loadingFile = false
      }
    },
    async loadSessionEntries(sessionId: string) {
      this.activeSessionId = sessionId
      this.activeEntries = await getSessionEntries(sessionId)
    },
    async selectDiffFile(filePath: string) {
      if (!this.activeCardId) {
        return
      }
      this.selectedDiff = await getDiffFile(this.activeCardId, filePath)
    },
    async setAcceptanceSubstate(substate: string | null) {
      if (!this.activeCardId) {
        return
      }
      await updateAcceptanceSubstate(this.activeCardId, substate)
      await this.loadCardWorkspace(this.activeCardId)
      await this.refreshBoard()
    },
    async sendChat(message: string) {
      if (!this.activeCardId) {
        return
      }
      this.loadingChat = true
      this.actionError = ''
      try {
        const payload = await sendCardMessage(this.activeCardId, message, this.activeSessionId)
        this.activeSessionId = payload.session.id
        this.activeEntries = await getSessionEntries(payload.session.id)
        this.activeSessions = await getCardSessions(this.activeCardId)
        this.activeProcessState = await getCardProcess(this.activeCardId)
      } catch (error) {
        this.actionError = error instanceof Error ? error.message : '发送消息失败'
        throw error
      } finally {
        this.loadingChat = false
      }
    },
    async runAction(actionKey: string) {
      if (!this.activeCardId || !this.activeCard) {
        return
      }
      this.runningAction = actionKey
      this.actionError = ''
      try {
        if (actionKey === 'generate-contract') {
          await precheckGenerateContract(this.activeCardId)
          await generateContract(this.activeCardId)
        } else if (actionKey === 'start-development') {
          await precheckStartDevelopment(this.activeCardId)
          await startDevelopment(this.activeCardId)
        } else if (actionKey === 'rollback-acceptance') {
          await rollbackAcceptance(this.activeCardId)
        }
        await this.refreshBoard()
        await this.loadCardWorkspace(this.activeCardId)
      } catch (error) {
        this.actionError = error instanceof Error ? error.message : '执行动作失败'
        throw error
      } finally {
        this.runningAction = ''
      }
    },
  },
})
