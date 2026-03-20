<template>
  <div class="submit-row">
    <div class="submit-left">
      <span class="composer-hint">Enter 发送，Shift + Enter 换行</span>
    </div>
    <div class="submit-right">
      <button class="send-btn" type="button" :disabled="disabled" @click="$emit('submit')">{{ submitting ? '发送中...' : '发送消息' }}</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['submit'])
</script>

<style scoped>
.submit-row {
  flex: 0 0 auto;
  padding: 0 14px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  background: #fafaf9;
}

.submit-left,
.submit-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}

.submit-left {
  flex: 1 1 220px;
}

.submit-right {
  flex: 0 0 auto;
  margin-left: auto;
  justify-content: flex-end;
}

.composer-hint {
  font-size: 12px;
  line-height: 1.5;
  color: #94979d;
}

.send-btn {
  min-height: 34px;
  padding: 0 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid #cfd9ea;
  background: #edf4ff;
  color: #2f61c2;
}

.send-btn:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.send-btn:hover {
  border-color: #cfd3d8;
}

.send-btn:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: 1px;
}

@media (max-width: 768px) {
  .submit-row {
    align-items: stretch;
  }

  .submit-left,
  .submit-right {
    width: 100%;
    flex: 1 1 100%;
    margin-left: 0;
  }

  .submit-right {
    justify-content: stretch;
  }

  .send-btn {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 520px) {
  .composer-hint {
    font-size: 11px;
  }
}
</style>
