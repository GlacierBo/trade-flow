<script setup>
import StockCard from './StockCard.vue'

defineProps({
  stocks: { type: Array, default: () => [] },
  watchedCodes: { type: Array, default: () => [] },
})

const emit = defineEmits(['stock-click', 'toggle-watch'])
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
    <StockCard
      v-for="stock in stocks"
      :key="stock.code"
      :stock="stock"
      :is-watched="watchedCodes.includes(stock.code)"
      @click="emit('stock-click', stock)"
      @toggle-watch="emit('toggle-watch', $event)"
    />
  </div>
</template>
