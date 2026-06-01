<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStockStore } from './stores/stock'
import LoginPage from './components/LoginPage.vue'
import Sidebar from './components/Sidebar.vue'
import QuickTrade from './components/QuickTrade.vue'
import TradeList from './components/TradeList.vue'
import PositionList from './components/PositionList.vue'
import TradeModal from './components/TradeModal.vue'
import SellModal from './components/SellModal.vue'
import ConfirmModal from './components/common/ConfirmModal.vue'
import Toast from './components/common/Toast.vue'
import PortfolioRatio from './components/PortfolioRatio.vue'
import PortfolioModal from './components/PortfolioModal.vue'
import UserManagement from './components/UserManagement.vue'
import SponsorView from './components/SponsorView.vue'
import ChangePasswordForm from './components/ChangePasswordForm.vue'
import StockSearch from './components/StockSearch.vue'
import PortfolioAllocator from './components/PortfolioAllocator.vue'

const store = useStockStore()
const route = useRoute()
const router = useRouter()

// 路由变化同步到 store，用来高亮侧边栏
watch(() => route.name, (name) => {
  if (name && typeof name === 'string') store.setView(name)
})

onMounted(() => {
  store.checkAuth()
  if (store.isAuthenticated) {
    store.loadData()
    // 首次加载，URL 为空时跳到 home
    if (route.name === 'home' || !route.name) {
      store.setView('home')
    }
  }
})
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!store.isAuthenticated" />

  <!-- Main App with Sidebar -->
  <div v-else class="flex min-h-screen">
    <Sidebar />

    <!-- Content Area -->
    <main class="flex-1 ml-60 p-6">
      <!-- 网格交易页 -->
      <div v-if="route.name === 'home'" class="grid grid-cols-1 lg:grid-cols-12 gap-5">
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
          <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden sticky top-6">
            <div class="p-4">
              <h2 class="text-lg font-black text-blue-400 mb-4">持仓概览</h2>
              <PositionList />
            </div>
          </div>
        </div>
      </div>

      <!-- 股票查询页 -->
      <StockSearch v-if="route.name === 'stocks'" />

      <!-- 持仓分配页 -->
      <PortfolioAllocator v-if="route.name === 'allocator'" />

      <!-- 持仓比例页 -->
      <PortfolioRatio v-if="route.name === 'portfolio'" />

      <!-- 用户管理页（仅管理员） -->
      <UserManagement v-if="route.name === 'users'" />

      <!-- 赞助作者页 -->
      <div v-if="route.name === 'sponsor'" class="py-8">
        <SponsorView />
      </div>
    </main>
  </div>

  <TradeModal />
  <PortfolioModal />
  <SellModal />
  <ConfirmModal />
  <Toast />

  <!-- 修改密码弹窗 -->
  <div
    v-if="store.profileModalVisible"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closeProfileModal()"
  >
    <ChangePasswordForm />
  </div>
</template>
