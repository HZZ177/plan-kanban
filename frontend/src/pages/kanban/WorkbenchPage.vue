<template>
  <div class="app-shell">
    <div class="top-strip">Plan Kanban · 内部需求协同平台</div>
    <ProjectHeader />
    <WorkspaceShell />
  </div>
</template>

<script setup lang="ts">
import ProjectHeader from '../../components/header/ProjectHeader.vue'
import WorkspaceShell from '../../components/workspace/WorkspaceShell.vue'
</script>

<style scoped>
.app-shell {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-rows: 40px auto minmax(0, 1fr);
  overflow: hidden;
  background: #f5f5f3;
  color: #232427;
}

.top-strip {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  background: #f6f5f3;
  border-bottom: 1px solid #ddddda;
  color: #5f6269;
  font-size: 12px;
  letter-spacing: 0.01em;
}
</style>
