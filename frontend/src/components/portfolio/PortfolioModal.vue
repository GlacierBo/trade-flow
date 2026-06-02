<script setup>
import { ref, computed, watch } from 'vue'
import { useStockStore } from '../../stores/stock'

const store = useStockStore()

const name = ref('')
const contract = ref('')
const tag = ref('')
const price = ref('')
const isSubmitting = ref(false)

const existingTags = computed(() => {
  const tags = new Set(store.portfolioItems.map(i => i.tag).filter(Boolean))
  return [...tags].sort()
})

watch(() => store.portfolioModalVisible, (v) => {
  if (v) {
    if (store.portfolioPresetData) {
      name.value = store.portfolioPresetData.name || ''
      contract.value = store.portfolioPresetData.contract || ''
      tag.value = store.portfolioPresetData.tag || ''
      price.value = ''
    } else {
      name.value = ''
      contract.value = ''
      tag.value = ''
      price.value = ''
    }
  }
})

async function submit() {
  if (isSubmitting.value) return
  if (!name.value.trim() || !contract.value.trim() || !price.value) {
    store.showToast('请填写完整信息', 'error')
    return
  }
  try {
    isSubmitting.value = true
    await store.createPortfolioItem({
      name: name.value.trim(),
      contract: contract.value.trim(),
      tag: tag.value.trim(),
      price: price.value
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div
    v-if="store.portfolioModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
  >
    <div class="bg-gray-800 rounded-2xl max-w-md w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
      <h3 class="text-lg font-black text-blue-400 mb-4">新增持仓项目</h3>
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">名称</label>
          <input
            v-model="name"
            type="text"
            placeholder="如: 酒ETF"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">代码</label>
          <input
            v-model="contract"
            type="text"
            placeholder="如: 512690"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">Tag</label>
          <input
            v-model="tag"
            type="text"
            placeholder="如: 基金"
            list="existing-tags"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
          <datalist id="existing-tags">
            <option v-for="t in existingTags" :key="t" :value="t" />
          </datalist>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">价格</label>
          <input
            v-model="price"
            type="number"
            step="0.001"
            placeholder="如: 0.481"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
      </div>
      <div class="flex gap-3 mt-5">
        <button
          @click="store.closePortfolioModal()"
          class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="submit"
          :disabled="isSubmitting"
          :class="[
            'flex-1 py-2.5 rounded-xl text-white font-black text-sm shadow-lg transition',
            isSubmitting
              ? 'bg-gray-500 cursor-not-allowed opacity-50'
              : 'bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 shadow-blue-500/30'
          ]"
        >
          {{ isSubmitting ? '提交中...' : '确认保存' }}
        </button>
      </div>
    </div>
  </div>
</template>
