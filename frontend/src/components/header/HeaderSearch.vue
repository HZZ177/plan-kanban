<template>
  <label
    class="search-wrap"
    aria-label="搜索需求"
  >
    <svg
      width="13"
      height="13"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="7"
        cy="7"
        r="4.5"
        stroke="currentColor"
        stroke-width="1.4"
      />
      <path
        d="M10.5 10.5L14 14"
        stroke="currentColor"
        stroke-width="1.4"
        stroke-linecap="round"
      />
    </svg>
    <input
      :value="store.searchQuery"
      type="text"
      placeholder="搜索需求"
      @input="onInput"
    >
  </label>
</template>

<script setup>
import { useCardStore } from '../../stores/cardStore'

const store = useCardStore()

const onInput = (event) => {
  store.setSearchQuery(event.target.value)
}
</script>

<style scoped>
.search-wrap {
  flex: 1 1 240px;
  min-width: 180px;
  height: 30px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 9px;
  border: 1px solid #ddddda;
  border-radius: 7px;
  background: #ffffff;
  color: #7a7e85;
}

input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  color: #232427;
  font-size: 12px;
}

input::placeholder {
  color: #9a9ea5;
}

.search-wrap:focus-within {
  outline: 2px solid rgba(76, 139, 245, 0.22);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .search-wrap {
    flex: 1 1 200px;
    min-width: 0;
  }
}
</style>
