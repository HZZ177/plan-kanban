<template>
  <div class="summary-grid">
    <div class="summary-box">
      <div class="summary-label">当前阶段</div>
      <div class="summary-value">{{ stageTitle || '—' }}</div>
    </div>
    <div class="summary-box">
      <div class="summary-label">优先级</div>
      <div class="summary-value">{{ priority || '—' }}</div>
    </div>
    <div class="summary-box full-width">
      <div class="summary-label">负责人</div>
      <div class="summary-value">{{ owner || '—' }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stageTitle: {
    type: String,
    default: '',
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
.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.summary-box {
  padding: 10px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
}

.full-width {
  grid-column: 1 / -1;
}

.summary-label {
  margin-bottom: 6px;
  font-size: 11px;
  color: #94979d;
}

.summary-value {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.5;
  color: #42454b;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }
}
</style>
