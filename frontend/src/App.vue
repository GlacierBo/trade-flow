<script setup>
import { onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStockStore } from './stores/stock'
import LoginPage from './components/auth/LoginPage.vue'
import Sidebar from './components/layout/Sidebar.vue'
import TradeList from './components/trade/TradeList.vue'
import PositionList from './components/trade/PositionList.vue'
import TradeModal from './components/trade/TradeModal.vue'
import SellModal from './components/trade/SellModal.vue'
import ConfirmModal from './components/common/ConfirmModal.vue'
import Toast from './components/common/Toast.vue'
import DataTransfer from './components/common/DataTransfer.vue'
import PortfolioRatio from './components/portfolio/PortfolioRatio.vue'
import PortfolioModal from './components/portfolio/PortfolioModal.vue'
import UserManagement from './components/admin/UserManagement.vue'
import SponsorView from './components/sponsor/SponsorView.vue'
import ChangePasswordForm from './components/auth/ChangePasswordForm.vue'
import StockSearch from './components/stocks/StockSearch.vue'
import PortfolioAllocator2 from './components/portfolio/PortfolioAllocator2.vue'
import ContractManagement from './components/contract/ContractManagement.vue'
import DataManagement from './components/common/DataManagement.vue'

const store = useStockStore()
const route = useRoute()
const router = useRouter()

// 懒加载标记：记录各页面数据是否已加载
const loaded = ref({ home: false })

// 路由变化同步到 store，用来高亮侧边栏；并按页面懒加载数据
watch(() => route.name, (name) => {
  if (name && typeof name === 'string') {
    store.setView(name)
    // 首次访问 home 时加载交易、持仓、标签数据
    if (name === 'home' && !loaded.value.home && store.isAuthenticated) {
      loaded.value.home = true
      store.loadData()
    }
  }
}, { immediate: true })

onMounted(() => {
  store.checkAuth()
})
</script>

<template>
  <!-- Login Page -->
  <LoginPage v-if="!store.isAuthenticated" />

  <!-- Main App with Sidebar -->
  <div v-else class="flex min-h-screen">
    <Sidebar />

    <!-- Content Area -->
    <main class="flex-1 p-6 transition-all duration-300" :class="store.sidebarCollapsed ? 'ml-16' : 'ml-60'">
      <!-- 网格交易页 -->
      <div v-if="route.name === 'home'" class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- 左侧：交易明细 -->
        <div class="lg:col-span-7">
          <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 overflow-hidden">
            <!-- 头部 -->
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/30 bg-gradient-to-r from-gray-800/60 to-transparent">
              <div class="flex items-center gap-3">
                <div class="w-1.5 h-5 bg-blue-500 rounded-full" />
                <h2 class="text-base font-black text-gray-100 tracking-tight">交易明细</h2>
                <button
                  @click="store.openTradeModal()"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white text-xs font-bold rounded-lg transition-all duration-200 active:scale-95 shadow-lg shadow-blue-500/25"
                >
                  <span class="text-sm leading-none">+</span>
                  <span>新增</span>
                </button>
                <DataTransfer
                  page-name="交易"
                  :get-export-data="() => ({ trades: store.trades, positions: store.positions, tags: store.tags })"
                  :on-import="async (data) => {
                    if (data.trades) store.trades = data.trades
                    if (data.positions) store.positions = data.positions
                    if (data.tags) store.tags = data.tags
                    store.showToast('数据导入完成', 'success')
                  }"
                />
              </div>
              <div class="relative">
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-500 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
                <input
                  v-model="store.searchQuery"
                  type="text"
                  placeholder="搜索合约或单号…"
                  aria-label="搜索交易记录"
                  class="w-48 bg-gray-700/30 border border-gray-600/30 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 outline-none transition-all duration-200 focus:border-blue-500/40 focus:bg-gray-700/50"
                >
              </div>
            </div>
            <!-- 列表内容 -->
            <div class="p-4">
              <TradeList />
            </div>
          </div>
        </div>

        <!-- 右侧：持仓概览 -->
        <div class="lg:col-span-5">
          <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 overflow-hidden sticky top-6">
            <!-- 头部 -->
            <div class="px-5 py-4 border-b border-gray-700/30 bg-gradient-to-r from-gray-800/60 to-transparent">
              <div class="flex items-center gap-2">
                <div class="w-1.5 h-5 bg-green-500 rounded-full" />
                <h2 class="text-base font-black text-gray-100 tracking-tight">持仓概览</h2>
              </div>
            </div>
            <!-- 列表内容 -->
            <div class="p-4">
              <PositionList />
            </div>
          </div>
        </div>
      </div>

      <!-- 股票查询页 -->
      <StockSearch v-if="route.name === 'stocks'" />

      <!-- 我的持仓页 -->
      <PortfolioAllocator2 v-if="route.name === 'allocator2'" />

      <!-- 合约管理页 -->
      <div v-if="route.name === 'contracts'" class="py-4">
        <ContractManagement />
      </div>

      <!-- 持仓比例页 -->
      <PortfolioRatio v-if="route.name === 'portfolio'" />

      <!-- 数据管理页 -->
      <div v-if="route.name === 'data'" class="py-4">
        <DataManagement />
      </div>

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
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
  >
    <ChangePasswordForm />
  </div>
</template>
