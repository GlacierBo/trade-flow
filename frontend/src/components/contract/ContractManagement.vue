<script setup>
import { ref, onMounted } from 'vue'
import { useContractStore } from '../../stores/contract'
import { useStockStore } from '../../stores/stock'
import DataTransfer from '../common/DataTransfer.vue'

const store = useContractStore()
const stockStore = useStockStore()

onMounted(() => {
  store.fetchContracts(stockStore.userId)
})

const showForm = ref(false)
const contractInput = ref('')
const saving = ref(false)
const inputError = ref('')

function openAdd() {
  contractInput.value = ''
  inputError.value = ''
  showForm.value = true
}

function parseContractInput(val) {
  const idx = val.indexOf('-')
  if (idx === -1) return { code: val.trim(), name: '' }
  return {
    code: val.slice(0, idx).trim(),
    name: val.slice(idx + 1).trim(),
  }
}

function validateCode(code) {
  return /^[A-Za-z]+\d+$/.test(code)
}

async function save() {
  inputError.value = ''
  const raw = contractInput.value.trim()
  if (!raw) return

  const { code, name } = parseContractInput(raw)
  if (!code) {
    inputError.value = '请输入合约代码'
    return
  }
  if (!validateCode(code)) {
    inputError.value = '合约代码格式错误，前面必须是字母+数字（如：IF2406）'
    return
  }
  if (!name) {
    inputError.value = '请输入合约名称，格式：代码-名称（如：IF2406-沪深300主力）'
    return
  }

  // 判重复
  const exists = store.contracts.some(c => c.code === code)
  if (exists) {
    inputError.value = `合约代码"${code}"已存在`
    return
  }

  saving.value = true
  const ok = await store.addContract(code, name, stockStore.userId)
  saving.value = false
  if (ok) showForm.value = false
}

async function remove(code) {
  // 检查网格交易中是否有正在使用的合约
  if (stockStore.trades && stockStore.trades.length) {
    const inUse = stockStore.trades.some(t => t.contract === code)
    if (inUse) {
      stockStore.showToast(`"${code}" 存在关联交易记录，不能删除`, 'error')
      return
    }
  }
  await store.removeContract(code, stockStore.userId)
}

function handleRemoveClick(e, code) {
  e.stopPropagation()
  remove(code)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-black text-gray-100">合约管理</h2>
      <div class="flex items-center gap-2">
        <DataTransfer
          page-name="合约"
          :get-export-data="() => ({ contracts: store.contracts })"
          :on-import="async (data) => {
            if (data.contracts) store.contracts = data.contracts
          }"
        />
        <button class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95" @click="openAdd">+ 新增合约</button>
      </div>
    </div>

    <div v-if="store.error" class="mb-4 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
      {{ store.error }}
    </div>

    <!-- Loading -->
    <div v-if="store.loading && !store.contracts.length" class="flex items-center justify-center py-16 text-gray-500">
      <span class="text-sm">加载中…</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="!store.contracts.length" class="flex flex-col items-center justify-center py-16 text-gray-500">
      <svg class="w-12 h-12 mb-3 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="12" y1="18" x2="12" y2="12" /><line x1="9" y1="15" x2="15" y2="15" />
      </svg>
      <p class="text-sm">暂无合约</p>
      <p class="text-xs text-gray-600 mt-1">点击上方按钮新增合约</p>
    </div>

    <!-- Card grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
      <div v-for="c in store.contracts" :key="c.code"
        class="relative group bg-gray-800/60 border border-gray-700/30 rounded-xl p-3.5 transition-all hover:bg-gray-800/80 hover:shadow-lg">
        <!-- Delete button top-right -->
        <button
          class="absolute -top-2 -right-2 w-6 h-6 flex items-center justify-center rounded-full bg-gray-700/80 border border-gray-600/50 text-gray-400 hover:text-red-400 hover:bg-red-500/20 hover:border-red-500/30 transition-all opacity-0 group-hover:opacity-100"
          @click="handleRemoveClick($event, c.code)">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <!-- Card content -->
        <div class="text-center">
          <div class="text-sm font-mono font-bold text-gray-100 tracking-wide truncate">{{ c.code }}</div>
          <div class="text-xs text-gray-400 mt-1.5 truncate">{{ c.name }}</div>
        </div>
      </div>
    </div>

    <!-- 新增合约弹窗 -->
    <div v-if="showForm" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
>
      <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
          <h3 class="text-base font-black text-gray-100">新增合约</h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="showForm = false">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="text-xs text-gray-400 font-bold mb-1.5 block">
              合约信息
              <span class="text-gray-600 font-normal ml-1">代码-名称</span>
            </label>
            <input
              v-model="contractInput"
              class="w-full bg-gray-700/50 border rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500 font-mono"
              :class="inputError ? 'border-red-500/50' : 'border-gray-600'"
              placeholder="如：IF2406-沪深300主力"
              @keydown.enter="save"
            />
            <p v-if="inputError" class="text-red-400 text-xs mt-1.5 flex items-center gap-1">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="flex-shrink-0">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {{ inputError }}
            </p>
          </div>
        </div>
        <div class="flex gap-3 px-5 pb-5">
          <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showForm = false">取消</button>
          <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all disabled:opacity-50" :disabled="!contractInput.trim() || saving" @click="save">
            {{ saving ? '保存中…' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
