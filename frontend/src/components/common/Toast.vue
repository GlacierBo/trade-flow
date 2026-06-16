<script setup>
import { useStockStore } from '../../stores/stock'

const store = useStockStore()
</script>

<template>
  <div class="fixed top-4 right-4 z-50 space-y-2 pointer-events-none" aria-live="polite" aria-atomic="true">
    <div
      v-for="toast in store.toasts"
      :key="toast.id"
      :class="[
        'pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl shadow-2xl font-bold text-sm animate-slideInRight backdrop-blur-sm',
        toast.type === 'success'
          ? 'bg-green-500/20 border border-green-500/30 text-green-300'
          : 'bg-red-500/20 border border-red-500/30 text-red-300'
      ]"
    >
      <span
        class="w-7 h-7 rounded-full flex items-center justify-center text-sm"
        :class="toast.type === 'success' ? 'bg-green-500/30' : 'bg-red-500/30'"
      >
        {{ toast.type === 'success' ? '✓' : '✕' }}
      </span>
      <span>{{ toast.msg }}</span>
    </div>
  </div>
</template>
