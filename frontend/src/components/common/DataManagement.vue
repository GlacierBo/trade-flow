<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStockStore } from '../../stores/stock'
import { useWatchlistStore } from '../../stores/watchlist'
import { useContractStore } from '../../stores/contract'
import { useAllocator2Store } from '../../stores/allocator2'

const stockStore = useStockStore()
const watchlistStore = useWatchlistStore()
const contractStore = useContractStore()
const allocator2Store = useAllocator2Store()

const activeSection = ref('trades')
const copied = ref('')
const saved = ref('')
const editError = ref('')

const sections = computed(() => [
  {
    key: 'trades',
    label: '网格交易',
    icon: 'home',
    getData: () => ({
      trades: stockStore.trades,
      positions: stockStore.positions,
      tags: stockStore.tags,
    }),
    setData: (data) => {
      if (data.trades) stockStore.trades = data.trades
      if (data.positions) stockStore.positions = data.positions
      if (data.tags) stockStore.tags = data.tags
    },
  },
  {
    key: 'watchlist',
    label: '我的自选',
    icon: 'star',
    getData: () => ({
      watchlist: watchlistStore.items,
    }),
    setData: (data) => {
      if (data.watchlist) watchlistStore.items = data.watchlist
    },
  },
  {
    key: 'allocator2',
    label: '我的持仓',
    icon: 'grid',
    getData: () => ({
      positions: allocator2Store.positions,
    }),
    setData: async (data) => {
      if (data.positions) {
        await allocator2Store.replaceAllPositions(data.positions, stockStore.userId)
      }
    },
  },
  {
    key: 'contracts',
    label: '合约管理',
    icon: 'file',
    getData: () => ({
      contracts: contractStore.contracts,
    }),
    setData: (data) => {
      if (data.contracts) contractStore.contracts = data.contracts
    },
  },
  {
    key: 'portfolio',
    label: '持仓比例',
    icon: 'chart',
    getData: () => ({
      portfolioItems: stockStore.portfolioItems,
    }),
    setData: (data) => {
      if (data.portfolioItems) stockStore.portfolioItems = data.portfolioItems
    },
  },
  {
    key: 'users',
    label: '用户管理',
    icon: 'users',
    adminOnly: true,
    getData: () => ({
      users: stockStore.users,
    }),
    setData: (data) => {
      if (data.users) stockStore.users = data.users
    },
  },
])

const activeSectionConfig = computed(() => sections.value.find(s => s.key === activeSection.value))

const jsonText = ref('')

function switchSection(key) {
  activeSection.value = key
  editError.value = ''
  refreshJson()
}

function refreshJson() {
  const section = sections.value.find(s => s.key === activeSection.value)
  if (section) {
    jsonText.value = JSON.stringify(section.getData(), null, 2)
  }
}

async function handleCopy() {
  try {
    await navigator.clipboard.writeText(jsonText.value)
    copied.value = activeSection.value
    setTimeout(() => { copied.value = '' }, 2000)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = jsonText.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = activeSection.value
    setTimeout(() => { copied.value = '' }, 2000)
  }
}

async function handleSave() {
  editError.value = ''
  let data
  try {
    data = JSON.parse(jsonText.value)
  } catch (e) {
    editError.value = `JSON 格式错误: ${e.message}`
    return
  }
  if (!data || typeof data !== 'object') {
    editError.value = '无效的 JSON 数据'
    return
  }
  const section = sections.value.find(s => s.key === activeSection.value)
  if (section) {
    try {
      await section.setData(data)
      saved.value = activeSection.value
      setTimeout(() => { saved.value = '' }, 2000)
      refreshJson()
    } catch (e) {
      editError.value = `保存失败: ${e.message}`
    }
  }
}

onMounted(() => {
  refreshJson()
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-5">
    <!-- 页头 -->
    <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 p-5">
      <div class="flex items-center gap-3 mb-1">
        <div class="w-1.5 h-6 bg-violet-500 rounded-full" />
        <h1 class="text-lg font-black text-gray-100 tracking-tight">数据管理</h1>
      </div>
      <p class="text-xs text-gray-500 ml-[18px]">查看、编辑和导出各页面的 JSON 数据</p>
    </div>

    <!-- 数据分类标签 -->
    <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 p-4">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="sec in sections.filter(s => !s.adminOnly || stockStore.isAdmin)"
          :key="sec.key"
          @click="switchSection(sec.key)"
          class="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all duration-200"
          :class="activeSection === sec.key
            ? 'bg-violet-500/15 text-violet-400 shadow-sm shadow-violet-500/10'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700/40'"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <template v-if="sec.icon === 'home'">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" /><polyline points="9 22 9 12 15 12 15 22" />
            </template>
            <template v-else-if="sec.icon === 'star'">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </template>
            <template v-else-if="sec.icon === 'grid'">
              <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
            </template>
            <template v-else-if="sec.icon === 'file'">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
            </template>
            <template v-else-if="sec.icon === 'chart'">
              <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </template>
            <template v-else-if="sec.icon === 'users'">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
            </template>
          </svg>
          {{ sec.label }}
        </button>
      </div>
    </div>

    <!-- JSON 编辑器 -->
    <div class="bg-gray-800/40 border border-gray-700/30 rounded-2xl shadow-lg shadow-black/20 overflow-hidden">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/30 bg-gradient-to-r from-gray-800/60 to-transparent">
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-5 bg-violet-500 rounded-full" />
          <h2 class="text-base font-black text-gray-100 tracking-tight">{{ activeSectionConfig?.label }} 数据</h2>
          <span class="text-xs text-gray-500 font-mono">JSON</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="handleCopy"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200"
            :class="copied === activeSection
              ? 'bg-green-500/15 text-green-400'
              : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 hover:text-gray-100'"
          >
            <svg v-if="copied === activeSection" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <svg v-else class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
            </svg>
            {{ copied === activeSection ? '已复制' : '复制' }}
          </button>
          <button
            @click="handleSave"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200"
            :class="saved === activeSection
              ? 'bg-green-500/15 text-green-400'
              : 'bg-violet-500/15 text-violet-400 hover:bg-violet-500/25 hover:text-violet-300'"
          >
            <svg v-if="saved === activeSection" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <svg v-else class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" />
              <polyline points="17 21 17 13 7 13 7 21" /><polyline points="7 3 7 8 15 8" />
            </svg>
            {{ saved === activeSection ? '已保存' : '保存修改' }}
          </button>
        </div>
      </div>
      <div class="p-5">
        <textarea
          v-model="jsonText"
          class="w-full bg-gray-900/80 border rounded-xl px-4 py-3 text-sm font-mono leading-relaxed outline-none resize-y transition-colors"
          :class="editError ? 'border-red-500/50' : 'border-gray-700/50 focus:border-violet-500/40'"
          rows="24"
          spellcheck="false"
          wrap="off"
        ></textarea>
        <p v-if="editError" class="text-red-400 text-xs mt-2 flex items-center gap-1">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="flex-shrink-0">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {{ editError }}
        </p>
        <p v-else class="text-gray-600 text-xs mt-2">修改 JSON 后点击「保存修改」即可生效，数据会同步到当前页面</p>
      </div>
    </div>
  </div>
</template>
