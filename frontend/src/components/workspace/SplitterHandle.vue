<template>
  <div
    class="splitter"
    :class="{ dragging: workspace.dragging }"
    role="separator"
    aria-label="调整工作区宽度"
    aria-orientation="vertical"
    tabindex="0"
    @mousedown="startDrag"
    @keydown="onKeydown"
  />
</template>

<script setup>
import { onBeforeUnmount } from 'vue'
import { useWorkspaceStore } from '../../stores/workspaceStore'

const workspace = useWorkspaceStore()
let pendingWidth = 0
let frameId = null

const flushWidth = () => {
  frameId = null
  if (!workspace.dragging) {
    return
  }
  workspace.setWidth(pendingWidth)
}

const onMouseMove = (event) => {
  if (!workspace.dragging) {
    return
  }

  pendingWidth = window.innerWidth - event.clientX
  if (frameId !== null) {
    return
  }
  frameId = requestAnimationFrame(flushWidth)
}

const stopDrag = () => {
  if (!workspace.dragging) {
    return
  }

  if (frameId !== null) {
    cancelAnimationFrame(frameId)
    frameId = null
  }
  workspace.setWidth(pendingWidth || workspace.width)
  workspace.setDragging(false)
  document.body.style.cursor = ''
}

const startDrag = (event) => {
  if (!workspace.expanded) {
    return
  }

  pendingWidth = workspace.width
  workspace.setDragging(true)
  document.body.style.cursor = 'col-resize'
  event.preventDefault()
}

const onKeydown = (event) => {
  if (!workspace.expanded) {
    return
  }

  if (event.key === 'ArrowLeft') {
    workspace.setWidth(workspace.width + 24)
    event.preventDefault()
  }

  if (event.key === 'ArrowRight') {
    workspace.setWidth(workspace.width - 24)
    event.preventDefault()
  }
}

window.addEventListener('mousemove', onMouseMove)
window.addEventListener('mouseup', stopDrag)

onBeforeUnmount(() => {
  if (frameId !== null) {
    cancelAnimationFrame(frameId)
  }
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.splitter {
  position: relative;
  background: #f3f4f6;
  border-left: 1px solid #ddddda;
  border-right: 1px solid #ddddda;
  cursor: col-resize;
  user-select: none;
  opacity: 0;
  transition: opacity 300ms cubic-bezier(0.22, 1, 0.36, 1), background-color 180ms ease;
}

.splitter.visible {
  opacity: 1;
}

.splitter::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 36px;
  border-radius: 999px;
  background: #cfd3d8;
}

.splitter:hover,
.splitter.dragging {
  background: #edf2fb;
}

.splitter:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

@media (prefers-reduced-motion: reduce) {
  .splitter {
    transition: none;
  }
}
</style>
