import { defineStore } from 'pinia'

const DEFAULT_PROJECT_ID = 'plan-kanban'
const STORAGE_KEY = 'plan-kanban:active-project-id'

function readStoredProjectId(): string {
  if (typeof window === 'undefined') {
    return DEFAULT_PROJECT_ID
  }
  const value = window.localStorage.getItem(STORAGE_KEY)?.trim()
  return value || DEFAULT_PROJECT_ID
}

export const useProjectStore = defineStore('projectStore', {
  state: () => ({
    activeProjectId: readStoredProjectId(),
  }),
  actions: {
    setActiveProjectId(projectId: string) {
      const normalized = projectId.trim() || DEFAULT_PROJECT_ID
      this.activeProjectId = normalized
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(STORAGE_KEY, normalized)
      }
    },
  },
})
