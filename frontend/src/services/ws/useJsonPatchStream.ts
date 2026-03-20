import type { PatchEvent } from './patchClient'

export function useJsonPatchStream(onEvent: (event: PatchEvent) => void) {
  return {
    handle(event: PatchEvent) {
      onEvent(event)
    },
  }
}
