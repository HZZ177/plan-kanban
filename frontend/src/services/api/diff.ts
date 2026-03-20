import { request } from './http'
import type { DiffPreview, StageFileItem } from './types'

export async function getDiffFiles(cardId: string): Promise<StageFileItem[]> {
  return request<StageFileItem[]>(`/cards/${cardId}/diff/files`)
}

export async function getDiffFile(cardId: string, filePath: string): Promise<DiffPreview> {
  return request<DiffPreview>(`/cards/${cardId}/diff/file`, undefined, { file_path: filePath })
}
