<template>
  <div class="chip-row">
    <span class="chip"><span class="mini-dot" :style="{ background: stageColor }" />{{ stageTitle }}</span>
    <span class="chip">{{ priority }}</span>
    <span class="chip">{{ owner }}</span>
  </div>
</template>

<script setup>
defineProps({
  stageTitle: {
    type: String,
    default: '',
  },
  stageColor: {
    type: String,
    default: '#4c8bf5',
  },
  priority: {
    type: String,
    default: '',
  },
  owner: {
    type: String,
    default: '',
  },
})
</script>

<style scoped>
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.chip {
  min-height: 30px;
  padding: 0 10px;
  border: 1px solid #ddddda;
  border-radius: 999px;
  background: #f1f2f4;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4f535b;
}

.mini-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}
</style>
