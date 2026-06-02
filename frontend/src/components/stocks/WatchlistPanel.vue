<script setup>
import { computed, ref } from 'vue'
import { useWatchlistStore } from '../../stores/watchlist'

const store = useWatchlistStore()
const removing = ref(null) // 当前正在删除的 code

const lastUpdatedText = computed(() => {
  if (!store.lastRefreshed) return ''
  const d = new Date(store.lastRefreshed)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
})

function change(item) {
  if (!item.yesterday) return 0
  return item.price - item.yesterday
}

function changePercent(item) {
  if (!item.changePercent && item.changePercent !== 0) return 0
  return item.changePercent / 100
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

async function handleRemove(code) {
  if (removing.value) return
  removing.value = code
  try {
    await store.remove(code)
  } finally {
    removing.value = null
  }
}
</script>

<template>
  <div class="bg-gray-800/50 rounded-b-2xl border border-t-0 border-gray-700/50 overflow-hidden">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4">
      <div
        v-for="item in store.items"
        :key="item.code"
        class="bg-gray-800/50 border border-gray-700/50 border-l-4 rounded-xl p-4 transition-all hover:bg-gray-700/50 hover:shadow-lg hover:shadow-black/20"
        :class="bgClass(changePercent(item))"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="min-w-0">
            <div class="flex items-baseline gap-2">
              <span class="text-base font-bold text-gray-100 truncate">{{ item.name }}</span>
              <span class="text-xs text-gray-500 font-mono flex-shrink-0">{{ item.code }}</span>
            </div>
          </div>
          <button
            class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg transition-colors"
            :class="removing === item.code ? 'text-gray-600' : 'text-gray-500 hover:text-red-400 hover:bg-red-500/10'"
            :title="'删除 ' + item.name"
            :disabled="removing === item.code"
            @click="handleRemove(item.code)"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="flex items-baseline gap-3 mb-3">
          <span class="text-2xl font-bold font-mono" :class="pctClass(changePercent(item))">
            {{ fmtPrice(item.price) }}
          </span>
          <span
            class="px-2 py-0.5 rounded text-xs font-bold font-mono"
            :class="{
              'bg-red-500/15 text-red-400': changePercent(item) > 0,
              'bg-green-500/15 text-green-400': changePercent(item) < 0,
              'bg-gray-600/30 text-gray-400': !changePercent(item),
            }"
          >
            {{ fmtPercent(changePercent(item)) }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-xs">
          <div class="flex gap-1.5">
            <span class="text-gray-500">涨跌</span>
            <span class="font-mono font-medium" :class="pctClass(changePercent(item))">{{ fmtPrice(change(item)) }}</span>
          </div>
          <div class="flex gap-1.5">
            <span class="text-gray-500">昨收</span>
            <span class="text-gray-300 font-mono font-medium">{{ fmtPrice(item.yesterday) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
