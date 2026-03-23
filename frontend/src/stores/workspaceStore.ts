import { defineStore } from 'pinia'

function getViewportMaxWidth() {
  if (typeof window === 'undefined') {
    return 1120
  }
  return Math.min(window.innerWidth - 260, 1120)
}

let animationTimer: ReturnType<typeof setTimeout> | null = null
let openFrame: ReturnType<typeof requestAnimationFrame> | null = null

function clearAnimationTimer() {
  if (!animationTimer) {
    return
  }
  clearTimeout(animationTimer)
  animationTimer = null
}

function clearOpenFrame() {
  if (openFrame === null) {
    return
  }
  cancelAnimationFrame(openFrame)
  openFrame = null
}

export const useWorkspaceStore = defineStore('workspaceStore', {
  state: () => ({
    present: false,
    expanded: false,
    width: 760,
    activeFile: '',
    dragging: false,
    heavyRenderDeferred: false,
  }),
  actions: {
    open(file = '') {
      clearAnimationTimer()
      clearOpenFrame()
      this.present = true
      this.expanded = false
      this.activeFile = file
      this.heavyRenderDeferred = true
      this.width = getViewportMaxWidth()
      openFrame = requestAnimationFrame(() => {
        this.expanded = true
        openFrame = null
      })
      animationTimer = setTimeout(() => {
        this.heavyRenderDeferred = false
        animationTimer = null
      }, 340)
    },
    close() {
      clearAnimationTimer()
      clearOpenFrame()
      this.expanded = false
      this.dragging = false
      this.heavyRenderDeferred = true
      animationTimer = setTimeout(() => {
        this.present = false
        this.activeFile = ''
        this.heavyRenderDeferred = false
        animationTimer = null
      }, 240)
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
      if (dragging) {
        clearAnimationTimer()
        this.heavyRenderDeferred = true
        return
      }
      animationTimer = setTimeout(() => {
        this.heavyRenderDeferred = false
        animationTimer = null
      }, 120)
    },
  },
})
