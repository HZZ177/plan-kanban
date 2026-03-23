import type { PatchEvent, WsSubscription } from './patchClient'
import { subscribeWs } from './patchClient'

export function useJsonPatchStream(onEvent: (event: PatchEvent) => void) {
  let subscription: WsSubscription | null = null

  return {
    connect(path: string) {
      subscription?.close()
      subscription = subscribeWs(path, onEvent)
    },
    disconnect() {
      subscription?.close()
      subscription = null
    },
    handle(event: PatchEvent) {
      onEvent(event)
    },
  }
}
