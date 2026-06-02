<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useStockStore } from '../../stores/stock'
import { useContractStore } from '../../stores/contract'
import Dropdown from '../common/Dropdown.vue'

const store = useStockStore()
const contractStore = useContractStore()

const selectedContract = ref('')
const name = ref('')
const price = ref('')
const shares = ref('')
const feeRate = ref('0.02')
const isSubmitting = ref(false)
const showAddContract = ref(false)
const newContractCode = ref('')
const newContractName = ref('')

// 合约下拉选项
const contractOptions = computed(() => {
  return contractStore.contracts.map(c => ({
    value: c.code,
    label: `${c.code} - ${c.name}`
  }))
})

// 加载合约列表
onMounted(() => {
  if (store.isAuthenticated && store.userId) {
    contractStore.fetchContracts(store.userId)
  }
})

watch(() => store.tradeModalVisible, (v) => {
  if (v) {
    if (store.tradePresetData) {
      selectedContract.value = store.tradePresetData.contract || ''
      name.value = store.tradePresetData.name || ''
      price.value = ''
      shares.value = ''
      feeRate.value = '0.02'
      store.setTradeType('buy')
    } else {
      selectedContract.value = ''
      name.value = ''
      price.value = ''
      shares.value = ''
      feeRate.value = '0.02'
      store.setTradeType('buy')
    }
    showAddContract.value = false
  }
})

// 选择合约时自动填充名称
function onContractChange(code) {
  const contract = contractStore.contracts.find(c => c.code === code)
  if (contract) {
    name.value = contract.name
  }
}

// 新增合约
async function addContract() {
  if (!newContractCode.value.trim() || !newContractName.value.trim()) {
    store.showToast('请填写合约代码和名称', 'error')
    return
  }

  const success = await contractStore.addContract(
    newContractCode.value.trim(),
    newContractName.value.trim(),
    store.userId
  )

  if (success) {
    selectedContract.value = newContractCode.value.trim()
    name.value = newContractName.value.trim()
    newContractCode.value = ''
    newContractName.value = ''
    showAddContract.value = false
    store.showToast('合约添加成功', 'success')
  } else {
    store.showToast(contractStore.error || '添加失败', 'error')
  }
}

const amount = computed(() => {
  const p = parseFloat(price.value) || 0
  const s = parseInt(shares.value) || 0
  return (p * s).toFixed(2)
})

const fee = computed(() => {
  const amt = parseFloat(amount.value) || 0
  const rate = parseFloat(feeRate.value) / 100 || 0
  return Math.max(amt * rate, 0.2).toFixed(2)
})

const net = computed(() => {
  return (parseFloat(amount.value) + parseFloat(fee.value)).toFixed(2)
})

