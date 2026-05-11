<script setup>
import { ref, watch } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const price = ref('')
const shares = ref('')
const errorMsg = ref('')

watch(() => store.sellModalVisible, (v) => {
  if (v) {
    price.value = ''
    shares.value = ''
    errorMsg.value = ''
  }
})

async function submit() {
  errorMsg.value = ''

  const p = parseFloat(price.value)
  const s = parseInt(shares.value)

  if (!p || p <= 0) {
    errorMsg.value = '请输入有效的价格'
    return
  }
  if (!s || s <= 0) {
    errorMsg.value = '请输入有效的份额'
    return
  }
  if (s > store.sellTarget.remainingShares) {
    errorMsg.value = `卖出份额不能超过可卖数量 ${store.sellTarget.remainingShares}股`
    return
  }

  await store.sellFromBuy({
    price: price.value,
    shares: shares.value,
    feeRate: '0.02',
    minFee: 0.2,
    buyOrderNo: store.sellTarget.buyOrderNo
  })
}
</script>

<template>
  <div
    v-if="store.sellModalVisible && store.sellTarget"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closeSellModal()"
  >
    <div class="bg-gray-800 rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
      <h3 class="text-lg font-black text-red-400 mb-4">卖出操作</h3>
      <div class="space-y-3">
        <div class="bg-gray-700/30 rounded-lg p-3 space-y-2">
          <div class="text-xs text-gray-400">买入单号</div>
          <div class="font-bold text-blue-400 text-sm">{{ store.sellTarget.buyOrderNo }}</div>
          <div class="text-xs text-gray-400 mt-2">买入价格</div>
          <div class="font-bold text-gray-100">¥{{ store.sellTarget.buyPrice.toFixed(3) }}</div>
          <div class="text-xs text-gray-400 mt-2">剩余可卖</div>
          <div class="font-bold text-yellow-400">{{ store.sellTarget.remainingShares }}股</div>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">卖出价格</label>
          <input
            v-model="price"
            type="number"
            step="0.001"
            placeholder="请输入价格"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">卖出份额</label>
          <input
            v-model="shares"
            type="number"
            placeholder="请输入份额"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
          <p v-if="errorMsg" class="text-xs text-red-400 mt-1">{{ errorMsg }}</p>
        </div>
      </div>
      <div class="flex gap-3 mt-5">
        <button
          @click="store.closeSellModal()"
          class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="submit"
          class="flex-1 bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 py-2.5 rounded-xl text-white font-black text-sm shadow-lg"
        >确认卖出</button>
      </div>
    </div>
  </div>
</template>
