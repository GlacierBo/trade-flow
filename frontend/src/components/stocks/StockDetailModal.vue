<script setup>
import { computed } from 'vue'

const props = defineProps({
  stock: { type: Object, required: true },
})

const emit = defineEmits(['close'])

const changePct = computed(() => props.stock.changePercent ?? props.stock.percent)

const priceClass = computed(() => {
  if (changePct.value > 0) return 'text-red-400'
  if (changePct.value < 0) return 'text-green-400'
  return 'text-gray-100'
})

const isUp = computed(() => changePct.value > 0)
const isDown = computed(() => changePct.value < 0)

function fmtPrice(v) {
  if (!v && v !== 0) return '--'
  return Number(v).toFixed(2)
}

function fmtPercent(v) {
  if (!v && v !== 0) return '0.00%'
  const sign = v > 0 ? '+' : ''
  return `${sign}${v.toFixed(2)}%`
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
  >
    <div class="bg-gray-800/95 backdrop-blur-xl border border-gray-700/50 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl shadow-black/40 animate-fadeInScale">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/40">
        <div class="flex items-baseline gap-3">
          <h2 class="text-xl font-black text-gray-100 tracking-tight">{{ stock.name }}</h2>
          <span class="text-sm text-gray-500 font-mono">{{ stock.code }}</span>
        </div>
        <button
          class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700/70 transition-all duration-200"
          @click="emit('close')"
          aria-label="关闭"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Price Section -->
      <div class="p-6 text-center border-b border-gray-700/30 bg-gradient-to-b from-gray-800/60 to-transparent">
        <div class="text-5xl font-black font-mono tracking-tight mb-3" :class="priceClass">
          {{ fmtPrice(stock.price ?? stock.now) }}
        </div>
        <span
          class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm font-bold font-mono"
          :class="{
            'bg-red-500/15 text-red-400': isUp,
            'bg-green-500/15 text-green-400': isDown,
            'bg-gray-600/30 text-gray-400': !changePct,
          }"
        >
          <svg v-if="isUp" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><polyline points="18 15 12 9 6 15" /></svg>
          <svg v-else-if="isDown" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><polyline points="6 9 12 15 18 9" /></svg>
          <span v-else class="w-3.5 h-3.5 inline-block">—</span>
          {{ fmtPercent(changePct) }}
        </span>
      </div>

      <!-- Detail Grid -->
      <div class="p-5">
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-gray-700/20 rounded-xl p-4">
            <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /></svg>
              昨收
            </div>
            <div class="text-lg font-bold font-mono text-gray-100">{{ fmtPrice(stock.yesterday) }}</div>
          </div>
          <div class="bg-red-500/5 rounded-xl p-4 border border-red-500/10">
            <div class="flex items-center gap-1.5 text-xs text-red-400/70 mb-2">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15" /></svg>
              最高
            </div>
            <div class="text-lg font-bold font-mono text-red-400">{{ fmtPrice(stock.high) }}</div>
          </div>
          <div class="bg-green-500/5 rounded-xl p-4 border border-green-500/10">
            <div class="flex items-center gap-1.5 text-xs text-green-400/70 mb-2">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9" /></svg>
              最低
            </div>
            <div class="text-lg font-bold font-mono text-green-400">{{ fmtPrice(stock.low) }}</div>
          </div>
          <div class="bg-gray-700/20 rounded-xl p-4">
            <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></svg>
              数据源
            </div>
            <div class="text-lg font-bold font-mono text-gray-100">东方财富</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
