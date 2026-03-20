export type PatchEvent = {
  type: string
  channel: string
  payload: Record<string, unknown>
}

export function applyPatchBatch<T extends Record<string, unknown>>(state: T, batch: PatchEvent): T {
  return {
    ...state,
    lastPatch: batch,
  }
}
