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
import PortfolioRatio from './components/portfolio/PortfolioRatio.vue'
import PortfolioModal from './components/portfolio/PortfolioModal.vue'
import UserManagement from './components/admin/UserManagement.vue'
import SponsorView from './components/sponsor/SponsorView.vue'
import ChangePasswordForm from './components/auth/ChangePasswordForm.vue'
import StockSearch from './components/stocks/StockSearch.vue'
import PortfolioAllocator from './components/portfolio/PortfolioAllocator.vue'
import PortfolioAllocator2 from './components/portfolio/PortfolioAllocator2.vue'
import ContractManagement from './components/contract/ContractManagement.vue'

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
      <div v-if="route.name === 'home'" class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <!-- 左侧：交易明细 -->
        <div class="lg:col-span-7">
          <div class="bg-gray-800/60 rounded-2xl border border-gray-700/40 shadow-lg shadow-black/20">
            <!-- 头部 -->
            <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/40">
              <div class="flex items-center gap-3">
                <h2 class="text-base font-bold text-gray-100">交易明细</h2>
                <button
                  @click="store.openTradeModal()"
                  class="inline-flex items-center gap-1 px-3 py-1.5 bg-blue-500 hover:bg-blue-400 text-white text-xs font-bold rounded-lg transition-all active:scale-95 shadow-md shadow-blue-500/25"
                >
                  <span class="text-sm leading-none">+</span>
                  <span>新增</span>
                </button>
              </div>
              <div class="relative">
                <input
                  v-model="store.searchQuery"
                  type="text"
                  placeholder="搜索合约或单号..."
                  class="w-48 bg-gray-700/40 border border-gray-600/50 rounded-lg px-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 outline-none focus:border-blue-500/50 focus:bg-gray-700/60 transition-all"
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
          <div class="bg-gray-800/60 rounded-2xl border border-gray-700/40 shadow-lg shadow-black/20 sticky top-6">
            <!-- 头部 -->
            <div class="px-5 py-4 border-b border-gray-700/40">
              <h2 class="text-base font-bold text-gray-100">持仓概览</h2>
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

      <!-- 持仓分配页 -->
      <PortfolioAllocator v-if="route.name === 'allocator'" />
      <PortfolioAllocator2 v-if="route.name === 'allocator2'" />

      <!-- 合约管理页 -->
      <div v-if="route.name === 'contracts'" class="py-4">
        <ContractManagement />
      </div>

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
