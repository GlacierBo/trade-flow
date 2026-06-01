<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()
const showMenu = ref(false)

function onDocClick(e) {
  if (!e.target.closest('.user-menu-area')) {
    showMenu.value = false
  }
}
onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))

const menuItems = [
  { key: 'home', label: '网格交易', icon: 'home' },
  { key: 'stocks', label: '股票查询', icon: 'search' },
  { key: 'portfolio', label: '持仓比例', icon: 'chart' },
  { key: 'users', label: '用户管理', icon: 'users', adminOnly: true },
]

const iconMap = {
  home: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />`,
  chart: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />`,
  users: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />`,
  search: `<circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />`,
}

function toggleMenu() {
  showMenu.value = !showMenu.value
}

function openProfile() {
  showMenu.value = false
  store.openProfileModal()
}

function handleLogout() {
  showMenu.value = false
  store.showConfirm('确定要退出登录吗？', () => {
    store.logout()
    window.location.reload()
  })
}
</script>

<template>
  <aside class="w-60 bg-gray-800/80 border-r border-gray-700/50 flex flex-col h-screen fixed left-0 top-0">
    <!-- Logo -->
    <div class="p-5 border-b border-gray-700/50">
      <h1 class="text-lg font-black tracking-tight accent-gradient">TradeFlow</h1>
      <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Smart Trading Management</p>
    </div>

    <!-- Menu -->
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto scrollbar-thin">
      <button
        v-for="item in menuItems.filter(i => !i.adminOnly || store.isAdmin)"
        :key="item.key"
        @click="store.setView(item.key)"
        :class="[
          'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all',
          store.currentView === item.key
            ? 'bg-blue-500/20 text-blue-400'
            : 'text-gray-400 hover:text-gray-100 hover:bg-gray-700/50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" v-html="iconMap[item.icon]" />
        <span>{{ item.label }}</span>
      </button>
    </nav>

    <!-- Sponsor Button -->
    <div class="px-3 pb-2">
      <button
        @click="store.setView('sponsor')"
        :class="[
          'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all',
          store.currentView === 'sponsor'
            ? 'bg-amber-500/20 text-amber-400'
            : 'text-gray-400 hover:text-gray-100 hover:bg-gray-700/50'
        ]"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
        <span>赞助作者</span>
      </button>
    </div>

    <!-- User Section -->
    <div class="p-3 border-t border-gray-700/50 relative user-menu-area">
      <div class="flex items-center gap-3 px-3 py-2">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-400 flex items-center justify-center text-white text-xs font-black flex-shrink-0">
          {{ store.username.charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-gray-200 truncate">{{ store.username }}</p>
          <p class="text-[10px] text-gray-500">已登录</p>
        </div>
        <button
          @click="toggleMenu"
          class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700/50 transition-all flex-shrink-0"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
          </svg>
        </button>
      </div>

      <!-- Dropdown Menu -->
      <div
        v-if="showMenu"
        class="absolute bottom-full left-3 right-3 mb-1 bg-gray-700 border border-gray-600 rounded-xl overflow-hidden shadow-xl animate-fadeIn"
      >
        <button
          @click="openProfile"
          class="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-gray-300 hover:text-gray-100 hover:bg-gray-600/50 transition-all"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          个人中心
        </button>
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-gray-300 hover:text-red-400 hover:bg-red-500/10 transition-all"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          退出登录
        </button>
      </div>
    </div>
  </aside>
</template>
