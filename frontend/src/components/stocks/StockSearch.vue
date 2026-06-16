<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useWatchlistStore } from '../../stores/watchlist'
import { useStocksStore } from '../../stores/stocks'
import { useStockStore } from '../../stores/stock'
import SearchBar from './SearchBar.vue'
import StockGrid from './StockGrid.vue'
import StockDetailModal from './StockDetailModal.vue'
import WatchlistPanel from './WatchlistPanel.vue'
import DataTransfer from '../common/DataTransfer.vue'

const watchlistStore = useWatchlistStore()
const stocksStore = useStocksStore()
const store = useStockStore()

const serverError = ref(false)
const loading = ref(true)
const selectedStock = ref(null)
const watchlistCollapsed = ref(true)

onMounted(async () => {
  try {
    await watchlistStore.fetchWatchlist()
    watchlistStore.startPolling()
    serverError.value = false
  } catch {
    serverError.value = true
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  watchlistStore.stopPolling()
})

function onStockClick(stock) {
  selectedStock.value = stock
}

async function onToggleWatch(stock) {
  if (watchlistStore.isWatched(stock.code)) {
    await watchlistStore.remove(stock.code)
    store.showToast(`已取消自选 ${stock.name}`, 'success')
  } else {
    await watchlistStore.add(stock.code, stock.name)
    store.showToast(`已添加自选 ${stock.name}`, 'success')
  }
}
</script>

<template>
  <div class="space-y-5">
    <!-- 搜索栏 -->
    <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 p-5">
      <SearchBar />
    </div>

    <!-- 搜索结果 -->
    <div v-if="stocksStore.results.length > 0" class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 p-5">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <div class="w-1 h-5 bg-blue-500 rounded-full" />
          <h2 class="text-base font-black text-gray-100 tracking-tight">搜索结果</h2>
        </div>
        <div class="flex items-center gap-2">
          <DataTransfer
            page-name="自选"
            :get-export-data="() => ({ watchlist: watchlistStore.items })"
            :on-import="async (data) => {
              if (data.watchlist) {
                watchlistStore.items = data.watchlist
                store.showToast('数据导入完成', 'success')
              }
            }"
          />
          <button
            @click="stocksStore.clearResults()"
            class="text-xs text-gray-400 hover:text-gray-200 transition"
          >清除结果</button>
        </div>
      </div>
      <StockGrid
        :stocks="stocksStore.results"
        :watched-codes="watchlistStore.codes"
        @stock-click="onStockClick"
        @toggle-watch="onToggleWatch"
      />
    </div>

    <!-- 搜索加载中 -->
    <div v-else-if="stocksStore.loading" class="flex items-center justify-center py-12">
      <div class="w-6 h-6 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin mr-3" />
      <span class="text-sm text-gray-400">搜索中…</span>
    </div>

    <!-- 自选股面板 -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin mb-3" />
      <span class="text-sm text-gray-500">加载中…</span>
    </div>

    <!-- 服务未连接提示 -->
    <div
      v-else-if="serverError"
      class="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-8 text-center"
    >
      <svg class="w-14 h-14 mx-auto mb-4 text-amber-400/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
        <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
        <line x1="6" y1="6" x2="6.01" y2="6" />
        <line x1="6" y1="18" x2="6.01" y2="18" />
      </svg>
      <p class="text-amber-400 font-bold text-base mb-2">自选股服务未运行</p>
      <p class="text-gray-500 text-sm mb-4">请确保后端服务已启动</p>
      <code class="inline-block bg-gray-800 px-4 py-2 rounded-lg text-xs text-gray-300 font-mono">
        cd backend && python -m app.main
      </code>
    </div>

    <!-- 自选股列表 -->
    <div v-if="watchlistStore.items.length === 0 && !loading && !serverError" class="flex flex-col items-center justify-center py-16 text-gray-500">
      <svg class="w-12 h-12 mb-3 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
      <p class="text-sm font-bold mb-1">暂无自选股</p>
      <p class="text-xs text-gray-600">搜索并添加您关注的股票</p>
    </div>
    <div v-else-if="!loading && !serverError && !watchlistCollapsed">
      <!-- Tab 样式的标题栏 -->
      <div class="flex items-center justify-between pb-2 mb-3" style="border-bottom: 1px solid rgba(55,65,81,0.3);">
        <button class="flex items-center gap-2 group cursor-pointer bg-transparent border-none p-0" @click="watchlistCollapsed = true" aria-label="收起自选">
          <span class="text-sm font-bold text-gray-200 relative pb-1 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-0.5 after:bg-gradient-to-r after:from-amber-400 after:to-amber-300 after:rounded-full">我的自选</span>
          <span class="bg-gradient-to-r from-amber-400/20 to-amber-300/20 text-amber-400 text-xs font-bold px-2 py-0.5 rounded-full shadow-sm shadow-amber-500/10">{{ watchlistStore.items.length }}</span>
        </button>
        <button
          class="w-6 h-6 flex items-center justify-center rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700/50 transition-all duration-200"
          @click="watchlistCollapsed = true"
          aria-label="收起"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
      </div>
      <WatchlistPanel />
    </div>

    <!-- 收起状态的悬浮按钮 -->
    <button
      v-if="watchlistCollapsed && watchlistStore.items.length > 0 && !loading && !serverError"
      class="fixed bottom-6 right-6 z-40 flex items-center gap-2.5 px-5 py-3 bg-gray-800/90 backdrop-blur-sm border border-gray-700/50 rounded-full shadow-2xl shadow-black/40 hover:bg-gray-700 hover:border-gray-600/60 hover:shadow-blue-500/10 transition-all duration-200 active:scale-95 group"
      @click="watchlistCollapsed = false"
    >
      <svg class="w-4 h-4 text-amber-400 transition-transform group-hover:scale-110 duration-200" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
      <span class="text-sm font-bold text-gray-200">我的自选</span>
      <span class="bg-gradient-to-r from-amber-400/20 to-amber-300/20 text-amber-400 text-xs font-bold px-2 py-0.5 rounded-full">{{ watchlistStore.items.length }}</span>
    </button>

    <!-- 股票详情弹窗 -->
    <StockDetailModal
      v-if="selectedStock"
      :stock="selectedStock"
      :is-watched="watchlistStore.isWatched(selectedStock?.code)"
      @close="selectedStock = null"
      @toggle-watch="onToggleWatch"
    />
  </div>
</template>
