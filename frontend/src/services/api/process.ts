import { request } from './http'
import type { ProcessState } from './types'

export async function getCardProcess(cardId: string): Promise<ProcessState> {
  return request<ProcessState>(`/cards/${cardId}/process`)
}

export async function stopCardProcess(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/cards/${cardId}/process/stop`, {
    method: 'POST',
  })
}
