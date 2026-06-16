<script setup>
import { computed } from 'vue'

const props = defineProps({
  stock: { type: Object, required: true },
  isWatched: { type: Boolean, default: false },
})

const emit = defineEmits(['click', 'toggle-watch'])

const isUp = computed(() => props.stock.percent > 0)
const isDown = computed(() => props.stock.percent < 0)

const priceClass = computed(() => {
  if (isUp.value) return 'text-red-400'
  if (isDown.value) return 'text-green-400'
  return 'text-gray-100'
})

const borderClass = computed(() => {
  if (isUp.value) return 'border-l-red-500/60'
  if (isDown.value) return 'border-l-green-500/60'
  return 'border-l-gray-600'
})

const glowClass = computed(() => {
  if (isUp.value) return 'glow-up'
  if (isDown.value) return 'glow-down'
  return ''
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
    class="bg-gray-800/40 border border-gray-700/30 border-l-4 rounded-xl p-4 cursor-pointer transition-all duration-200 hover:bg-gray-700/40 hover:shadow-xl hover:shadow-black/30 active:scale-[0.98]"
    :class="[borderClass, glowClass]"
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
        class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-lg transition-all duration-200"
        :class="isWatched ? 'text-amber-400 hover:bg-amber-400/15' : 'text-gray-500 hover:text-amber-400 hover:bg-amber-400/10'"
        :title="isWatched ? '取消自选' : '加自选'"
        :aria-label="isWatched ? '取消自选' : '加自选'"
        @click.stop="emit('toggle-watch', stock)"
      >
        <svg
          viewBox="0 0 24 24"
          width="16" height="16"
          :fill="isWatched ? 'currentColor' : 'none'"
          stroke="currentColor"
          stroke-width="2"
          :class="isWatched ? '' : 'hover:scale-110 transition-transform'"
          aria-hidden="true"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </button>
    </div>

    <div class="flex items-baseline gap-3 mb-3">
      <span class="text-2xl font-bold font-mono tracking-tight tabular-nums" :class="priceClass">
        {{ fmtPrice(stock.now) }}
      </span>
      <span
        class="px-2 py-0.5 rounded text-xs font-bold font-mono"
        :class="{
          'bg-red-500/15 text-red-400': isUp,
          'bg-green-500/15 text-green-400': isDown,
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
