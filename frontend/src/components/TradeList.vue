<script setup>
import { ref } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const expandedSells = ref({})

function toggleSells(tradeId) {
  expandedSells.value[tradeId] = !expandedSells.value[tradeId]
}

function isExpanded(tradeId) {
  return !!expandedSells.value[tradeId]
}

function formatDateTime(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

function profitClass(val) {
  if (val > 0) return 'text-red-400'
  if (val < 0) return 'text-green-400'
  return 'text-gray-400'
}

function profitSign(val) {
  return val >= 0 ? '+' : ''
}

function onDelete(trade, tradeType) {
  const msg = tradeType === 'buy'
    ? '确定要删除这条买入记录吗？此操作不可恢复。'
    : '确定要删除这条卖出记录吗？'
  store.showConfirm(msg, () => store.deleteTrade(trade.id))
}
</script>

<template>
  <div class="space-y-3 max-h-[700px] overflow-y-auto scrollbar-thin">
    <div v-if="store.filteredTrades.length === 0" class="text-center py-8 text-gray-500">
      暂无交易记录
    </div>

    <div
      v-for="t in store.filteredTrades"
      :key="t.id"
    >
      <!-- 买入记录卡片 -->
      <div class="bg-gray-800/50 border border-gray-700/50 rounded-xl p-3 hover-accent transition-all animate-fadeIn">
        <div class="flex justify-between items-start mb-2">
          <div>
            <div class="font-black text-gray-100 text-sm">
              {{ t.name }} <span class="text-xs text-gray-500">{{ t.contract }}</span>
            </div>
            <div class="text-xs text-blue-400 mt-0.5">{{ t.buy_order_no }}</div>
          </div>
          <span class="bg-green-900/50 text-green-400 border-green-700 px-2 py-0.5 rounded-full text-xs font-bold border">
            买入
          </span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs mb-2">
          <div><span class="text-gray-500">价格:</span> <span class="font-bold text-blue-400">¥{{ t.price.toFixed(3) }}</span></div>
          <div><span class="text-gray-500">份额:</span> <span class="font-bold text-gray-100">{{ t.shares }}</span></div>
          <div><span class="text-gray-500">可卖:</span> <span class="font-bold text-yellow-400">{{ t.remaining_shares }}</span></div>
          <div><span class="text-gray-500">金额:</span> <span class="font-bold text-blue-400">¥{{ t.amount.toFixed(2) }}</span></div>
          <div><span class="text-gray-500">佣金:</span> <span class="font-bold text-gray-400">¥{{ t.fee.toFixed(2) }}</span></div>
          <div><span class="text-gray-500">累计收益:</span> <span class="font-bold" :class="profitClass(t.realized_profit)">{{ profitSign(t.realized_profit) }}¥{{ t.realized_profit.toFixed(2) }}</span></div>
        </div>
        <div class="flex justify-between items-center pt-2 border-t border-gray-700">
          <span class="text-xs text-gray-400">{{ formatDateTime(t.created_at) }}</span>
          <div class="flex gap-1.5">
            <button
              v-if="t.remaining_shares > 0"
              @click="store.openSellModal(t.buy_order_no, t.price, t.remaining_shares)"
              class="bg-red-900/50 hover:bg-red-800/50 text-red-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-red-700/50 transition"
            >卖出</button>
            <button
              @click="onDelete(t, 'buy')"
              class="bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-gray-600/50 transition"
            >删除</button>
          </div>
        </div>
      </div>

      <!-- 卖出子列表 -->
      <div v-if="t.sells && t.sells.length > 0" class="mt-2">
        <button
          @click="toggleSells(t.id)"
          class="w-full flex items-center justify-center gap-1 text-xs text-gray-400 hover:text-blue-400 transition py-1 rounded-lg bg-gray-800/30 border border-gray-700/30"
        >
          <span>{{ isExpanded(t.id) ? '▲' : '▼' }}</span>
          <span>{{ isExpanded(t.id) ? '收起' : '展开' }} {{ t.sells.length }} 笔卖出记录</span>
        </button>
        <div v-if="isExpanded(t.id)" class="mt-2 space-y-2">
          <div
            v-for="s in t.sells"
            :key="s.id"
            class="sell-row bg-gray-800/30 border border-gray-700/30 rounded-lg p-2.5 animate-fadeIn"
          >
            <div class="flex justify-between items-center mb-1.5">
              <div class="text-xs">
                <span class="text-red-400 font-bold">卖出</span>
                <span class="text-gray-500 ml-1.5">{{ s.buy_order_no }}</span>
              </div>
              <span class="text-xs text-gray-400">{{ formatDateTime(s.created_at) }}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs mb-2">
              <div><span class="text-gray-500">价格:</span> <span class="font-bold text-blue-400">¥{{ s.price.toFixed(3) }}</span></div>
              <div><span class="text-gray-500">份额:</span> <span class="font-bold text-gray-100">{{ Math.abs(s.shares) }}</span></div>
              <div><span class="text-gray-500">佣金:</span> <span class="font-bold text-gray-400">¥{{ s.fee.toFixed(2) }}</span></div>
              <div><span class="text-gray-500">收益:</span> <span class="font-bold" :class="profitClass(s.single_profit)">{{ profitSign(s.single_profit) }}¥{{ s.single_profit.toFixed(2) }}</span></div>
            </div>
            <div class="flex justify-end pt-2 border-t border-gray-700/50">
              <button
                @click="onDelete(s, 'sell')"
                class="bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 px-2.5 py-1 rounded-lg text-xs font-bold border border-gray-600/50 transition"
              >删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
