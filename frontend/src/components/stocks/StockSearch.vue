<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useWatchlistStore } from '../../stores/watchlist'
import WatchlistPanel from './WatchlistPanel.vue'

const store = useWatchlistStore()
const serverError = ref(false)
const loading = ref(true)

onMounted(async () => {
  try {
    await store.fetchWatchlist()
    store.startPolling()
    serverError.value = false
  } catch {
    serverError.value = true
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  store.stopPolling()
})
</script>

<template>
  <div class="space-y-5">
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="w-8 h-8 border-2 border-gray-600 border-t-blue-500 rounded-full animate-spin mb-3" />
      <span class="text-sm text-gray-500">加载中...</span>
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
      <p class="text-gray-500 text-sm mb-4">请在终端启动股票行情代理服务后刷新页面</p>
      <code class="inline-block bg-gray-800 px-4 py-2 rounded-lg text-xs text-gray-300 font-mono">
        cd server && node dev-server.js
      </code>
    </div>

    <!-- 空自选提示 -->
    <div
      v-else-if="store.items.length === 0"
      class="flex flex-col items-center justify-center py-20 text-gray-500"
    >
      <svg class="w-14 h-14 mb-4 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>
      <p class="text-sm font-bold mb-1">暂无自选股</p>
      <p class="text-xs text-gray-600">请在股票行情代理服务中添加自选</p>
    </div>

    <!-- 自选股面板 -->
    <WatchlistPanel v-else />
  </div>
</template>
