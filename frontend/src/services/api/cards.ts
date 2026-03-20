import { request } from './http'
import type { CardDetail, StageKey } from './types'

export type CreateCardPayload = {
  project_id: string
  title: string
  summary?: string
  owner?: string
  priority?: string
  raw_requirement: string
}

export async function listCards(): Promise<CardDetail[]> {
  return request<CardDetail[]>('/cards')
}

export async function createCard(payload: CreateCardPayload): Promise<CardDetail> {
  return request<CardDetail>('/cards', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function getCard(cardId: string): Promise<CardDetail> {
  return request<CardDetail>(`/cards/${cardId}`)
}

export async function updateCardStage(cardId: string, currentStage: StageKey): Promise<CardDetail> {
  return request<CardDetail>(`/cards/${cardId}/stage`, {
    method: 'PUT',
    body: JSON.stringify({ current_stage: currentStage }),
  })
}

export async function updateAcceptanceSubstate(cardId: string, acceptanceSubstate: string | null): Promise<{ acceptance_substate: string | null }> {
  return request<{ acceptance_substate: string | null }>(`/cards/${cardId}/acceptance-substate`, {
    method: 'PUT',
    body: JSON.stringify({ acceptance_substate: acceptanceSubstate }),
  })
}
