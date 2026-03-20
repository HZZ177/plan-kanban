<template>
  <button class="board-card" :class="{ active }" type="button" @click="$emit('select')">
    <div class="card-title">{{ title }}</div>
    <div class="card-summary">{{ summary }}</div>
    <div class="card-meta">
      <span>{{ id }}</span>
      <span class="card-chip">{{ priority }}</span>
    </div>
  </button>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  summary: {
    type: String,
    required: true,
  },
  priority: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['select'])
</script>

<style scoped>
.board-card {
  width: 100%;
  text-align: left;
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  transition: background 160ms ease, border-color 160ms ease;
  cursor: pointer;
}

.board-card:hover {
  background: #f5f7fa;
  border-color: #cfd3d8;
}

.board-card.active {
  border-color: #c8ddff;
  background: #f7fbff;
}

.board-card:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

.card-title {
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.5;
  color: #232427;
}

.card-summary {
  margin-bottom: 8px;
  font-size: 12px;
  line-height: 1.55;
  color: #6f7279;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 11px;
  color: #94979d;
}

.card-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-height: 22px;
  padding: 0 8px;
  border: 1px solid #ddddda;
  border-radius: 999px;
  background: #ffffff;
  color: #666a73;
}

.card-chip::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.7;
}

@media (prefers-reduced-motion: reduce) {
  .board-card {
    transition: none !important;
  }
}
</style>
