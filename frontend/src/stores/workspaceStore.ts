import { defineStore } from 'pinia'

function getViewportMaxWidth() {
  if (typeof window === 'undefined') {
    return 1120
  }
  return Math.min(window.innerWidth - 260, 1120)
}

export const useWorkspaceStore = defineStore('workspaceStore', {
  state: () => ({
    expanded: false,
    width: 760,
    activeFile: '',
    dragging: false,
  }),
  actions: {
    open(file = '') {
      this.expanded = true
      this.activeFile = file
      this.width = getViewportMaxWidth()
    },
    close() {
      this.expanded = false
      this.activeFile = ''
      this.dragging = false
    },
    setWidth(width: number) {
      const viewportMax = getViewportMaxWidth()
      this.width = Math.max(560, Math.min(width, viewportMax))
    },
    setActiveFile(file: string) {
      this.activeFile = file
    },
    setDragging(dragging: boolean) {
      this.dragging = dragging
    },
  },
})
