<template>
  <div class="composer-panel">
    <div class="composer-wrap">
      <div class="composer-box">
        <textarea
          :value="modelValue"
          placeholder="输入消息..."
          @input="$emit('update:modelValue', $event.target.value)"
          @keydown.enter.exact.prevent="$emit('submit')"
        />
      </div>
    </div>
    <ComposerSubmitRow
      :disabled="disabled"
      :submitting="submitting"
      @submit="$emit('submit')"
    />
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
  height: 100%;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  background: #fafaf9;
  display: flex;
  flex-direction: column;
}

.composer-wrap {
  flex: 1;
  min-height: 0;
  padding: 12px 14px 12px;
  background: #fafaf9;
  width: 100%;
  min-width: 0;
}

.composer-box {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
  max-width: 100%;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

textarea {
  width: 100%;
  height: 100%;
  max-width: 100%;
  min-width: 0;
  min-height: 0;
  resize: none;
  border: 0;
  padding: 12px 14px;
  line-height: 1.7;
  font-size: 12px;
  display: block;
  background: #ffffff;
  box-sizing: border-box;
  color: #232427;
  overflow: auto;
}

textarea::placeholder {
  color: #9aa0a8;
}

textarea:focus-visible {
  outline: 2px solid rgba(76, 139, 245, 0.26);
  outline-offset: -2px;
}
</style>
