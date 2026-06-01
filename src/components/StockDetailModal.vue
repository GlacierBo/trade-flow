<script setup>
import { computed } from 'vue'

const props = defineProps({
  stock: { type: Object, required: true },
})

const emit = defineEmits(['close'])

const priceClass = computed(() => {
  if (props.stock.percent > 0) return 'text-red-400'
  if (props.stock.percent < 0) return 'text-green-400'
  return 'text-gray-100'
})

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
  <div
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="emit('close')"
  >
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl animate-fadeIn">
      <!-- Header -->
      <div class="flex items-center justify-between p-5 border-b border-gray-700/50">
        <div class="flex items-baseline gap-3">
          <h2 class="text-xl font-black text-gray-100">{{ stock.name }}</h2>
          <span class="text-sm text-gray-500 font-mono">{{ stock.code }}</span>
        </div>
        <button
          class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors"
          @click="emit('close')"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Price Section -->
      <div class="p-5 text-center border-b border-gray-700/50">
        <div class="text-4xl font-black font-mono mb-2" :class="priceClass">
          {{ fmtPrice(stock.now) }}
        </div>
        <span
          class="inline-block px-3 py-1 rounded-lg text-sm font-bold font-mono"
          :class="{
            'bg-red-500/15 text-red-400': stock.percent > 0,
            'bg-green-500/15 text-green-400': stock.percent < 0,
            'bg-gray-600/30 text-gray-400': !stock.percent,
          }"
        >
          {{ fmtPercent(stock.percent) }}
        </span>
      </div>

      <!-- Detail Grid -->
      <div class="grid grid-cols-2 gap-px bg-gray-700/30">
        <div class="bg-gray-800/50 p-4">
          <div class="text-xs text-gray-500 mb-1">昨收</div>
          <div class="text-base font-bold font-mono text-gray-100">{{ fmtPrice(stock.yesterday) }}</div>
        </div>
        <div class="bg-gray-800/50 p-4">
          <div class="text-xs text-gray-500 mb-1">最高</div>
          <div class="text-base font-bold font-mono text-red-400">{{ fmtPrice(stock.high) }}</div>
        </div>
        <div class="bg-gray-800/50 p-4">
          <div class="text-xs text-gray-500 mb-1">最低</div>
          <div class="text-base font-bold font-mono text-green-400">{{ fmtPrice(stock.low) }}</div>
        </div>
        <div class="bg-gray-800/50 p-4">
          <div class="text-xs text-gray-500 mb-1">数据源</div>
          <div class="text-base font-bold text-gray-100">东方财富</div>
        </div>
      </div>
    </div>
  </div>
</template>
