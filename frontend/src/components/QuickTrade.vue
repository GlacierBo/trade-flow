<script setup>
import { useStockStore } from '../stores/stock'

const store = useStockStore()

function onDeleteTag(tag) {
  store.showConfirm(`确定要删除"${tag.name}"的快捷交易吗？`, () => {
    store.deleteTag(tag.id)
  })
}
</script>

<template>
  <div class="bg-gray-800/50 rounded-2xl p-4 border border-gray-700/50">
    <h2 class="text-lg font-black text-blue-400 mb-3">快捷交易</h2>
    
    <div v-if="store.tags.length === 0" class="text-center py-6 text-gray-500 text-sm">
      暂无快捷交易<br>
      <span class="text-xs">创建交易后会自动添加</span>
    </div>

    <div v-else class="space-y-1.5 max-h-[600px] overflow-y-auto scrollbar-thin">
      <div
        v-for="tag in store.tags"
        :key="tag.id"
        class="group bg-gray-700/30 hover:bg-gray-700/50 border border-gray-600/30 rounded-lg px-2.5 py-2 cursor-pointer transition-all active:scale-95 relative flex items-center justify-between"
        @click="store.handleTagClick(tag)"
      >
        <div class="flex-1 min-w-0">
          <div class="font-bold text-gray-100 text-xs truncate">
            {{ tag.name }}
          </div>
          <div class="text-xs text-gray-400 mt-0.5">{{ tag.contract }}</div>
        </div>
        <button
          @click.stop="onDeleteTag(tag)"
          class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-400 transition-opacity ml-2 px-1 py-0.5 rounded text-base leading-none flex-shrink-0"
          title="删除标签"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>
