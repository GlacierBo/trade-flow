<script setup>
import { useStockStore } from '../../stores/stock'

const store = useStockStore()
</script>

<template>
  <div
    v-if="store.confirmModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
  >
    <div class="bg-gray-800/95 backdrop-blur-xl rounded-2xl max-w-sm w-full p-5 shadow-2xl shadow-black/40 border border-gray-700/50 animate-fadeInScale">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-yellow-500/20 flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 class="text-lg font-black text-gray-100">确认操作</h3>
      </div>
      <p class="text-sm text-gray-300 mb-5 ml-[52px]">{{ store.confirmMessage }}</p>
      <div class="flex gap-3">
        <button
          @click="store.closeConfirm()"
          class="flex-1 py-2.5 bg-gray-700/50 hover:bg-gray-600/50 rounded-xl text-gray-300 font-bold text-sm transition-all duration-200 active:scale-[0.98]"
        >取消</button>
        <button
          @click="store.executeConfirm()"
          class="flex-1 py-2.5 bg-gradient-to-r from-red-500 to-red-400 hover:from-red-400 hover:to-red-300 rounded-xl text-white font-black text-sm shadow-lg shadow-red-500/25 transition-all duration-200 active:scale-[0.98]"
        >{{ store.confirmLabel }}</button>
      </div>
    </div>
  </div>
</template>
