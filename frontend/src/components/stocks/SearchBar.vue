<script setup>
import { ref, computed } from 'vue'
import { useStocksStore } from '../../stores/stocks'

const store = useStocksStore()
const keyword = ref('')

const sources = [
  { value: 'auto', label: '自动', desc: '自动选择最佳数据源' },
  { value: 'sina', label: '新浪', desc: '新浪财经' },
  { value: 'tencent', label: '腾讯', desc: '腾讯股票' },
  { value: 'eastmoney', label: '东方财富', desc: '东方财富' },
]

const currentSource = computed(() => store.source)

let _timer = null
function onInput() {
  if (_timer) clearTimeout(_timer)
  _timer = setTimeout(() => {
    if (keyword.value.trim()) store.search(keyword.value)
  }, 500)
}

function onSubmit() {
  if (_timer) clearTimeout(_timer)
  if (keyword.value.trim()) store.search(keyword.value)
}

function setSource(value) {
  store.source = value
  if (keyword.value.trim()) {
    store.search(keyword.value)
  }
}
</script>

<template>
  <div class="space-y-3">
    <!-- 搜索框 -->
    <div class="flex gap-3">
      <div class="relative flex-1">
        <svg
          class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
          fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          v-model="keyword"
          type="text"
          aria-label="搜索股票"
          placeholder="输入股票代码或名称，如 SH510500、格力电器"
          class="w-full bg-gray-700/30 border border-gray-600/30 rounded-xl pl-10 pr-4 py-3 text-sm outline-none transition-all duration-200 text-gray-100 placeholder-gray-500 focus:border-blue-500/40 focus:bg-gray-700/50 focus:shadow-lg focus:shadow-blue-500/5"
          @input="onInput"
          @keydown.enter="onSubmit"
        />
      </div>
      <button
        class="px-5 py-3 bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all duration-200 active:scale-95"
        @click="onSubmit"
      >
        搜索
      </button>
    </div>

    <!-- 数据源切换 -->
    <div class="flex items-center gap-2">
      <span class="text-xs text-gray-500 font-medium">数据源：</span>
      <div class="flex gap-1.5">
        <button
          v-for="s in sources"
          :key="s.value"
          @click="setSource(s.value)"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer',
            currentSource === s.value
              ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10'
              : 'bg-gray-700/30 text-gray-400 border border-gray-600/20 hover:bg-gray-600/30 hover:text-gray-300 hover:border-gray-500/30'
          ]"
        >
          {{ s.label }}
        </button>
      </div>
    </div>
  </div>
</template>
