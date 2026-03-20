<template>
  <div class="columns">
    <StageColumn
      v-for="column in columns"
      :key="column.key"
      :title="column.title"
      :color="column.color"
      :cards="column.cards"
      :active-card-id="store.activeCardId"
      @select="onSelect"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCardStore } from '../../stores/cardStore'
import { showErrorMessage } from '../../utils/message'
import StageColumn from './StageColumn.vue'

const store = useCardStore()
const { columns } = storeToRefs(store)

const onSelect = async (cardId) => {
  try {
    await store.selectCard(cardId)
  } catch (error) {
    showErrorMessage(error, '加载工作区失败')
  }
}

onMounted(async () => {
  if (!store.cards.length) {
    try {
      await store.loadKanban()
    } catch (error) {
      showErrorMessage(error, '加载看板失败')
    }
  }
})
</script>

<style scoped>
.columns {
  min-width: 960px;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(5, minmax(210px, 1fr));
  align-items: stretch;
}
</style>

