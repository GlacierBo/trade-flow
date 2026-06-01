<script setup>
import { computed } from 'vue'
import { useWatchlistStore } from '../stores/watchlist'

const emit = defineEmits(['stock-click', 'toggle-watch'])
const store = useWatchlistStore()

const lastUpdatedText = computed(() => {
  if (!store.lastRefreshed) return ''
  const d = new Date(store.lastRefreshed)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
})

function change(item) {
  return item.latestPrice - item.basePrice
}

function changePercent(item) {
  if (!item.basePrice) return 0
  return (item.latestPrice - item.basePrice) / item.basePrice
}

function pctClass(pct) {
  if (pct > 0) return 'text-red-400'
  if (pct < 0) return 'text-green-400'
  return 'text-gray-400'
}

function bgClass(pct) {
  if (pct > 0) return 'border-l-red-500/60'
  if (pct < 0) return 'border-l-green-500/60'
  return 'border-l-gray-600'
}

function fmtPrice(v) {
  if (!v && v !== 0) return '--'
  return Number(v).toFixed(2)
}

function fmtPercent(v) {
  if (!v && v !== 0) return '0.00%'
  const sign = v > 0 ? '+' : ''
  return `${sign}${(v * 100).toFixed(2)}%`
}
</script>

<template>
  <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden">
    <div class="flex items-center justify-between px-5 py-3.5 border-b border-gray-700/50">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-400" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
        <h3 class="text-sm font-black text-gray-200">我的自选</h3>
        <span class="bg-blue-500/20 text-blue-400 text-xs font-bold px-2 py-0.5 rounded-full">
          {{ store.items.length }}
        </span>
      </div>
      <div class="text-xs text-gray-500">
        <span v-if="store.loading" class="text-blue-400">刷新中...</span>
        <span v-else-if="lastUpdatedText">上次更新 {{ lastUpdatedText }}</span>
      </div>
    </div>

    <div class="divide-y divide-gray-700/30">
      <div
        v-for="item in store.items"
        :key="item.code"
        class="flex items-center gap-3 px-5 py-3 border-l-4 cursor-pointer transition-colors hover:bg-gray-700/30"
        :class="bgClass(changePercent(item))"
        @click="emit('stock-click', { code: item.code, name: item.name, now: item.latestPrice, ...item })"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline gap-2">
            <span class="text-sm font-bold text-gray-200 truncate">{{ item.name }}</span>
            <span class="text-xs text-gray-500 font-mono flex-shrink-0">{{ item.code }}</span>
          </div>
        </div>
        <div class="text-right flex-shrink-0">
          <div class="text-sm font-bold font-mono" :class="pctClass(changePercent(item))">
            {{ fmtPrice(item.latestPrice) }}
          </div>
          <div class="text-xs font-mono" :class="pctClass(changePercent(item))">
            {{ fmtPrice(change(item)) }} ({{ fmtPercent(changePercent(item)) }})
          </div>
        </div>
        <button
          class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          :title="'删除 ' + item.name"
          @click.stop="store.remove(item.code)"
        >
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
