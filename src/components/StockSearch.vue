<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStocksStore } from '../stores/stocks'
import { useWatchlistStore } from '../stores/watchlist'
import SearchBar from './SearchBar.vue'
import StockGrid from './StockGrid.vue'
import StockDetailModal from './StockDetailModal.vue'
import WatchlistPanel from './WatchlistPanel.vue'

const stocksStore = useStocksStore()
const watchlistStore = useWatchlistStore()

const selectedStock = ref(null)

onMounted(() => {
  if (watchlistStore.items.length > 0) {
    watchlistStore.startPolling()
  }
})

onUnmounted(() => {
  watchlistStore.stopPolling()
})

function handleStockClick(stock) {
  selectedStock.value = stock
}

function handleToggleWatch(stock) {
  if (watchlistStore.isWatched(stock.code)) {
    watchlistStore.remove(stock.code)
  } else {
    watchlistStore.add(stock)
  }
}

function handleRetry() {
  stocksStore.clearError()
  if (stocksStore.lastKeyword) {
    stocksStore.search(stocksStore.lastKeyword)
  }
}

function closeDetail() {
  selectedStock.value = null
}
</script>

<template>
  <div class="space-y-5">
    <div class="bg-gray-800/50 rounded-2xl p-5 border border-gray-700/50">
      <SearchBar />
    </div>

    <WatchlistPanel
      v-if="watchlistStore.items.length > 0"
      @stock-click="handleStockClick"
      @toggle-watch="handleToggleWatch"
    />

    <!-- Error -->
    <div
      v-if="stocksStore.error"
      class="flex items-center gap-3 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3"
    >
      <svg class="w-5 h-5 text-red-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
      </svg>
      <span class="text-sm text-red-400 flex-1">{{ stocksStore.error }}</span>
      <button
        class="px-3 py-1 text-xs font-bold text-red-400 border border-red-400/50 rounded-lg hover:bg-red-500/10 transition-colors"
        @click="handleRetry"
      >
        重试
      </button>
    </div>

    <!-- Loading -->
    <div v-if="stocksStore.loading" class="flex flex-col items-center justify-center py-16">
      <div class="w-8 h-8 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin mb-3" />
      <span class="text-sm text-gray-500">搜索中...</span>
    </div>

    <!-- Results -->
    <template v-else-if="!stocksStore.error">
      <div
        v-if="stocksStore.results.length === 0"
        class="flex flex-col items-center justify-center py-20 text-gray-500"
      >
        <svg class="w-16 h-16 mb-4 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 3v18h18" /><path d="M7 16l4-8 4 4 6-10" />
        </svg>
        <p class="text-sm">
          {{ stocksStore.lastKeyword ? '未找到相关股票' : '输入股票代码或名称开始搜索' }}
        </p>
      </div>
      <StockGrid
        v-else
        :stocks="stocksStore.results"
        :watched-codes="watchlistStore.codes"
        @stock-click="handleStockClick"
        @toggle-watch="handleToggleWatch"
      />
    </template>

    <!-- Detail Modal -->
    <StockDetailModal
      v-if="selectedStock"
      :stock="selectedStock"
      @close="closeDetail"
    />
  </div>
</template>
