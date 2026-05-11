<script setup>
import { ref } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const priceEditValue = ref('')

function profitClass(val) {
  if (val > 0) return 'text-red-400'
  if (val < 0) return 'text-green-400'
  return 'text-gray-400'
}

function profitSign(val) {
  return val >= 0 ? '+' : ''
}

function openPriceEdit(p) {
  priceEditValue.value = String(p.latest_price)
  store.openPriceModal(p.id, p.latest_price)
}

async function confirmPrice() {
  if (store.priceTarget) {
    await store.updatePrice(store.priceTarget.id, priceEditValue.value)
  }
}

function onClear(p) {
  store.showConfirm(
    '确定要清仓吗？这将删除所有相关交易记录！',
    () => store.clearPosition(p.id)
  )
}
</script>

<template>
  <div class="space-y-3">
    <div v-if="store.positions.length === 0" class="text-center py-6 text-gray-500">
      暂无持仓
    </div>

    <div
      v-for="p in store.positions"
      :key="p.id"
      class="bg-gray-800/50 border border-gray-700/50 rounded-xl p-3"
    >
      <div class="flex justify-between items-center mb-2">
        <div>
          <span class="font-black text-gray-100 text-sm">{{ p.name }}</span>
          <span class="text-xs text-gray-500 ml-1.5">{{ p.contract }}</span>
        </div>
        <span class="font-bold text-lg" :class="profitClass(p.profit)">
          {{ profitSign(p.profit) }}¥{{ p.profit.toFixed(2) }}
        </span>
      </div>
      <div class="grid grid-cols-2 gap-2 text-xs mb-2">
        <div><span class="text-gray-500">持仓:</span> <span class="text-gray-100">{{ p.total_shares }}股</span></div>
        <div><span class="text-gray-500">成本:</span> <span class="text-gray-100">¥{{ p.avg_cost.toFixed(3) }}</span></div>
        <div>
          <span class="text-gray-500">现价:</span>
          <span
            class="text-gray-100 cursor-pointer hover:text-blue-400"
            @click="openPriceEdit(p)"
          >¥{{ p.latest_price.toFixed(3) }}</span>
        </div>
        <div><span class="text-gray-500">收益:</span> <span :class="profitClass(p.profit)">{{ profitSign(p.profit) }}¥{{ p.profit.toFixed(2) }}</span></div>
      </div>
      <div class="flex gap-2 mt-2 pt-2 border-t border-gray-700/50">
        <button
          @click="onClear(p)"
          class="flex-1 bg-red-900/50 hover:bg-red-800/50 text-red-400 py-1.5 rounded-lg text-xs font-bold border border-red-700/50 transition"
        >清仓</button>
      </div>
    </div>

    <!-- 修改价格弹窗 -->
    <div
      v-if="store.priceModalVisible"
      class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      @click.self="store.closePriceModal()"
    >
      <div class="bg-gray-800 rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
        <h3 class="text-lg font-black text-blue-400 mb-4">修改现价</h3>
        <div>
          <label class="block text-xs font-bold text-gray-400 mb-1">当前现价</label>
          <input
            v-model="priceEditValue"
            type="number"
            step="0.001"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm"
          >
        </div>
        <div class="flex gap-3 mt-5">
          <button
            @click="store.closePriceModal()"
            class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
          >取消</button>
          <button
            @click="confirmPrice"
            class="flex-1 bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 py-2.5 rounded-xl text-white font-black text-sm shadow-lg"
          >确认修改</button>
        </div>
      </div>
    </div>
  </div>
</template>
