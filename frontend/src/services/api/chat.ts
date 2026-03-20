import { request } from './http'
import type { ChatResponse, ConversationEntry, SessionRecord } from './types'

export async function sendCardMessage(cardId: string, message: string, sessionId?: string | null): Promise<ChatResponse> {
  return request<ChatResponse>(`/cards/${cardId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId ?? null }),
  })
}

export async function getCardSessions(cardId: string): Promise<SessionRecord[]> {
  return request<SessionRecord[]>(`/cards/${cardId}/sessions`)
}

export async function getSessionEntries(sessionId: string): Promise<ConversationEntry[]> {
  return request<ConversationEntry[]>(`/sessions/${sessionId}/entries`)
}
