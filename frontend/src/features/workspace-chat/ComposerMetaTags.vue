<template>
  <div class="composer-meta" :class="{ empty: tags.length === 0 }">
    <span v-for="tag in tags" :key="tag" class="composer-tag">{{ tag }}</span>
  </div>
</template>

<script setup>
defineProps({
  tags: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.composer-meta {
  flex: 0 0 auto;
  padding: 8px 14px 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  background: #fafaf9;
}

.composer-meta.empty {
  display: none;
}

.composer-tag {
  min-height: 26px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 999px;
  background: #ffffff;
  font-size: 12px;
  color: #666a73;
  display: inline-flex;
  align-items: center;
}

@media (max-width: 520px) {
  .composer-tag {
    min-height: 24px;
  }
}
</style>
