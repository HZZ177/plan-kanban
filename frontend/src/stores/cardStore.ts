import { defineStore } from 'pinia'
import { getAcceptanceSummary, rollbackAcceptance } from '../services/api/acceptance'
import { generateContract, precheckGenerateContract, precheckStartDevelopment, startDevelopment } from '../services/api/actions'
import { createCard, getCard, updateAcceptanceSubstate } from '../services/api/cards'
import { getCardSessions, getSessionEntries, sendCardMessage } from '../services/api/chat'
import { getDiffFile, getDiffFiles } from '../services/api/diff'
import { getStageFileContent, getStageFiles } from '../services/api/files'
import { getKanban } from '../services/api/kanban'
import { getCardProcess } from '../services/api/process'
import { getRecoverySnapshot } from '../services/api/recovery'
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
import type { PatchEvent } from '../services/ws/patchClient'
import { useJsonPatchStream } from '../services/ws/useJsonPatchStream'
import { useProjectStore } from './projectStore'
import { useWorkspaceStore } from './workspaceStore'

export type PriorityKey = 'P0' | 'P1' | 'P2'
export type BoardFilterKey = 'in-progress' | 'acceptance'

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
  id: string
  role: 'user' | 'assistant' | 'tool' | 'thinking' | 'ghost'
  label: string
  time: string
  content: string
  entryType?: string
  streaming?: boolean
  isFinished?: boolean
  output?: string
  payload?: Record<string, unknown> | null
  ghostKind?: 'thinking' | 'tool_use' | 'tool_result' | 'summary'
}

