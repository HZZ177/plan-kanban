import { request } from './http'

export async function getRecoverySnapshot(cardId: string, sessionId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/cards/${cardId}/recovery/${sessionId}`)
}
