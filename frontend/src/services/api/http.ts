const API_BASE = 'http://127.0.0.1:8000/api'

const TRACE_ID_STORAGE_KEY = 'plan-kanban-trace-id'

function generateRequestId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function getTraceId(): string {
  if (typeof window === 'undefined') {
    return generateRequestId()
  }
  const existing = window.sessionStorage.getItem(TRACE_ID_STORAGE_KEY)
  if (existing) {
    return existing
  }
  const next = generateRequestId()
  window.sessionStorage.setItem(TRACE_ID_STORAGE_KEY, next)
  return next
}

export function createRequestContext(): { traceId: string; requestId: string } {
  return {
    traceId: getTraceId(),
    requestId: generateRequestId(),
  }
}

export class ApiError extends Error {
  status: number
  payload: unknown
  traceId?: string | null
  requestId?: string | null

  constructor(message: string, status: number, payload: unknown, traceId?: string | null, requestId?: string | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
    this.traceId = traceId
    this.requestId = requestId
  }
}

export const buildApiUrl = (path: string, query?: Record<string, string | number | boolean | null | undefined>) => {
  const url = new URL(`${API_BASE}${path}`)
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        return
      }
      url.searchParams.set(key, String(value))
    })
  }
  return url.toString()
}

// HTTP 请求工具负责统一注入 trace/request id，并在失败时输出可排障日志。
export async function request<T>(path: string, init?: RequestInit, query?: Record<string, string | number | boolean | null | undefined>): Promise<T> {
  const context = createRequestContext()
  const response = await fetch(buildApiUrl(path, query), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Trace-Id': context.traceId,
      'X-Request-Id': context.requestId,
      ...(init?.headers ?? {}),
    },
  })

  const responseTraceId = response.headers.get('X-Trace-Id')
  const responseRequestId = response.headers.get('X-Request-Id')
  const text = await response.text()
  const payload = text ? JSON.parse(text) : null

  if (!response.ok) {
    const message = typeof payload === 'object' && payload && 'detail' in payload ? String((payload as { detail?: unknown }).detail) : `Request failed with status ${response.status}`
    console.error('API 请求失败', {
      path,
      status: response.status,
      traceId: responseTraceId ?? context.traceId,
      requestId: responseRequestId ?? context.requestId,
      payload,
    })
    throw new ApiError(message, response.status, payload, responseTraceId ?? context.traceId, responseRequestId ?? context.requestId)
  }

  return payload as T
}
