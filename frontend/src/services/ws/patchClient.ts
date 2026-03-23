export type PatchEvent = {
  type: string
  channel: string
  payload: Record<string, unknown>
}

import { ReconnectManager, buildWsUrl } from './reconnectManager'

export type WsSubscription = {
  close: () => void
}

export function applyPatchBatch<T extends Record<string, unknown>>(state: T, batch: PatchEvent): T {
  return {
    ...state,
    lastPatch: batch,
  }
}

// WS 客户端负责建立连接、自动重连，并把服务端事件回调给上层 store。
export function subscribeWs(path: string, onEvent: (event: PatchEvent) => void): WsSubscription {
  const reconnect = new ReconnectManager()
  let socket: WebSocket | null = null
  let timer: ReturnType<typeof setTimeout> | null = null
  let closed = false

  const connect = () => {
    if (closed) {
      return
    }
    const url = buildWsUrl(path)
    console.debug('开始连接 WebSocket', { path, url })
    socket = new WebSocket(url)
    socket.onopen = () => {
      reconnect.reset()
      console.debug('WebSocket 连接成功', { path })
    }
    socket.onmessage = (message) => {
      const payload = JSON.parse(String(message.data)) as PatchEvent
      onEvent(payload)
    }
    socket.onclose = () => {
      if (closed) {
        return
      }
      const delay = reconnect.nextDelay()
      console.warn('WebSocket 已关闭，准备重连', { path, delay })
      timer = setTimeout(connect, delay)
    }
    socket.onerror = () => {
      console.error('WebSocket 连接出错', { path })
      socket?.close()
    }
  }

  connect()

  return {
    close() {
      closed = true
      if (timer) {
        clearTimeout(timer)
      }
      console.debug('主动关闭 WebSocket', { path })
      socket?.close()
    },
  }
}
