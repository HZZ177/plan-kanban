import { message } from 'ant-design-vue'

function normalizeError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) {
    return error.message
  }
  if (typeof error === 'string' && error.trim()) {
    return error
  }
  return fallback
}

export function showErrorMessage(error: unknown, fallback: string) {
  const content = normalizeError(error, fallback)
  message.error(content)
  return content
}
