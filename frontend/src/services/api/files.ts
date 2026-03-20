import { request } from './http'
import type { StageFileContent, StageFileItem } from './types'

export async function getStageFiles(cardId: string): Promise<StageFileItem[]> {
  return request<StageFileItem[]>(`/cards/${cardId}/files`)
}

export async function getStageFileContent(cardId: string, filePath: string): Promise<StageFileContent> {
  return request<StageFileContent>(`/cards/${cardId}/files/content`, undefined, { file_path: filePath })
}
