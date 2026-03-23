<template>
  <div class="message-list">
    <template v-if="messages.length">
      <template
        v-for="message in messages"
        :key="message.id"
      >
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
          :streaming="Boolean(message.streaming)"
          :is-finished="Boolean(message.isFinished)"
        />
        <GhostEventItem
          v-else-if="message.role === 'ghost'"
          :title="message.content"
          :time="message.time"
          :content="message.entryType === 'thinking' ? message.content : ''"
          :kind="message.ghostKind || 'summary'"
          :payload="message.payload || null"
          :default-expanded="message.entryType === 'thinking'"
          :streaming="Boolean(message.streaming)"
          :is-finished="Boolean(message.isFinished)"
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
    <div
      v-else
      class="empty-history"
    >
      当前卡片还没有历史消息。
    </div>
  </div>
</template>

<script setup>
import AssistantMessageItem from './AssistantMessageItem.vue'
import GhostEventItem from './GhostEventItem.vue'
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
  min-width: 0;
  display: grid;
  gap: 8px;
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
