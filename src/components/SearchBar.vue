<script setup>
import { ref } from 'vue'
import { useStocksStore } from '../stores/stocks'

const store = useStocksStore()
const keyword = ref('')

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
</script>

<template>
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
        placeholder="输入股票代码或名称，如 SH510500、格力电器"
        class="w-full bg-gray-700/50 border border-gray-600 rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500 transition-colors"
        @input="onInput"
        @keydown.enter="onSubmit"
      />
    </div>
    <button
      class="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95"
      @click="onSubmit"
    >
      搜索
    </button>
  </div>
</template>
