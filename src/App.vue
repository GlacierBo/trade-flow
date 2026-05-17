<script setup>
import { computed, onMounted } from 'vue'
import { useStockStore } from './stores/stock'
import LoginPage from './components/LoginPage.vue'
import QuickTrade from './components/QuickTrade.vue'
import TradeList from './components/TradeList.vue'
import PositionList from './components/PositionList.vue'
import TradeModal from './components/TradeModal.vue'
import SellModal from './components/SellModal.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import Toast from './components/Toast.vue'
import PortfolioRatio from './components/PortfolioRatio.vue'
import PortfolioModal from './components/PortfolioModal.vue'
import UserManagement from './components/UserManagement.vue'
import ChangePasswordForm from './components/ChangePasswordForm.vue'

const store = useStockStore()

const tabs = computed(() => {
  const list = [
    { key: 'trade', label: '网格交易' },
    { key: 'portfolio', label: '持仓比例' }
  ]
  if (store.isAdmin) {
    list.push({ key: 'users', label: '用户管理' })
  }
  return list
})

onMounted(() => {
  store.checkAuth()
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
  <div v-else class="max-w-7xl mx-auto px-4">
    <header class="mb-4 flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-black tracking-tight accent-gradient">TradeFlow</h1>
        <p class="text-xs text-gray-500 font-bold uppercase tracking-widest">Smart Trading Management</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-400">
          {{ store.username }}
        </span>
        <button
          @click="store.openPasswordModal()"
          class="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-2 rounded-xl font-bold transition-all active:scale-95 text-xs"
        >
          修改密码
        </button>
        <button
          @click="handleLogout"
          class="bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded-xl font-bold transition-all active:scale-95 text-sm"
        >
          退出
        </button>
      </div>
    </header>

    <!-- Tab 导航 -->
    <div class="flex gap-1 mb-5 bg-gray-800/30 rounded-xl p-1 border border-gray-700/30 w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="store.setActiveTab(tab.key)"
        :class="[
          'px-5 py-2 rounded-lg text-sm font-black transition-all',
          store.activeTab === tab.key
            ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/50'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 网格交易页 -->
    <div v-if="store.activeTab === 'trade'" class="grid grid-cols-1 lg:grid-cols-12 gap-5">
      <div class="lg:col-span-2">
        <QuickTrade />
      </div>
      <div class="lg:col-span-6">
        <div class="bg-gray-800/50 rounded-2xl p-5 border border-gray-700/50">
          <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
            <h2 class="text-lg font-black text-blue-400">交易明细<button
                @click="store.openTradeModal()"
                class="ml-1.5 inline-flex items-center justify-center w-5 h-5 rounded-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white font-black text-sm leading-none shadow-lg shadow-blue-500/30 transition-all active:scale-95"
              >+</button></h2>
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
      <div class="lg:col-span-4">
        <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden sticky top-4">
          <div class="p-4">
            <h2 class="text-lg font-black text-blue-400 mb-4">持仓概览</h2>
            <PositionList />
          </div>
        </div>
      </div>
    </div>

    <!-- 持仓比例页 -->
    <PortfolioRatio v-if="store.activeTab === 'portfolio'" />

    <!-- 用户管理页（仅管理员） -->
    <UserManagement v-if="store.activeTab === 'users'" />
  </div>

  <TradeModal />
  <PortfolioModal />
  <SellModal />
  <ConfirmModal />
  <Toast />

  <!-- 修改密码弹窗 -->
  <div
    v-if="store.passwordModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closePasswordModal()"
  >
    <ChangePasswordForm />
  </div>
</template>
