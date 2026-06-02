<script setup>
import { ref, onMounted } from 'vue'
import { useContractStore } from '../stores/contract'
import { useStockStore } from '../stores/stock'

const store = useContractStore()
const stockStore = useStockStore()

onMounted(() => {
  store.fetchContracts(stockStore.userId)
})

const showForm = ref(false)
const editCode = ref('')
const codeInput = ref('')
const nameInput = ref('')
const isEdit = ref(false)
const saving = ref(false)

function openAdd() {
  editCode.value = ''
  codeInput.value = ''
  nameInput.value = ''
  isEdit.value = false
  showForm.value = true
}

function openEdit(c) {
  editCode.value = c.code
  codeInput.value = c.code
  nameInput.value = c.name
  isEdit.value = true
  showForm.value = true
}

async function save() {
  if (!codeInput.value.trim() || !nameInput.value.trim()) return
  saving.value = true
  let ok
  if (isEdit.value) {
    ok = await store.updateContract(editCode.value, codeInput.value.trim(), nameInput.value.trim(), stockStore.userId)
  } else {
    ok = await store.addContract(codeInput.value.trim(), nameInput.value.trim(), stockStore.userId)
  }
  saving.value = false
  if (ok) showForm.value = false
}

async function remove(code) {
  await store.removeContract(code, stockStore.userId)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-black text-gray-100">合约管理</h2>
      <button class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95" @click="openAdd">+ 新增合约</button>
    </div>

    <div v-if="store.error" class="mb-4 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
      {{ store.error }}
    </div>

    <div class="bg-gray-800/30 border border-gray-700/30 rounded-2xl overflow-hidden">
      <div v-if="store.loading && !store.contracts.length" class="flex items-center justify-center py-16 text-gray-500">
        <span class="text-sm">加载中...</span>
      </div>
      <div v-else-if="!store.contracts.length" class="flex flex-col items-center justify-center py-16 text-gray-500">
        <svg class="w-12 h-12 mb-3 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="12" y1="18" x2="12" y2="12" /><line x1="9" y1="15" x2="15" y2="15" />
        </svg>
        <p class="text-sm">暂无合约</p>
        <p class="text-xs text-gray-600 mt-1">点击上方按钮新增合约</p>
      </div>
      <table v-else class="w-full">
        <thead>
          <tr class="text-xs text-gray-500 border-b border-gray-700/50">
            <th class="text-left px-5 py-3 font-bold">合约代码</th>
            <th class="text-left px-5 py-3 font-bold">合约名称</th>
            <th class="text-right px-5 py-3 font-bold">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in store.contracts" :key="c.code" class="border-b border-gray-700/30 hover:bg-gray-700/20 transition-colors">
            <td class="px-5 py-3.5 text-sm font-mono text-gray-200">{{ c.code }}</td>
            <td class="px-5 py-3.5 text-sm text-gray-300">{{ c.name }}</td>
            <td class="px-5 py-3.5 text-right">
              <button class="px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 text-xs font-bold rounded-lg transition-all mr-2" @click="openEdit(c)">编辑</button>
              <button class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold rounded-lg transition-all" @click="remove(c.code)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新增/编辑合约弹窗 -->
    <div v-if="showForm" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
          <h3 class="text-base font-black text-gray-100">{{ isEdit ? '编辑合约' : '新增合约' }}</h3>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="showForm = false">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          </button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约代码</label>
            <input v-model="codeInput" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：IF2406" />
          </div>
          <div>
            <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约名称</label>
            <input v-model="nameInput" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：沪深300主力" @keydown.enter="save" />
          </div>
        </div>
        <div class="flex gap-3 px-5 pb-5">
          <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showForm = false">取消</button>
          <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all disabled:opacity-50" :disabled="!codeInput.trim() || !nameInput.trim() || saving" @click="save">
            {{ saving ? '保存中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
