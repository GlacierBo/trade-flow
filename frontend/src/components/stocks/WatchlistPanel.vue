<script setup>
import { computed, ref } from 'vue'
import { useWatchlistStore } from '../../stores/watchlist'

const store = useWatchlistStore()
const removing = ref(null) // 当前正在删除的 code
const selectedItem = ref(null) // 点开的卡片
const copied = ref(false)

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

function openCard(item) {
  selectedItem.value = item
  copied.value = false
}

function closeCard() {
  selectedItem.value = null
}

async function copyCode() {
  if (!selectedItem.value) return
  const text = `${selectedItem.value.code}-${selectedItem.value.name}`
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
  }
}
</script>

<template>
  <div>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
      <div
        v-for="item in store.items"
        :key="item.code"
        class="bg-gray-800/30 border border-gray-700/30 border-l-4 rounded-lg p-3 transition-all duration-200 hover:bg-gray-700/30 hover:shadow-lg hover:shadow-black/20 active:scale-[0.98] cursor-pointer"
        :class="[bgClass(changePercent(item)), changePercent(item) > 0 ? 'glow-up' : changePercent(item) < 0 ? 'glow-down' : '']"
        @click="openCard(item)"
      >
        <div class="flex items-start justify-between mb-2">
          <div class="min-w-0">
            <div class="flex items-baseline gap-1.5">
              <span class="text-sm font-bold text-gray-100 truncate">{{ item.name }}</span>
              <span class="text-[10px] text-gray-500 font-mono flex-shrink-0">{{ item.code }}</span>
            </div>
          </div>
          <button
            class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-lg transition-colors"
            :class="removing === item.code ? 'text-gray-600' : 'text-gray-500 hover:text-red-400 hover:bg-red-500/10'"
            :title="'删除 ' + item.name"
            :aria-label="'删除 ' + item.name"
            :disabled="removing === item.code"
            @click.stop="handleRemove(item.code)"
          >
            <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="flex items-baseline gap-2 mb-2">
          <span class="text-xl font-bold font-mono tabular-nums" :class="pctClass(changePercent(item))">
            {{ fmtPrice(item.price) }}
          </span>
          <span
            class="px-1.5 py-0.5 rounded text-[10px] font-bold font-mono"
            :class="{
              'bg-red-500/15 text-red-400': changePercent(item) > 0,
              'bg-green-500/15 text-green-400': changePercent(item) < 0,
              'bg-gray-600/30 text-gray-400': !changePercent(item),
            }"
          >
            {{ fmtPercent(changePercent(item)) }}
          </span>
        </div>

        <div class="flex items-center gap-3 text-[11px]">
          <div class="flex gap-1">
            <span class="text-gray-500">涨跌</span>
            <span class="font-mono font-medium" :class="pctClass(changePercent(item))">{{ fmtPrice(change(item)) }}</span>
          </div>
          <div class="flex gap-1">
            <span class="text-gray-500">昨收</span>
            <span class="text-gray-300 font-mono font-medium">{{ fmtPrice(item.yesterday) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 卡片详情弹窗 -->
    <Teleport to="body">
      <div
        v-if="selectedItem"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
            >
        <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-xs overflow-hidden shadow-2xl animate-fadeIn">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
            <h3 class="text-base font-black text-gray-100">自选详情</h3>
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors"
              @click="closeCard"
              aria-label="关闭"
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <div class="p-5 space-y-4">
            <div class="bg-gray-700/30 rounded-xl p-4 text-center">
              <div class="flex items-baseline justify-center gap-2 mb-2">
                <span class="text-lg font-bold text-gray-100">{{ selectedItem.name }}</span>
                <span class="text-sm text-gray-500 font-mono">{{ selectedItem.code }}</span>
              </div>
              <div class="flex items-baseline justify-center gap-2">
                <span class="text-2xl font-bold font-mono" :class="pctClass(changePercent(selectedItem))">
                  {{ fmtPrice(selectedItem.price) }}
                </span>
                <span
                  class="px-1.5 py-0.5 rounded text-xs font-bold font-mono"
                  :class="{
                    'bg-red-500/15 text-red-400': changePercent(selectedItem) > 0,
                    'bg-green-500/15 text-green-400': changePercent(selectedItem) < 0,
                    'bg-gray-600/30 text-gray-400': !changePercent(selectedItem),
                  }"
                >
                  {{ fmtPercent(changePercent(selectedItem)) }}
                </span>
              </div>
            </div>

            <div class="bg-gray-700/20 rounded-xl p-3">
              <div class="text-xs text-gray-400 font-bold mb-2">合约信息</div>
              <div
                class="flex items-center justify-between bg-gray-800/50 border border-gray-600/50 rounded-lg px-3 py-2.5 cursor-pointer hover:border-blue-500/40 transition-all group"
                @click="copyCode"
              >
                <code class="text-sm font-mono text-gray-200 select-all">{{ selectedItem.code }}-{{ selectedItem.name }}</code>
                <span
                  v-if="copied"
                  class="text-xs text-green-400 font-bold flex-shrink-0 ml-2"
                >已复制</span>
                <svg v-else class="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors flex-shrink-0 ml-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
              </div>
            </div>
          </div>
          <div class="px-5 pb-5">
            <button
              class="w-full py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all"
              @click="copyCode"
            >
              {{ copied ? '✓ 已复制' : '复制合约信息' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
