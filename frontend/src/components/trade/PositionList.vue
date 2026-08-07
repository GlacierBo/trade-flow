<script setup>
import { ref } from 'vue'
import { useStockStore } from '../../stores/stock'

const store = useStockStore()

const priceEditValue = ref('')

function profitClass(val) {
  if (val > 0) return 'text-red-400'
  if (val < 0) return 'text-green-400'
  return 'text-gray-400'
}

function profitBgClass(val) {
  if (val > 0) return 'bg-red-500/10'
  if (val < 0) return 'bg-green-500/10'
  return 'bg-gray-700/30'
}

function profitSign(val) {
  return val >= 0 ? '+' : ''
}

// 浮动盈亏 = (现价 - 摊薄成本) × 持仓数量
function floatingProfit(p) {
  return (p.latest_price - p.avg_cost) * p.total_shares
}

function isClosed(p) {
  return p.total_shares === 0
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
    () => store.clearPosition(p.id),
    '确认清仓'
  )
}
</script>

<template>
  <div class="space-y-3 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
    <!-- 空状态 -->
    <div v-if="store.positions.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-500">
      <svg class="w-10 h-10 mb-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="text-sm">暂无持仓</p>
    </div>

    <!-- 活跃持仓 -->
    <div
      v-for="p in store.positions.filter(p => !isClosed(p))"
      :key="p.id"
      class="bg-gray-700/30 hover:bg-gray-700/40 border border-gray-600/30 rounded-xl p-4 transition-all duration-200"
    >
      <!-- 顶部：名称 + 收益 -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <span class="font-bold text-gray-100 text-sm">{{ p.name }}</span>
          <span class="text-xs text-gray-500 font-mono">{{ p.contract }}</span>
        </div>
        <div class="flex items-start gap-2">
          <div class="flex flex-col items-end">
            <span class="text-[10px] text-gray-500 mb-0.5">已实现收益</span>
            <div
              class="px-2.5 py-1 rounded-lg text-sm font-bold"
              :class="[profitClass(p.profit), profitBgClass(p.profit)]"
            >
              {{ profitSign(p.profit) }}¥{{ p.profit.toFixed(2) }}
            </div>
          </div>
          <div class="flex flex-col items-end">
            <span class="text-[10px] text-gray-500 mb-0.5">浮动盈亏</span>
            <div
              class="px-2.5 py-1 rounded-lg text-sm font-bold"
              :class="[profitClass(floatingProfit(p)), profitBgClass(floatingProfit(p))]"
            >
              {{ profitSign(floatingProfit(p)) }}¥{{ floatingProfit(p).toFixed(2) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 数据网格 -->
      <div class="grid grid-cols-2 gap-2 mb-3">
        <div class="bg-gray-800/40 rounded-lg px-3 py-2">
          <div class="text-xs text-gray-500 mb-0.5">持仓</div>
          <div class="text-sm font-bold text-gray-100">{{ p.total_shares }} <span class="text-xs font-normal text-gray-500">股</span></div>
        </div>
        <div class="bg-gray-800/40 rounded-lg px-3 py-2">
          <div class="text-xs text-gray-500 mb-0.5">成本</div>
          <div class="text-sm font-bold text-gray-100">¥{{ p.avg_cost.toFixed(3) }}</div>
        </div>
        <div class="bg-gray-800/40 rounded-lg px-3 py-2 cursor-pointer hover:bg-gray-800/60 transition" @click="openPriceEdit(p)">
          <div class="text-xs text-gray-500 mb-0.5">现价 <span class="text-blue-400">编辑</span></div>
          <div class="text-sm font-bold text-blue-400">¥{{ p.latest_price.toFixed(3) }}</div>
        </div>
        <div class="bg-gray-800/40 rounded-lg px-3 py-2">
          <div class="text-xs text-gray-500 mb-0.5">收益率</div>
          <div class="text-sm font-bold" :class="profitClass(p.profit_rate)">
            {{ profitSign(p.profit_rate) }}{{ p.profit_rate.toFixed(2) }}%
          </div>
        </div>
      </div>

      <!-- 清仓按钮 -->
      <button
        @click="onClear(p)"
        class="w-full py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold rounded-lg border border-red-500/20 transition-all active:scale-[0.98]"
      >清仓</button>
    </div>

    <!-- 已平仓记录 -->
    <div v-if="store.positions.filter(p => isClosed(p)).length > 0">
      <!-- 分隔线 -->
      <div class="flex items-center gap-3 my-4">
        <div class="flex-1 h-px bg-gray-700/50"></div>
        <span class="text-xs text-gray-500 font-medium">已平仓</span>
        <div class="flex-1 h-px bg-gray-700/50"></div>
      </div>

      <div class="space-y-2">
        <div
          v-for="p in store.positions.filter(p => isClosed(p))"
          :key="p.id"
          class="bg-gray-800/20 border border-gray-700/20 rounded-xl px-4 py-3 opacity-60 hover:opacity-100 transition-opacity"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="font-medium text-gray-400 text-sm">{{ p.name }}</span>
              <span class="text-xs text-gray-600 font-mono">{{ p.contract }}</span>
              <span class="text-xs bg-gray-700/50 text-gray-500 px-1.5 py-0.5 rounded">已平仓</span>
            </div>
            <span class="text-sm font-bold" :class="profitClass(p.profit)">
              {{ profitSign(p.profit) }}¥{{ p.profit.toFixed(2) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 修改价格弹窗 -->
  <div
    v-if="store.priceModalVisible"
    class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"

  >
    <div class="bg-gray-800 rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-gray-700/50 animate-fadeIn" @keydown.enter="confirmPrice">
      <h3 class="text-lg font-bold text-gray-100 mb-5">修改现价</h3>
      <div>
        <label class="block text-xs font-medium text-gray-400 mb-2">当前现价</label>
        <input
          v-model="priceEditValue"
          type="number"
          step="0.001"
          class="w-full bg-gray-700/50 border border-gray-600/50 rounded-xl px-4 py-3 outline-none focus:border-blue-500/50 text-gray-100 text-sm transition"
        >
      </div>
      <div class="flex gap-3 mt-6">
        <button
          @click="store.closePriceModal()"
          class="flex-1 bg-gray-700 hover:bg-gray-600 py-3 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="confirmPrice"
          class="flex-1 bg-blue-500 hover:bg-blue-400 py-3 rounded-xl text-white font-bold text-sm transition shadow-lg shadow-blue-500/25"
        >确认修改</button>
      </div>
    </div>
  </div>
</template>
