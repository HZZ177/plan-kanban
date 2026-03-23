<template>
  <div
    ref="scrollRef"
    class="board-scroll"
    @wheel="onWheel"
  >
    <BoardColumns />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BoardColumns from './BoardColumns.vue'

const scrollRef = ref(null)

const onWheel = (event) => {
  if (!event.shiftKey || !scrollRef.value) {
    return
  }

  const container = scrollRef.value
  const canScrollHorizontally = container.scrollWidth > container.clientWidth
  if (!canScrollHorizontally) {
    return
  }

  container.scrollLeft += event.deltaY
  event.preventDefault()
}
</script>

<style scoped>
.board-scroll {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  background: white;
}
</style>
