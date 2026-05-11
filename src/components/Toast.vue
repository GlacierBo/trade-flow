<script setup>
import { useStockStore } from '../stores/stock'

const store = useStockStore()
</script>

<template>
  <div class="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 space-y-2">
    <div
      v-for="toast in store.toasts"
      :key="toast.id"
      :class="[
        'px-4 py-2 rounded-xl shadow-xl font-black text-sm animate-fadeIn',
        toast.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
      ]"
    >
      <span>{{ toast.type === 'success' ? '✅' : '❌' }}</span> {{ toast.msg }}
    </div>
  </div>
</template>
