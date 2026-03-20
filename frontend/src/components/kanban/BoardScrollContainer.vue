<template>
  <div class="board-scroll">
    <BoardColumns />
  </div>
</template>

<script setup lang="ts">
import BoardColumns from './BoardColumns.vue'
</script>

<style scoped>
.board-scroll { flex: 1; overflow-x: auto; overflow-y: hidden; background: white; }
</style>
