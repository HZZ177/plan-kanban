export type StageKey = 'raw' | 'plan' | 'contract' | 'developing' | 'acceptance'

export type CardDetail = {
  id: string
  project_id: string
  title: string
  summary: string
  owner: string
  priority: string
  raw_requirement: string
  current_stage: StageKey
  acceptance_substate: string | null
  plan_path: string | null
  issues_path: string | null
  active_process_type: string
  active_process_status: string
  active_process_session_id: string | null
}

export type KanbanStage = {
  key: StageKey
  title: string
  count: number
  items: CardDetail[]
}

export type StageFileItem = {
  path: string
  name: string
  exists: boolean
}

export type StageFileContent = {
  path: string
  name: string
  content: string
}

export type SessionRecord = {
  id: string
  card_id: string
  stage_key: StageKey
  session_type: string
  cc_conversation_id: string | null
  status: string
  started_at: string | null
  completed_at: string | null
}

export type ConversationEntry = {
  id: string
  session_id: string
  execution_process_id: string | null
  entry_type: string
  role: string
  content: string | null
  payload: Record<string, unknown> | null
  created_at: string | null
  updated_at: string | null
}

export type ChatResponse = {
  session: SessionRecord
  context: {
    stage_key: StageKey
    stage_label: string
    active_process_type: string
    active_process_status: string
    acceptance_substate: string | null
    plan_path: string | null
    issues_path: string | null
  }
  entries: ConversationEntry[]
}

export type ProcessState = {
  active_process_type: string
  active_process_status: string
  active_process_session_id: string | null
}

export type AcceptanceSummary = {
  card_id: string
  current_stage: StageKey
  changed_files: StageFileItem[]
  preview: {
    path: string
    diff: string
    line_count: number
  } | null
  acceptance_substate: string | null
}

export type DiffPreview = {
  path: string
  diff: string
  line_count: number
}
