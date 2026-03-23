import { buildApiUrl, createRequestContext, getTraceId } from '../api/http'

export class ReconnectManager {
  private attempts = 0

  nextDelay(base = 1000): number {
    this.attempts += 1
    const delay = Math.min(base * this.attempts, 10000)
    console.debug('已安排 WebSocket 重连', { attempts: this.attempts, delay })
    return delay
  }

  reset(): void {
    this.attempts = 0
  }
}

export function buildWsUrl(path: string): string {
  const apiUrl = new URL(buildApiUrl('/health'))
  const context = createRequestContext()
  apiUrl.protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
  apiUrl.pathname = path.startsWith('/') ? path : `/${path}`
  apiUrl.searchParams.set('trace_id', getTraceId())
  apiUrl.searchParams.set('request_id', context.requestId)
  return apiUrl.toString()
}
