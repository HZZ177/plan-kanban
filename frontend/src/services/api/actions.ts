import { request } from './http'

export async function precheckGenerateContract(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/actions/cards/${cardId}/generate-contract/precheck`, {
    method: 'POST',
  })
}

export async function generateContract(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/actions/cards/${cardId}/generate-contract`, {
    method: 'POST',
  })
}

export async function precheckStartDevelopment(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/actions/cards/${cardId}/start-development/precheck`, {
    method: 'POST',
  })
}

export async function startDevelopment(cardId: string): Promise<Record<string, unknown>> {
  return request<Record<string, unknown>>(`/actions/cards/${cardId}/start-development`, {
    method: 'POST',
  })
}
