<template>
  <label class="search-wrap" aria-label="搜索需求">
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.4" />
      <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
    </svg>
    <input :value="store.searchQuery" type="text" placeholder="搜索需求..." @input="store.setSearchQuery($event.target.value)" />
  </label>
</template>

<script setup>
import { useCardStore } from '../../stores/cardStore'

const store = useCardStore()
</script>

<style scoped>
.search-wrap {
  flex: 0 1 260px;
  min-width: 220px;
  height: 34px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  color: #74777d;
}

input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  color: #232427;
}

.search-wrap:focus-within {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .search-wrap {
    flex: auto;
    min-width: 0;
  }
}
</style>
