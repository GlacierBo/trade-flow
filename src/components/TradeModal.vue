<script setup>
import { ref, computed, watch } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const contract = ref('')
const name = ref('')
const price = ref('')
const shares = ref('')
const feeRate = ref('0.02')

watch(() => store.tradeModalVisible, (v) => {
  if (v) {
    contract.value = ''
    name.value = ''
    price.value = ''
    shares.value = ''
    feeRate.value = '0.02'
    store.setTradeType('buy')
  }
})

const amount = computed(() => {
  const p = parseFloat(price.value) || 0
  const s = parseInt(shares.value) || 0
  return (p * s).toFixed(2)
})

const fee = computed(() => {
  const amt = parseFloat(amount.value) || 0
  const rate = parseFloat(feeRate.value) / 100 || 0
  return Math.max(amt * rate, 0.2).toFixed(2)
})

const net = computed(() => {
  return (parseFloat(amount.value) + parseFloat(fee.value)).toFixed(2)
})

async function submit() {
  if (!contract.value.trim() || !name.value.trim() || !price.value || !shares.value) {
    store.showToast('请填写完整信息', 'error')
    return
  }
  await store.createTrade({
    contract: contract.value.trim(),
    name: name.value.trim(),
    price: price.value,
    shares: shares.value,
    feeRate: feeRate.value,
    minFee: 0.2
  })
}
</script>

<template>
  <div
    v-if="store.tradeModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closeTradeModal()"
  >
    <div class="bg-gray-800 rounded-2xl max-w-md w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
      <h3 class="text-lg font-black text-blue-400 mb-4">新增交易</h3>
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">合约代码</label>
          <input
            v-model="contract"
            type="text"
            placeholder="如: 512690"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">交易类型</label>
          <div class="flex gap-2">
            <button
              @click="store.setTradeType('buy')"
              :class="[
                'flex-1 py-2 rounded-lg text-white font-bold text-sm transition',
                store.tradeType === 'buy' ? 'bg-green-600 hover:bg-green-500' : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              ]"
            >买入</button>
            <button
              @click="store.setTradeType('sell')"
              :class="[
                'flex-1 py-2 rounded-lg text-white font-bold text-sm transition',
                store.tradeType === 'sell' ? 'bg-red-600 hover:bg-red-500' : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              ]"
            >卖出</button>
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">合约名称</label>
          <input
            v-model="name"
            type="text"
            placeholder="如: 酒ETF"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">交易价格</label>
          <input
            v-model="price"
            type="number"
            step="0.001"
            placeholder="如: 0.481"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">交易份额</label>
          <input
            v-model="shares"
            type="number"
            placeholder="如: 1200"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
          >
        </div>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">手续费率 (%)</label>
          <input
            v-model="feeRate"
            type="number"
            step="0.001"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm"
          >
        </div>
        <div class="bg-gray-700/30 rounded-lg p-3 space-y-1.5">
          <div class="flex justify-between text-xs">
            <span class="text-gray-400">成交金额</span>
            <span class="font-bold text-blue-400">¥{{ amount }}</span>
          </div>
          <div class="flex justify-between text-xs">
            <span class="text-gray-400">佣金</span>
            <span class="font-bold text-blue-400">¥{{ fee }}</span>
          </div>
          <div class="flex justify-between text-xs pt-2 border-t border-gray-600">
            <span class="text-gray-300 font-bold">净额</span>
            <span class="font-black text-blue-400">¥{{ net }}</span>
          </div>
        </div>
      </div>
      <div class="flex gap-3 mt-5">
        <button
          @click="store.closeTradeModal()"
          class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="submit"
          class="flex-1 bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 py-2.5 rounded-xl text-white font-black text-sm shadow-lg shadow-blue-500/30"
        >确认交易</button>
      </div>
    </div>
  </div>
</template>
