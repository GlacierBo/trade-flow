<script setup>
import { onMounted } from 'vue'
import { useStockStore } from './stores/stock'
import LoginPage from './components/LoginPage.vue'
import Sidebar from './components/Sidebar.vue'
import TradeList from './components/TradeList.vue'
import PositionList from './components/PositionList.vue'
import SponsorView from './components/SponsorView.vue'
import TradeModal from './components/TradeModal.vue'
import SellModal from './components/SellModal.vue'
import ConfirmModal from './components/common/ConfirmModal.vue'
import Toast from './components/common/Toast.vue'

const store = useStockStore()

onMounted(() => {
  store.checkAuth()
  if (store.isAuthenticated) {
    store.loadData()
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
      <!-- Home View -->
      <div v-if="store.currentView === 'home'" class="max-w-5xl mx-auto">
        <div class="flex flex-wrap justify-between items-center gap-4 mb-6">
          <div>
            <h2 class="text-lg font-black text-blue-400">交易管理</h2>
            <p class="text-xs text-gray-500">管理你的所有交易记录和持仓</p>
          </div>
          <button
            @click="store.openTradeModal()"
            class="bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white px-5 py-2.5 rounded-xl font-black shadow-lg shadow-blue-500/30 transition-all active:scale-95 text-sm"
          >
            + 新增交易
          </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
          <div class="lg:col-span-2">
            <div class="bg-gray-800/50 rounded-2xl p-5 border border-gray-700/50">
              <div class="flex flex-wrap justify-between items-center gap-3 mb-4">
                <h3 class="text-base font-black text-gray-200">交易明细</h3>
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
            <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden sticky top-6">
              <div class="p-4">
                <h3 class="text-base font-black text-gray-200 mb-4">持仓概览</h3>
                <PositionList />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sponsor View -->
      <div v-else-if="store.currentView === 'sponsor'" class="py-8">
        <SponsorView />
      </div>
    </main>
  </div>

  <TradeModal />
  <SellModal />
  <ConfirmModal />
  <Toast />
</template>
