<script setup>
import { useStockStore } from '../stores/stock'

const store = useStockStore()
</script>

<template>
  <div
    v-if="store.confirmModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closeConfirm()"
  >
    <div class="bg-gray-800 rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
      <h3 class="text-lg font-black text-yellow-400 mb-3">⚠️ 确认操作</h3>
      <p class="text-sm text-gray-300 mb-4">{{ store.confirmMessage }}</p>
      <div class="flex gap-3">
        <button
          @click="store.closeConfirm()"
          class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="store.executeConfirm()"
          class="flex-1 bg-red-600 hover:bg-red-500 py-2.5 rounded-xl text-white font-black text-sm shadow-lg"
        >确认</button>
      </div>
    </div>
  </div>
</template>
