<script setup>
import { onMounted } from 'vue'
import { useStockStore } from './stores/stock'
import LoginPage from './components/LoginPage.vue'
import TradeList from './components/TradeList.vue'
import PositionList from './components/PositionList.vue'
import TradeModal from './components/TradeModal.vue'
import SellModal from './components/SellModal.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import Toast from './components/Toast.vue'

const store = useStockStore()

onMounted(() => {
  // 检查登录状态
  store.checkAuth()
  
  // 如果已登录，加载数据
  if (store.isAuthenticated) {
    store.loadData()
  }
})

const handleLogout = () => {
  store.showConfirm('确定要退出登录吗？', () => {
    store.logout()
    window.location.reload()
  })
}
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!store.isAuthenticated" />

  <!-- Main App -->
  <div v-else class="max-w-6xl mx-auto">
    <header class="mb-6 flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight accent-gradient">TradeFlow</h1>
        <p class="text-xs text-gray-500 font-bold uppercase tracking-widest">Smart Trading Management</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-400">
          👤 {{ store.username }}
        </span>
        <button
          @click="handleLogout"
          class="bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2.5 rounded-xl font-bold transition-all active:scale-95 text-sm"
        >
          退出登录
        </button>
        <button
          @click="store.openTradeModal()"
          class="bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white px-5 py-2.5 rounded-xl font-black shadow-lg shadow-blue-500/30 transition-all active:scale-95 text-sm"
        >
          + 新增交易
        </button>
      </div>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="lg:col-span-2">
        <div class="bg-gray-800/50 rounded-2xl p-5 border border-gray-700/50">
          <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
            <h2 class="text-lg font-black text-blue-400">交易明细</h2>
            <div class="relative">
              <input
                v-model="store.searchQuery"
                type="text"
                placeholder="搜索合约或单号..."
                class="bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-blue-500 w-48 text-gray-100 placeholder-gray-500"
              >
            </div>
          </div>
          <TradeList />
        </div>
      </div>

      <div class="lg:col-span-1">
        <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden sticky top-4">
          <div class="p-4">
            <h2 class="text-lg font-black text-blue-400 mb-4">持仓概览</h2>
            <PositionList />
          </div>
        </div>
      </div>
    </div>
  </div>

  <TradeModal />
  <SellModal />
  <ConfirmModal />
  <Toast />
</template>
