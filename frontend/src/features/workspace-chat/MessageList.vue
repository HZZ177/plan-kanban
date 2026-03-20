<template>
  <div class="message-list">
    <template v-if="messages.length">
      <template v-for="(message, index) in messages" :key="`${message.role}-${message.time}-${index}`">
        <UserMessageItem
          v-if="message.role === 'user'"
          :label="message.label"
          :time="message.time"
          :content="message.content"
        />
        <AssistantMessageItem
          v-else-if="message.role === 'assistant'"
          :label="message.label"
          :time="message.time"
          :content="message.content"
        />
        <ToolMessageItem
          v-else-if="message.role === 'tool'"
          :label="message.label"
          :time="message.time"
          :content="message.content"
          :output="message.output || ''"
        />
        <ThinkingMessageItem
          v-else
          :label="message.label"
          :time="message.time"
          :content="message.content"
        />
      </template>
    </template>
    <div v-else class="empty-history">当前卡片还没有历史消息。</div>
  </div>
</template>

<script setup>
import AssistantMessageItem from './AssistantMessageItem.vue'
import ThinkingMessageItem from './ThinkingMessageItem.vue'
import ToolMessageItem from './ToolMessageItem.vue'
import UserMessageItem from './UserMessageItem.vue'

defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.message-list {
  display: grid;
  gap: 10px;
}

.empty-history {
  padding: 12px;
  border: 1px dashed #ddddda;
  border-radius: 8px;
  background: #fafafc;
  color: #6f7279;
  font-size: 12px;
}
</style>
