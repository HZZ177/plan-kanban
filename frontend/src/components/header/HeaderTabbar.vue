<template>
  <div class="tabbar" aria-label="看板视图切换">
    <button :class="{ active: store.boardFilter === 'all' }" type="button" @click="store.setBoardFilter('all')">全部需求</button>
    <button :class="{ active: store.boardFilter === 'in-progress' }" type="button" @click="store.setBoardFilter('in-progress')">进行中</button>
    <button :class="{ active: store.boardFilter === 'acceptance' }" type="button" @click="store.setBoardFilter('acceptance')">待验收</button>
  </div>
</template>

<script setup>
import { useCardStore } from '../../stores/cardStore'

const store = useCardStore()
</script>

<style scoped>
.tabbar {
  display: inline-flex;
  overflow: hidden;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
}

button {
  min-height: 34px;
  padding: 0 12px;
  border: 0;
  border-right: 1px solid #ddddda;
  background: #ffffff;
  color: #5f6269;
  cursor: pointer;
}

button:last-child {
  border-right: 0;
}

.active {
  background: #f4f5f7;
  color: #222325;
}

button:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: -2px;
}
</style>