async function submit() {
  if (isSubmitting.value) return

  if (!selectedContract.value || !name.value.trim() || !price.value || !shares.value) {
    store.showToast('请填写完整信息', 'error')
    return
  }

  try {
    isSubmitting.value = true
    await store.createTrade({
      contract: selectedContract.value,
      name: name.value.trim(),
      price: price.value,
      shares: shares.value,
      feeRate: feeRate.value,
      minFee: 0.2
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div
    v-if="store.tradeModalVisible"
    class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.closeTradeModal()"
  >
    <div class="bg-gray-800 rounded-2xl max-w-md w-full shadow-2xl border border-gray-700/50 animate-fadeIn">
      <!-- 头部 -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/40">
        <h3 class="text-base font-bold text-gray-100">新增交易</h3>
        <button
          @click="store.closeTradeModal()"
          class="text-gray-400 hover:text-gray-200 transition"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="p-5 space-y-4">
        <!-- 合约选择 -->
        <div>
          <label class="block text-xs font-medium text-gray-400 mb-2">合约代码</label>
          <div v-if="!showAddContract" class="flex gap-2">
            <div class="flex-1">
              <Dropdown
                v-model="selectedContract"
                :options="contractOptions"
                placeholder="请选择合约"
                @change="onContractChange"
              />
            </div>
            <button
              @click="showAddContract = true"
              class="px-3 py-2.5 bg-gray-700/50 hover:bg-gray-600/50 border border-gray-600/50 rounded-lg text-gray-300 transition"
              title="新增合约"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
          <!-- 新增合约表单 -->
          <div v-else class="bg-gray-700/30 rounded-lg p-3 space-y-3">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-medium text-blue-400">新增合约</span>
              <button
                @click="showAddContract = false"
                class="text-gray-400 hover:text-gray-200 transition"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <input
              v-model="newContractCode"
              type="text"
              placeholder="合约代码，如 512690"
              class="w-full bg-gray-700/50 border border-gray-600/50 rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-gray-500 outline-none focus:border-blue-500/50 transition"
            >
            <input
              v-model="newContractName"
              type="text"
              placeholder="合约名称，如 酒ETF"
              class="w-full bg-gray-700/50 border border-gray-600/50 rounded-lg px-3 py-2 text-sm text-gray-100 placeholder-gray-500 outline-none focus:border-blue-500/50 transition"
            >
            <button
              @click="addContract"
              class="w-full py-2 bg-blue-500 hover:bg-blue-400 text-white text-sm font-bold rounded-lg transition active:scale-[0.98]"
            >确认添加</button>
          </div>
        </div>

        <!-- 交易类型 -->
        <div>
          <label class="block text-xs font-medium text-gray-400 mb-2">交易类型</label>
          <div class="flex gap-2">
            <button
              @click="store.setTradeType('buy')"
              :class="[
                'flex-1 py-2.5 rounded-lg text-sm font-bold transition active:scale-[0.98]',
                store.tradeType === 'buy'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'bg-gray-700/50 text-gray-400 border border-gray-600/50 hover:bg-gray-600/50'
              ]"
            >买入</button>
            <button
              @click="store.setTradeType('sell')"
              :class="[
                'flex-1 py-2.5 rounded-lg text-sm font-bold transition active:scale-[0.98]',
                store.tradeType === 'sell'
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'bg-gray-700/50 text-gray-400 border border-gray-600/50 hover:bg-gray-600/50'
              ]"
            >卖出</button>
          </div>
        </div>

        <!-- 合约名称（只读） -->
        <div>
          <label class="block text-xs font-medium text-gray-400 mb-2">合约名称</label>
          <input
            v-model="name"
            type="text"
            readonly
            class="w-full bg-gray-700/30 border border-gray-600/30 rounded-lg px-3 py-2.5 text-sm text-gray-300 cursor-not-allowed"
          >
        </div>

        <!-- 价格和份额 -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-2">交易价格</label>
            <input
              v-model="price"
              type="number"
              step="0.001"
              placeholder="0.000"
              class="w-full bg-gray-700/50 border border-gray-600/50 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 outline-none focus:border-blue-500/50 transition"
            >
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-400 mb-2">交易份额</label>
            <input
              v-model="shares"
              type="number"
              placeholder="0"
              class="w-full bg-gray-700/50 border border-gray-600/50 rounded-lg px-3 py-2.5 text-sm text-gray-100 placeholder-gray-600 outline-none focus:border-blue-500/50 transition"
            >
          </div>
        </div>

        <!-- 手续费率 -->
        <div>
          <label class="block text-xs font-medium text-gray-400 mb-2">手续费率 (%)</label>
          <input
            v-model="feeRate"
            type="number"
            step="0.001"
            class="w-full bg-gray-700/50 border border-gray-600/50 rounded-lg px-3 py-2.5 text-sm text-gray-100 outline-none focus:border-blue-500/50 transition"
          >
        </div>

        <!-- 费用汇总 -->
        <div class="bg-gray-700/30 rounded-xl p-4 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">成交金额</span>
            <span class="font-medium text-gray-200">¥{{ amount }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-400">佣金</span>
            <span class="font-medium text-gray-200">¥{{ fee }}</span>
          </div>
          <div class="flex justify-between text-sm pt-2 border-t border-gray-600/50">
            <span class="text-gray-300 font-bold">净额</span>
            <span class="font-bold text-blue-400">¥{{ net }}</span>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex gap-3 px-5 py-4 border-t border-gray-700/40">
        <button
          @click="store.closeTradeModal()"
          class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition"
        >取消</button>
        <button
          @click="submit"
          :disabled="isSubmitting"
          :class="[
            'flex-1 py-2.5 rounded-xl text-white font-bold text-sm transition shadow-lg',
            isSubmitting
              ? 'bg-gray-500 cursor-not-allowed opacity-50'
              : 'bg-blue-500 hover:bg-blue-400 shadow-blue-500/25 active:scale-[0.98]'
          ]"
        >
          {{ isSubmitting ? '提交中...' : '确认交易' }}
        </button>
      </div>
    </div>
  </div>
</template>