function buildAssistantPlaceholder(): WorkspaceMessage {
  return {
    id: `transient-assistant-${Date.now()}`,
    role: 'ghost',
    label: 'Claude Code',
    time: formatTime(null),
    content: 'Claude 正在思考',
    entryType: 'thinking',
    ghostKind: 'thinking',
    streaming: true,
    isFinished: false,
    payload: null,
  }
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

function buildGhostSummary(entry: ConversationEntry): string {
  const payload = entry.payload ?? {}
  if (entry.entry_type === 'tool_use') {
    const toolName = typeof payload.tool_name === 'string' ? payload.tool_name : '工具'
    const toolInput = payload.tool_input && typeof payload.tool_input === 'object' ? payload.tool_input as Record<string, unknown> : {}
    if (typeof toolInput.description === 'string' && toolInput.description) {
      return `${toolName} · ${toolInput.description}`
    }
    if (typeof toolInput.command === 'string' && toolInput.command) {
      return `${toolName} · ${toolInput.command}`
    }
    if (typeof toolInput.url === 'string' && toolInput.url) {
      return `${toolName} · ${toolInput.url}`
    }
    if (typeof toolInput.question === 'string' && toolInput.question) {
      return `${toolName} · ${toolInput.question}`
    }
    return toolName
  }
  if (entry.entry_type === 'tool_result') {
    const isError = Boolean(payload.is_error)
    return isError ? '工具调用失败' : '工具调用完成'
  }
  if (entry.entry_type === 'summary') {
    return entry.content || '执行摘要'
  }
  return entry.content || 'Claude 正在思考'
}

function buildGhostPayload(entry: ConversationEntry): Record<string, unknown> | null {
  const payload = entry.payload ?? {}
  if (entry.entry_type === 'tool_use') {
    return {
      tool_id: payload.tool_id,
      tool_name: payload.tool_name,
      tool_input: payload.tool_input,
    }
  }
  if (entry.entry_type === 'tool_result') {
    return {
      tool_use_id: payload.tool_use_id,
      is_error: payload.is_error,
      tool_use_result: payload.tool_use_result,
      raw_block: payload.raw_block,
    }
  }
  if (entry.entry_type === 'summary') {
    return payload
  }
  return payload
}

function groupGhostMessages(messages: WorkspaceMessage[]): WorkspaceMessage[] {
  const grouped: WorkspaceMessage[] = []
  const toolIndexById = new Map<string, number>()

  messages.forEach((message) => {
    if (message.role !== 'ghost' || (message.entryType !== 'tool_use' && message.entryType !== 'tool_result')) {
      grouped.push(message)
      return
    }

    const payload = message.payload ?? {}
    const toolId = typeof payload.tool_id === 'string'
      ? payload.tool_id
      : typeof payload.tool_use_id === 'string'
        ? payload.tool_use_id
        : ''

    if (message.entryType === 'tool_use') {
      grouped.push({
        ...message,
        streaming: true,
        isFinished: false,
      })
      if (toolId) {
        toolIndexById.set(toolId, grouped.length - 1)
      }
      return
    }

    const groupedIndex = toolId ? toolIndexById.get(toolId) : undefined
    if (groupedIndex == null) {
      grouped.push(message)
      return
    }

    const existing = grouped[groupedIndex]
    grouped[groupedIndex] = {
      ...existing,
      content: `${existing.content}${payload.tool_result_error ?? payload.is_error ? ' · 失败' : ' · 完成'}`,
      payload: {
        ...(existing.payload ?? {}),
        tool_result_content: message.content,
        tool_result_error: Boolean(payload.is_error),
        tool_result: payload.tool_use_result ?? null,
      },
      streaming: false,
      isFinished: true,
      ghostKind: 'tool_use',
    }
  })

  return grouped
}

function mapEntryToMessage(entry: ConversationEntry, entries: ConversationEntry[], processState: ProcessState | null, activeSessionId: string | null): WorkspaceMessage | null {
  const time = formatTime(entry.updated_at || entry.created_at)
  const lastAssistantEntry = [...entries].reverse().find((item) => item.entry_type === 'assistant_text' || item.entry_type === 'error')
  const isActiveSession = Boolean(activeSessionId && entry.session_id === activeSessionId)
  const isStreaming = Boolean(
    isActiveSession
      && processState?.active_process_status === 'running'
      && entry.role !== 'user'
      && lastAssistantEntry?.id === entry.id,
  )

  if (entry.entry_type === 'tool_use' || entry.entry_type === 'tool_result' || entry.entry_type === 'summary') {
    return {
      id: entry.id,
      role: 'ghost',
      label: 'Claude Code',
      time,
      content: buildGhostSummary(entry),
      entryType: entry.entry_type,
      payload: buildGhostPayload(entry),
      ghostKind: entry.entry_type as 'tool_use' | 'tool_result' | 'summary',
      streaming: entry.entry_type === 'tool_use' && isActiveSession && processState?.active_process_status === 'running',
      isFinished: entry.entry_type !== 'tool_use' || !isStreaming,
    }
  }

  if (entry.entry_type === 'thinking') {
    return {
      id: entry.id,
      role: 'ghost',
      label: 'Claude Code',
      time,
      content: entry.content || 'Claude 正在思考',
      entryType: entry.entry_type,
      payload: entry.payload,
      ghostKind: 'thinking',
      streaming: true,
      isFinished: false,
    }
  }

  if (entry.entry_type === 'error') {
    return {
      id: entry.id,
      role: 'assistant',
      label: 'Claude Code',
      time,
      content: entry.content || '执行失败',
      entryType: entry.entry_type,
      streaming: isStreaming,
      isFinished: !isStreaming,
    }
  }

  if (entry.entry_type !== 'user_message' && entry.entry_type !== 'assistant_text') {
    return null
  }

  return {
    id: entry.id,
    role: entry.role === 'user' ? 'user' : 'assistant',
    label: entry.role === 'user' ? '用户' : 'Claude Code',
    time,
    content: entry.content || '',
    entryType: entry.entry_type,
    streaming: entry.role === 'user' ? false : isStreaming,
    isFinished: entry.role === 'user' ? true : !isStreaming,
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
    boardFilters: [] as BoardFilterKey[],
    searchQuery: '',
    activeCardId: null as string | null,
    activeCardDetail: null as CardDetail | null,
    activeProcessState: null as ProcessState | null,
    activeSessions: [] as SessionRecord[],
    activeSessionId: null as string | null,
    activeEntries: [] as ConversationEntry[],
    transientMessages: [] as WorkspaceMessage[],
    stageFiles: [] as StageFileItem[],
    selectedFilePath: '',
    selectedFileContent: '',
    acceptanceSummary: null as AcceptanceSummary | null,
    diffFiles: [] as Array<StageFileItem & { issue_id?: string; source?: string; dev_state?: string; test_state?: string }>,
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
    lastRecovery: null as Record<string, unknown> | null,
    wsClients: {} as Record<string, { connect: (path: string) => void; disconnect: () => void }>,
  }),
  getters: {
    filteredCards(state): CardItem[] {
      const keyword = state.searchQuery.trim().toLowerCase()
      const hasFilters = state.boardFilters.length > 0
      return state.cards.filter((card) => {
        if (hasFilters) {
          const matchesStage = state.boardFilters.some((filter) => {
            if (filter === 'in-progress') {
              return ['plan', 'contract', 'developing'].includes(card.currentStage)
            }
            if (filter === 'acceptance') {
              return card.currentStage === 'acceptance'
            }
            return false
          })
          if (!matchesStage) {
            return false
          }
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
      const persistedMessages = state.activeEntries
        .map((entry) => mapEntryToMessage(entry, state.activeEntries, state.activeProcessState, state.activeSessionId))
        .filter((item): item is WorkspaceMessage => item !== null)
      return groupGhostMessages([...persistedMessages, ...state.transientMessages])
    },
    workspaceResult(): string {
      if (this.acceptanceSummary?.runtime) {
        return `总计 ${this.acceptanceSummary.runtime.total} / 已完成 ${this.acceptanceSummary.runtime.completed} / 失败 ${this.acceptanceSummary.runtime.failed} / 阻塞 ${this.acceptanceSummary.runtime.blocked}`
      }
      return ''
    },
    hasWorkspaceResult(): boolean {
      return Boolean(this.workspaceResult)
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
    clearTransientMessages() {
      this.transientMessages = []
    },
    ensureWsClient(channel: string) {
      if (this.wsClients[channel]) {
        return this.wsClients[channel]
      }
      const client = useJsonPatchStream((event: PatchEvent) => this.handleWsEvent(event))
      this.wsClients[channel] = client
      return client
    },
    connectWorkspaceStreams() {
      this.ensureWsClient('conversation').connect('/ws/conversation')
      this.ensureWsClient('process').connect('/ws/process')
      this.ensureWsClient('issues').connect('/ws/issues')
      this.ensureWsClient('files').connect('/ws/files')
      this.ensureWsClient('kanban').connect('/ws/kanban')
    },
    disconnectWorkspaceStreams() {
      Object.values(this.wsClients).forEach((client) => client.disconnect())
      this.wsClients = {}
    },
    async handleWsEvent(event: PatchEvent) {
      const payload = event.payload || {}
      const projectStore = useProjectStore()
      if (event.channel === 'process' && this.activeCardId && payload.card_id === this.activeCardId) {
        this.activeProcessState = {
          active_process_type: String(payload.active_process_type || this.activeProcessState?.active_process_type || 'none'),
          active_process_status: String(payload.active_process_status || this.activeProcessState?.active_process_status || 'idle'),
          active_process_session_id: payload.active_process_session_id ? String(payload.active_process_session_id) : null,
        }
        if (this.activeProcessState.active_process_status !== 'running') {
          this.clearTransientMessages()
        }
      }
      if (event.channel === 'issues' && this.activeCardId && payload.card_id === this.activeCardId && Array.isArray(payload.items)) {
        this.diffFiles = payload.items as Array<StageFileItem & { issue_id?: string; source?: string; dev_state?: string; test_state?: string }>
      }
      if (event.channel === 'files' && this.activeCardId && payload.card_id === this.activeCardId && Array.isArray(payload.files)) {
        this.stageFiles = payload.files as StageFileItem[]
      }
      if (
        event.channel === 'kanban'
        && Array.isArray(payload.stages)
        && (!payload.project_id || String(payload.project_id) === projectStore.activeProjectId)
      ) {
        this.stages = payload.stages as KanbanStage[]
        this.cards = this.stages.flatMap((stage) => stage.items.map(toCardItem))
      }
      if (
        event.channel === 'conversation'
        && this.activeCardId
        && payload.card_id === this.activeCardId
        && payload.session_id
        && String(payload.session_id) === this.activeSessionId
      ) {
        if (payload.entry) {
          const entry = payload.entry as ConversationEntry
          const existingIndex = this.activeEntries.findIndex((item) => item.id === entry.id)
          if (existingIndex >= 0) {
            const next = [...this.activeEntries]
            next[existingIndex] = entry
            this.activeEntries = next
          } else {
            this.activeEntries = [...this.activeEntries, entry]
          }
          if (entry.entry_type === 'assistant_text' || entry.entry_type === 'error') {
            this.clearTransientMessages()
          }
        } else {
          await this.loadSessionEntries(this.activeSessionId)
        }
      }
    },
    setActiveCard(cardId: string | null) {
      this.activeCardId = cardId
    },
    setBoardFilters(filters: BoardFilterKey[]) {
      this.boardFilters = [...filters]
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
        useProjectStore().setActiveProjectId(projectId)
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
        const projectId = useProjectStore().activeProjectId
        const payload = await getKanban(projectId)
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
      this.clearTransientMessages()
      workspace.open('')
      try {
        await this.loadCardWorkspace(cardId)
        this.connectWorkspaceStreams()
      } catch (error) {
        this.workspaceError = error instanceof Error ? error.message : '加载工作区失败'
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

      if (files.length) {
        const defaultFile = files.find((item) => item.exists)?.path ?? files[0].path
        this.selectedFilePath = defaultFile
        this.selectedFileContent = ''
        useWorkspaceStore().setActiveFile(defaultFile)
        void this.selectFile(defaultFile, cardId)
      } else {
        this.selectedFilePath = ''
        this.selectedFileContent = ''
      }

      if (this.activeSessionId) {
        void this.loadSessionEntries(this.activeSessionId, cardId)
      } else {
        this.activeEntries = []
        this.lastRecovery = null
      }

      if (card.current_stage === 'acceptance') {
        void this.loadAcceptanceWorkspace(cardId)
      } else {
        this.acceptanceSummary = null
        this.diffFiles = []
        this.selectedDiff = null
      }
    },
    async loadAcceptanceWorkspace(cardId: string) {
      const acceptanceSummary = await getAcceptanceSummary(cardId)
      const diffFiles = await getDiffFiles(cardId)
      if (this.activeCardId !== cardId) {
        return
      }
      this.acceptanceSummary = acceptanceSummary
      this.diffFiles = diffFiles
      if (acceptanceSummary.preview?.path) {
        this.selectedDiff = await getDiffFile(cardId, acceptanceSummary.preview.path)
        if (this.activeCardId !== cardId) {
          return
        }
      } else {
        this.selectedDiff = null
      }
    },
    async selectFile(filePath: string, cardId = this.activeCardId) {
      if (!cardId || !filePath) {
        return
      }
      const workspace = useWorkspaceStore()
      this.loadingFile = true
      try {
        const payload = await getStageFileContent(cardId, filePath)
        if (this.activeCardId !== cardId) {
          return
        }
        this.selectedFilePath = payload.path
        this.selectedFileContent = payload.content
        workspace.setActiveFile(payload.path)
      } catch (error) {
        if (this.activeCardId !== cardId) {
          return
        }
        this.selectedFilePath = filePath
        this.selectedFileContent = error instanceof Error ? error.message : '读取文件失败'
        workspace.setActiveFile(filePath)
      } finally {
        if (this.activeCardId === cardId) {
          this.loadingFile = false
        }
      }
    },
    async loadSessionEntries(sessionId: string, cardId = this.activeCardId) {
      this.activeSessionId = sessionId
      this.clearTransientMessages()
      const entries = await getSessionEntries(sessionId)
      if (!cardId || this.activeCardId !== cardId || this.activeSessionId !== sessionId) {
        return
      }
      this.activeEntries = entries
      this.lastRecovery = await getRecoverySnapshot(cardId, sessionId)
      if (!cardId || this.activeCardId !== cardId || this.activeSessionId !== sessionId) {
        return
      }
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
      this.clearTransientMessages()
      this.transientMessages = [buildAssistantPlaceholder()]
      try {
        const payload = await sendCardMessage(this.activeCardId, message, this.activeSessionId)
        this.activeSessionId = payload.session.id
        this.activeEntries = payload.entries
        this.activeSessions = await getCardSessions(this.activeCardId)
        this.activeProcessState = {
          active_process_type: 'conversation',
          active_process_status: 'running',
          active_process_session_id: payload.session.id,
        }
      } catch (error) {
        this.clearTransientMessages()
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
