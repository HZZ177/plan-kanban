import { request } from './http'
import type { AcceptanceSummary } from './types'

export async function getAcceptanceSummary(cardId: string): Promise<AcceptanceSummary> {
  return request<AcceptanceSummary>(`/cards/${cardId}/acceptance`)
}

export async function rollbackAcceptance(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/cards/${cardId}/acceptance/rollback`, {
    method: 'POST',
  })
}
