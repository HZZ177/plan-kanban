<template>
  <div class="composer-panel">
    <div class="composer-wrap">
      <div class="composer-box">
        <textarea
          :value="modelValue"
          placeholder="输入消息..."
          @input="$emit('update:modelValue', $event.target.value)"
          @keydown.enter.exact.prevent="$emit('submit')"
        ></textarea>
      </div>
    </div>
    <ComposerSubmitRow :disabled="disabled" :submitting="submitting" @submit="$emit('submit')" />
  </div>
</template>

<script setup>
import ComposerSubmitRow from './ComposerSubmitRow.vue'

defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['update:modelValue', 'submit'])
</script>

<style scoped>
.composer-panel {
  flex: 0 0 auto;
  width: 100%;
  overflow: hidden;
  border-top: 1px solid #ddddda;
  background: #fafaf9;
  display: flex;
  flex-direction: column;
}

.composer-wrap {
  flex: 0 0 auto;
  padding: 12px 14px 12px;
  background: #fafaf9;
  width: 100%;
  min-width: 0;
}

.composer-box {
  width: 100%;
  max-width: 100%;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

textarea {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  min-height: 120px;
  resize: none;
  border: 0;
  padding: 12px 14px;
  line-height: 1.7;
  display: block;
  background: #ffffff;
  box-sizing: border-box;
  color: #232427;
}

textarea:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: -2px;
}

@media (max-width: 520px) {
  textarea {
    min-height: 104px;
  }
}
</style>

