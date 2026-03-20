<template>
  <div v-if="open" class="modal-mask" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-head">
        <div>
          <div class="modal-title">新建需求</div>
        </div>
        <button class="close-btn" type="button" @click="$emit('close')">×</button>
      </div>
      <div class="form-grid">
        <label>
          <span>project_id</span>
          <input :value="form.project_id" type="text" @input="$emit('update:form', { ...form, project_id: $event.target.value })" />
        </label>
        <label>
          <span>标题</span>
          <input :value="form.title" type="text" @input="$emit('update:form', { ...form, title: $event.target.value })" />
        </label>
        <label>
          <span>负责人</span>
          <input :value="form.owner" type="text" @input="$emit('update:form', { ...form, owner: $event.target.value })" />
        </label>
        <label>
          <span>优先级</span>
          <select :value="form.priority" @change="$emit('update:form', { ...form, priority: $event.target.value })">
            <option value="P0">P0</option>
            <option value="P1">P1</option>
            <option value="P2">P2</option>
          </select>
        </label>
        <label class="full">
          <span>摘要</span>
          <textarea :value="form.summary" @input="$emit('update:form', { ...form, summary: $event.target.value })"></textarea>
        </label>
        <label class="full">
          <span>原始需求</span>
          <textarea :value="form.raw_requirement" @input="$emit('update:form', { ...form, raw_requirement: $event.target.value })"></textarea>
        </label>
      </div>
      <div class="modal-actions">
        <button class="ghost-btn" type="button" @click="$emit('close')">取消</button>
        <button
          class="primary-btn"
          type="button"
          :disabled="submitting || !form.project_id.trim() || !form.title.trim() || !form.owner.trim() || !form.summary.trim() || !form.raw_requirement.trim()"
          @click="$emit('submit')"
        >
          {{ submitting ? '创建中...' : '创建需求' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
  form: {
    type: Object,
    required: true,
  },
})

defineEmits(['close', 'submit', 'update:form'])
</script>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 30;
  background: rgba(15, 23, 42, 0.28);
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal-card {
  width: min(680px, 100%);
  max-height: calc(100vh - 40px);
  overflow: auto;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #d9dde3;
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.18);
  padding: 16px;
  display: grid;
  gap: 14px;
}

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #232427;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #ddddda;
  border-radius: 8px;
  background: #ffffff;
  cursor: pointer;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

label {
  display: grid;
  gap: 6px;
  font-size: 12px;
  color: #555962;
}

label.full {
  grid-column: 1 / -1;
}

input,
select,
textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #d7dbe2;
  border-radius: 8px;
  background: #ffffff;
  padding: 10px 12px;
  color: #232427;
}

textarea {
  min-height: 110px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.ghost-btn,
.primary-btn {
  min-height: 36px;
  padding: 0 14px;
  border-radius: 8px;
  cursor: pointer;
}

.ghost-btn {
  border: 1px solid #ddddda;
  background: #ffffff;
  color: #555962;
}

.primary-btn {
  border: 1px solid #b56018;
  background: #b56018;
  color: #ffffff;
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
