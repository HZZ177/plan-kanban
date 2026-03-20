<template>
  <section class="column" :aria-label="title">
    <header class="column-head">
      <div class="column-left">
        <span class="stage-dot" :style="{ background: color }" />
        <span class="column-title">{{ title }}</span>
        <span class="column-count">{{ cards.length || '' }}</span>
      </div>
    </header>
    <div class="column-body">
      <template v-if="cards.length">
        <RequestCard
          v-for="card in cards"
          :key="card.id"
          :id="card.id"
          :title="card.title"
          :summary="card.summary"
          :priority="card.priority"
          :active="card.id === activeCardId"
          @select="$emit('select', card.id)"
        />
      </template>
      <EmptyState v-else />
    </div>
  </section>
</template>

<script setup>
import EmptyState from './EmptyState.vue'
import RequestCard from './RequestCard.vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
  color: {
    type: String,
    required: true,
  },
  cards: {
    type: Array,
    required: true,
  },
  activeCardId: {
    type: String,
    default: '',
  },
})

defineEmits(['select'])
</script>

<style scoped>
.column {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #ddddda;
  background: #ffffff;
}

.column:last-child {
  border-right: 0;
}

.column-head {
  flex: 0 0 46px;
  min-height: 46px;
  padding: 0 10px;
  border-bottom: 1px solid #ddddda;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background: #ffffff;
  position: sticky;
  top: 0;
  z-index: 2;
}

.column-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.stage-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  flex: 0 0 auto;
}

.column-title {
  overflow: hidden;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.column-count {
  font-size: 11px;
  color: #94979d;
}

.column-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  display: grid;
  align-content: start;
  gap: 8px;
  background: #ffffff;
  overscroll-behavior: contain;
}
</style>
