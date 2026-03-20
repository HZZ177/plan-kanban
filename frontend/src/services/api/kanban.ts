import { request } from './http'
import type { KanbanStage } from './types'

export async function getKanban(): Promise<{ stages: KanbanStage[] }> {
  return request<{ stages: KanbanStage[] }>('/kanban')
}
