<script setup>
import { ref } from 'vue'
import { useStockStore } from '../../stores/stock'

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
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
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
  <div class="space-y-3 max-h-[calc(100vh-220px)] overflow-y-auto pr-1">
    <!-- 空状态 -->
    <div v-if="store.filteredTrades.length === 0" class="flex flex-col items-center justify-center py-16 text-gray-500">
      <svg class="w-12 h-12 mb-3 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-sm">暂无交易记录</p>
      <p class="text-xs text-gray-600 mt-1">点击上方 "新增" 开始记录</p>
    </div>

    <!-- 交易记录列表 -->
    <div
      v-for="t in store.filteredTrades"
      :key="t.id"
      class="group"
    >
      <!-- 买入记录卡片 -->
      <div class="bg-gray-700/30 hover:bg-gray-700/40 border border-gray-600/30 rounded-xl p-4 transition-all duration-200">
        <!-- 顶部：名称 + 标签 + 操作按钮 -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="font-bold text-gray-100 text-sm">{{ t.name }}</span>
              <span class="text-xs text-gray-500 font-mono">{{ t.contract }}</span>
            </div>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs text-blue-400/70 font-mono">{{ t.buy_order_no }}</span>
              <span class="text-xs text-gray-600">·</span>
              <span class="text-xs text-gray-500">{{ formatDateTime(t.created_at) }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2 ml-3">
            <button
              v-if="t.remaining_shares > 0"
              @click="store.openSellModal(t.buy_order_no, t.price, t.remaining_shares)"
              class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold rounded-lg border border-red-500/20 transition-all active:scale-95"
            >卖出</button>
            <button
              @click="onDelete(t, 'buy')"
              class="px-2 py-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 数据网格 -->
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">价格</div>
            <div class="text-sm font-bold text-blue-400">¥{{ t.price.toFixed(3) }}</div>
          </div>
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">份额</div>
            <div class="text-sm font-bold text-gray-100">{{ t.shares }}</div>
          </div>
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">可卖</div>
            <div class="text-sm font-bold text-yellow-400">{{ t.remaining_shares }}</div>
          </div>
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">金额</div>
            <div class="text-sm font-bold text-gray-200">¥{{ t.amount.toFixed(2) }}</div>
          </div>
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">佣金</div>
            <div class="text-sm font-bold text-gray-400">¥{{ t.fee.toFixed(2) }}</div>
          </div>
          <div class="bg-gray-800/40 rounded-lg px-3 py-2">
            <div class="text-xs text-gray-500 mb-0.5">累计收益</div>
            <div class="text-sm font-bold" :class="profitClass(t.realized_profit)">
              {{ profitSign(t.realized_profit) }}¥{{ t.realized_profit.toFixed(2) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 卖出子列表 -->
      <div v-if="t.sells && t.sells.length > 0" class="ml-4 mt-1">
        <button
          @click="toggleSells(t.id)"
          class="w-full flex items-center justify-center gap-1.5 text-xs text-gray-500 hover:text-blue-400 transition py-1.5 rounded-lg hover:bg-gray-800/30"
        >
          <svg
            class="w-3 h-3 transition-transform"
            :class="isExpanded(t.id) ? 'rotate-180' : ''"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <span>{{ t.sells.length }} 笔卖出记录</span>
        </button>

        <div v-if="isExpanded(t.id)" class="space-y-2 mt-1">
          <div
            v-for="s in t.sells"
            :key="s.id"
            class="bg-gray-800/20 border border-gray-700/20 rounded-lg p-3 animate-fadeIn"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <span class="w-1 h-1 rounded-full bg-red-400"></span>
                <span class="text-xs text-red-400 font-bold">卖出</span>
                <span class="text-xs text-gray-600 font-mono">{{ formatDateTime(s.created_at) }}</span>
              </div>
              <button
                @click="onDelete(s, 'sell')"
                class="text-gray-600 hover:text-red-400 transition opacity-0 group-hover:opacity-100"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="grid grid-cols-4 gap-2 text-xs">
              <div>
                <span class="text-gray-600">价格</span>
                <div class="font-bold text-blue-400">¥{{ s.price.toFixed(3) }}</div>
              </div>
              <div>
                <span class="text-gray-600">份额</span>
                <div class="font-bold text-gray-300">{{ Math.abs(s.shares) }}</div>
              </div>
              <div>
                <span class="text-gray-600">佣金</span>
                <div class="font-bold text-gray-500">¥{{ s.fee.toFixed(2) }}</div>
              </div>
              <div>
                <span class="text-gray-600">收益</span>
                <div class="font-bold" :class="profitClass(s.single_profit)">
                  {{ profitSign(s.single_profit) }}¥{{ s.single_profit.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
