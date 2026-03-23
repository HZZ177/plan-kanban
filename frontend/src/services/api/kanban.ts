import { request } from './http'
import type { KanbanStage } from './types'

export async function getKanban(projectId?: string): Promise<{ stages: KanbanStage[]; project_id?: string | null }> {
  return request<{ stages: KanbanStage[]; project_id?: string | null }>('/kanban', undefined, { project_id: projectId ?? null })
}
