<template>
  <div class="filter-wrap">
    <button
      class="filter-trigger"
      type="button"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggleOpen"
    >
      <span class="filter-label">
        {{ summaryLabel }}
      </span>
      <span
        class="filter-caret"
        :class="{ open }"
      >▾</span>
    </button>
    <div
      v-if="open"
      class="filter-panel"
      role="listbox"
      aria-label="看板筛选"
      @click.stop
    >
      <label
        v-for="option in options"
        :key="option.value"
        class="filter-option"
      >
        <input
          type="checkbox"
          :checked="selectedSet.has(option.value)"
          @change="onCheckboxChange(option.value, $event)"
        >
        <span>
          {{ option.label }}
        </span>
      </label>
      <button
        v-if="store.boardFilters.length"
        class="clear-btn"
        type="button"
        @click="clearFilters"
      >
        清空筛选
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useCardStore } from '../../stores/cardStore'

const store = useCardStore()
const open = ref(false)

const options = [
  { value: 'in-progress', label: '进行中' },
  { value: 'acceptance', label: '待验收' },
]

const selectedSet = computed(() => new Set(store.boardFilters))
const summaryLabel = computed(() => {
  if (!store.boardFilters.length) {
    return '筛选：全部'
  }
  return `筛选：${options
    .filter((option) => selectedSet.value.has(option.value))
    .map((option) => option.label)
    .join('、')}`
})

const close = () => {
  open.value = false
}

const handleDocumentClick = () => {
  close()
}

const toggleOpen = (event) => {
  event.stopPropagation()
  open.value = !open.value
}

const toggleOption = (value, checked) => {
  const next = new Set(store.boardFilters)
  if (checked) {
    next.add(value)
  } else {
    next.delete(value)
  }
  store.setBoardFilters([...next])
}

const onCheckboxChange = (value, event) => {
  toggleOption(value, event.target.checked)
}

const clearFilters = () => {
  store.setBoardFilters([])
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.filter-wrap {
  position: relative;
  flex: 0 0 auto;
}

.filter-trigger {
  min-height: 30px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 7px;
  background: #ffffff;
  color: #4e5259;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  white-space: nowrap;
  cursor: pointer;
}

.filter-label {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.filter-caret {
  color: #8a8e96;
  transition: transform 0.18s ease;
}

.filter-caret.open {
  transform: rotate(180deg);
}

.filter-panel {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 20;
  min-width: 168px;
  padding: 8px;
  border: 1px solid #ddddda;
  border-radius: 10px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 0 4px;
  color: #232427;
  font-size: 13px;
  cursor: pointer;
}

.filter-option input {
  margin: 0;
}

.clear-btn {
  margin-top: 4px;
  min-height: 28px;
  border: 0;
  border-radius: 7px;
  background: #f4f5f7;
  color: #4e5259;
  font-size: 12px;
  cursor: pointer;
}

.filter-trigger:focus-visible,
.clear-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .filter-wrap {
    flex: 1 1 140px;
    min-width: 0;
  }

  .filter-trigger {
    width: 100%;
    justify-content: space-between;
  }

  .filter-label {
    max-width: none;
  }

  .filter-panel {
    width: 100%;
    min-width: 0;
  }
}
</style>
