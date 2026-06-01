<script setup>
import { computed } from 'vue'

const props = defineProps({
  stock: { type: Object, required: true },
  isWatched: { type: Boolean, default: false },
})

const emit = defineEmits(['click', 'toggle-watch'])

const priceClass = computed(() => {
  if (props.stock.percent > 0) return 'text-red-400'
  if (props.stock.percent < 0) return 'text-green-400'
  return 'text-gray-100'
})

const bgBorderClass = computed(() => {
  if (props.stock.percent > 0) return 'border-l-red-500/60'
  if (props.stock.percent < 0) return 'border-l-green-500/60'
  return 'border-l-gray-600'
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
    class="bg-gray-800/50 border border-gray-700/50 border-l-4 rounded-xl p-4 cursor-pointer transition-all hover:bg-gray-700/50 hover:shadow-lg hover:shadow-black/20 active:scale-[0.98]"
    :class="bgBorderClass"
    @click="emit('click', stock)"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="min-w-0">
        <div class="flex items-baseline gap-2">
          <span class="text-base font-bold text-gray-100 truncate">{{ stock.name }}</span>
          <span class="text-xs text-gray-500 font-mono flex-shrink-0">{{ stock.code }}</span>
        </div>
      </div>
      <button
        class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg transition-colors"
        :class="isWatched ? 'text-amber-400 hover:bg-amber-400/10' : 'text-gray-500 hover:text-amber-400 hover:bg-amber-400/10'"
        :title="isWatched ? '取消自选' : '加自选'"
        @click.stop="emit('toggle-watch', stock)"
      >
        <svg viewBox="0 0 24 24" width="16" height="16" :fill="isWatched ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </button>
    </div>

    <div class="flex items-baseline gap-3 mb-3">
      <span class="text-2xl font-bold font-mono" :class="priceClass">
        {{ fmtPrice(stock.now) }}
      </span>
      <span
        class="px-2 py-0.5 rounded text-xs font-bold font-mono"
        :class="{
          'bg-red-500/15 text-red-400': stock.percent > 0,
          'bg-green-500/15 text-green-400': stock.percent < 0,
          'bg-gray-600/30 text-gray-400': !stock.percent,
        }"
      >
        {{ fmtPercent(stock.percent) }}
      </span>
    </div>

    <div class="flex items-center gap-4 text-xs">
      <div class="flex gap-1.5">
        <span class="text-gray-500">最高</span>
        <span class="text-gray-300 font-mono font-medium">{{ fmtPrice(stock.high) }}</span>
      </div>
      <div class="flex gap-1.5">
        <span class="text-gray-500">最低</span>
        <span class="text-gray-300 font-mono font-medium">{{ fmtPrice(stock.low) }}</span>
      </div>
      <div class="flex gap-1.5">
        <span class="text-gray-500">昨收</span>
        <span class="text-gray-300 font-mono font-medium">{{ fmtPrice(stock.yesterday) }}</span>
      </div>
    </div>
  </div>
</template>
