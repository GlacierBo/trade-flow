<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useAllocator2Store } from '../../stores/allocator2'
import { useContractStore } from '../../stores/contract'
import { useStockStore } from '../../stores/stock'
import Dropdown from '../common/Dropdown.vue'
import DataTransfer from '../common/DataTransfer.vue'
import * as echarts from 'echarts'

const store = useAllocator2Store()
const contractStore = useContractStore()
const stockStore = useStockStore()
const chartRef = ref(null)
let chart = null
let ro = null

onMounted(() => {
  store.init(stockStore.userId)
  contractStore.fetchContracts(stockStore.userId)
  tryInit()
  setTimeout(tryInit, 300)
  setTimeout(tryInit, 1000)
})
onUnmounted(() => {
  ro?.disconnect()
  chart?.dispose()
})

watch(() => store.positions.length, () => {
  if (!chart && store.positions.length && store.totalAmount) tryInit()
}, { flush: 'post' })

watch(() => store.positions.map(p => p.amount).join(','), () => {
  nextTick(updateChart)
})

// ========== 品种汇总 ==========
const varietyGroups = computed(() => {
  const map = {}
  store.positions.forEach(p => {
    if (!map[p.variety]) {
      map[p.variety] = {
        variety: p.variety,
        positions: [],
        totalAmount: 0,
        color: p.color,
      }
    }
    map[p.variety].positions.push(p)
    map[p.variety].totalAmount += (p.amount || 0)
  })
  return Object.values(map)
})

// 合约下拉选项
const contractOptions = computed(() => {
  return contractStore.contracts.map(c => ({
    value: c.code,
    label: `${c.code} - ${c.name}`
  }))
})

function tryInit() {
  if (chart) return
  if (!chartRef.value || !chartRef.value.isConnected || !chartRef.value.offsetParent) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  updateChart()
  chart.on('click', (params) => {
    if (params.data?.variety != null) {
      selectedVariety.value = params.data.variety
      showPositions.value = true
    }
  })
  ro = new ResizeObserver(() => chart?.resize())
  ro.observe(chartRef.value)
}

const chartOption = computed(() => {
  const groups = varietyGroups.value
  if (!groups.length || !store.totalAmount) return null

  const data = groups.map((g) => {
    const ratio = g.totalAmount / store.totalAmount
    const first = g.positions[0]
    const rgb = (first.color || 'rgba(59,130,246,0.3)').replace(/rgba?\(([^)]+).*/, '$1').split(',').slice(0, 3).join(',')
    const alpha = Math.max(0.06, 0.1 + ratio * 0.3)

    return {
      name: g.variety,
      value: g.totalAmount || 1,
      variety: g.variety,
      itemStyle: {
        color: `rgba(${rgb},${alpha})`,
        borderColor: 'rgba(75,85,99,0.6)',
        borderWidth: 1,
      },
      label: {
        formatter: () => {
          const pct = store.totalAmount ? (g.totalAmount / store.totalAmount * 100).toFixed(1) : 0
          const lines = [g.variety, `${pct}%`]
          if (showAmounts.value) {
            lines.push(`¥${fmt(g.totalAmount)}`)
          }
          return lines.join('\n')
        },
      },
    }
  })

  return {
    tooltip: {
      formatter: (params) => {
        const g = groups.find(x => x.variety === params.data.variety)
        if (!g) return ''
        return [
          `<strong>${g.variety}</strong>`,
          `合计：¥${fmt(g.totalAmount)}`,
          `占比：${(g.totalAmount / store.totalAmount * 100).toFixed(1)}%`,
          `合约数：${g.positions.length}`,
        ].join('<br/>')
      },
    },
    series: [{
      type: 'treemap',
      roam: false,
      nodeClick: false,
      width: '98%',
      height: '96%',
      top: '2%',
      left: '1%',
      breadcrumb: { show: false },
      levels: [{ itemStyle: { borderColor: '#1f2937', borderWidth: 3, gapWidth: 3 } }],
      data,
    }],
  }
})

function updateChart() {
  if (!chart) return
  const opt = chartOption.value
  if (opt) chart.setOption(opt, true)
}

// ========== 金额显隐 ==========
const showAmounts = ref(false)
function toggleAmounts() {
  showAmounts.value = !showAmounts.value
  updateChart()
}

// ========== 新增品种弹窗 ==========
const showPositionForm = ref(false)
const formVariety = ref('')
const formContractCode = ref('')
const formPrice = ref('')

function openPositionForm() {
  formVariety.value = ''
  formContractCode.value = ''
  formPrice.value = ''
  showPositionForm.value = true
}

async function submitPosition() {
  if (!formVariety.value.trim() || !formContractCode.value || !formPrice.value) return
  const c = contractStore.contracts.find(x => x.code === formContractCode.value)
  try {
    await store.addPosition(
      formVariety.value.trim(),
      formContractCode.value,
      c?.name || '',
      Number(formPrice.value),
      stockStore.userId,
    )
    showPositionForm.value = false
    updateChart()
  } catch (e) {
    console.error('添加持仓失败', e)
  }
}

// ========== 新增合约弹窗（快速添加） ==========
const showContractForm = ref(false)
const contractCodeInput = ref('')
const contractNameInput = ref('')

function openContractForm() {
  contractCodeInput.value = ''
  contractNameInput.value = ''
  showContractForm.value = true
}

async function submitContract() {
  if (!contractCodeInput.value.trim() || !contractNameInput.value.trim()) return
  await contractStore.addContract(contractCodeInput.value.trim(), contractNameInput.value.trim(), stockStore.userId)
  formContractCode.value = contractCodeInput.value.trim()
  showContractForm.value = false
}

// ========== 编辑持仓弹窗 ==========
const editPositionPrice = ref(0)
function openEditPosition(id) {
  store.setEditPosition(id)
  const p = store.positions.find(x => x.id === id)
  if (p) editPositionPrice.value = p.price
}
async function saveEditPosition() {
  if (store.editPositionId != null) {
    try {
      await store.updatePosition(store.editPositionId, { price: Number(editPositionPrice.value) }, stockStore.userId)
    } catch (e) {
      console.error('更新持仓失败', e)
      return
    }
    store.clearEdit()
    updateChart()
  }
}

// ========== 持仓抽屉 ==========
const showPositions = ref(false)
const selectedVariety = ref(null)

const selectedGroup = computed(() =>
  varietyGroups.value.find(g => g.variety === selectedVariety.value) || null
)

function clickVariety(variety) {
  selectedVariety.value = variety
}

function backToVarieties() {
  selectedVariety.value = null
}

function clickContract(contractId) {
  showPositions.value = false
  nextTick(() => openEditPosition(contractId))
}

async function removePosition(id) {
  try {
    await store.removePosition(id, stockStore.userId)
    updateChart()
  } catch (e) {
    console.error('删除持仓失败', e)
  }
}
async function handleDeletePosition() {
  await removePosition(store.editPositionId)
  store.clearEdit()
}

function fmt(v) { return Number(v || 0).toFixed(2) }
</script>

<template>
  <div class="flex flex-col gap-4" style="height: calc(100vh - 8rem); min-height: 500px;">
    <!-- 顶栏 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-400">总金额：</span>
        <span class="text-2xl font-black text-blue-400">{{ showAmounts ? '¥' + fmt(store.totalAmount) : '***' }}</span>
        <button
          class="w-6 h-6 flex items-center justify-center rounded-lg transition-all text-sm"
          :class="showAmounts ? 'bg-gray-700/50 text-gray-400 hover:text-amber-400' : 'bg-amber-500/20 text-amber-400'"
          :title="showAmounts ? '隐藏金额' : '显示金额'"
          @click="toggleAmounts"
        >
          <svg v-if="showAmounts" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
        </button>
      </div>
      <div class="flex items-center gap-2">
        <button class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95" @click="openPositionForm">+ 新增品种</button>
        <button class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition-all active:scale-95" @click="showPositions = !showPositions; selectedVariety = null">查看持仓</button>
        <DataTransfer
          page-name="品种"
          :get-export-data="() => ({ positions: store.positions })"
          :on-import="async (data) => {
            if (data.positions) {
              await store.replaceAllPositions(data.positions, stockStore.userId)
              updateChart()
            }
          }"
        />
      </div>
    </div>

    <!-- ECharts Treemap -->
    <div
      ref="chartRef"
      v-if="store.positions.length"
      class="flex-1 bg-gray-800/20 border border-gray-700/30 rounded-2xl overflow-hidden"
      style="min-height: 400px;"
    />

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center bg-gray-800/30 border border-gray-700/30 rounded-2xl text-gray-500" style="min-height: 400px;">
      <svg class="w-16 h-16 mb-4 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
      </svg>
      <p class="text-sm mb-1">暂无持仓数据</p>
      <p class="text-xs text-gray-600">选择品种和合约，填入价格</p>
    </div>
  </div>

  <!-- 新增品种弹窗 -->
  <div v-if="showPositionForm" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain">
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <h3 class="text-base font-black text-gray-100">新增品种</h3>
        <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="showPositionForm = false">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">品种</label>
          <input v-model="formVariety" list="variety-list" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="输入或选择品种" />
          <datalist id="variety-list">
            <option v-for="v in store.varieties" :key="v" :value="v" />
          </datalist>
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约</label>
          <div class="flex gap-2">
            <div class="flex-1">
              <Dropdown
                v-model="formContractCode"
                :options="contractOptions"
                placeholder="选择合约"
              />
            </div>
            <button class="w-10 h-10 flex items-center justify-center rounded-xl bg-gray-700/50 border border-gray-600 text-gray-400 hover:text-blue-400 hover:border-blue-500 transition-all flex-shrink-0" title="新增合约" @click="openContractForm">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
            </button>
          </div>
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">价格</label>
          <input v-model.number="formPrice" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：3500" @keydown.enter="submitPosition" />
        </div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showPositionForm = false">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" :class="(!formVariety.trim() || !formContractCode || !formPrice) ? 'opacity-50' : ''" :disabled="!formVariety.trim() || !formContractCode || !formPrice" @click="submitPosition">确定</button>
      </div>
    </div>
  </div>

  <!-- 新增合约弹窗 -->
  <div v-if="showContractForm" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain">
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <h3 class="text-base font-black text-gray-100">新增合约</h3>
        <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="showContractForm = false">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约代码</label>
          <input v-model="contractCodeInput" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：IF2406" />
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约名称</label>
          <input v-model="contractNameInput" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：沪深300主力" @keydown.enter="submitContract" />
        </div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showContractForm = false">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" :class="(!contractCodeInput.trim() || !contractNameInput.trim()) ? 'opacity-50' : ''" :disabled="!contractCodeInput.trim() || !contractNameInput.trim()" @click="submitContract">确定</button>
      </div>
    </div>
  </div>

  <!-- 编辑持仓弹窗 -->
  <div v-if="store.editPositionId != null" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"
>
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn" @click.stop>
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <div>
          <h3 class="text-lg font-black text-gray-100">{{ store.positions.find(p => p.id === store.editPositionId)?.variety }}</h3>
          <p class="text-xs text-gray-500 mt-0.5">
            {{ store.positions.find(p => p.id === store.editPositionId)?.contractCode }}
            <span class="mx-1.5">|</span>
            {{ store.positions.find(p => p.id === store.editPositionId)?.contractName }}
          </p>
        </div>
        <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="store.clearEdit()">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">价格</label>
          <input v-model.number="editPositionPrice" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" @keydown.enter="saveEditPosition" />
        </div>
        <div class="flex items-center gap-2 text-sm">
          <div class="flex-1 h-2 rounded-full bg-gray-700/50 overflow-hidden">
            <div class="h-full rounded-full transition-all duration-500 bg-blue-500" :style="{ width: Math.min((editPositionPrice / store.totalAmount) * 100, 100) + '%' }" />
          </div>
          <span class="text-xs font-mono text-gray-400">{{ store.totalAmount ? ((editPositionPrice / store.totalAmount) * 100).toFixed(1) : 0 }}%</span>
        </div>
        <button class="w-full py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-bold rounded-xl transition-all" @click="handleDeletePosition">删除此持仓</button>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="store.clearEdit()">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" @click="saveEditPosition">确定</button>
      </div>
    </div>
  </div>

  <!-- 持仓抽屉 -->
  <Transition name="drawer">
    <div v-if="showPositions" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div class="absolute right-0 top-0 h-full w-80 max-w-[90vw] bg-gray-800 border-l border-gray-700/50 shadow-2xl flex flex-col">

        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50 flex-shrink-0">
          <div class="flex items-center gap-2">
            <button v-if="selectedVariety" class="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="backToVarieties">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <h3 class="text-base font-black text-gray-100">{{ selectedVariety || '持仓明细' }}</h3>
          </div>
          <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="showPositions = false">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-5 space-y-3">

          <!-- 品种汇总列表 -->
          <template v-if="!selectedVariety">
            <div
              v-for="g in varietyGroups"
              :key="g.variety"
              class="bg-gray-700/30 rounded-xl p-4 border border-gray-700/50 cursor-pointer hover:bg-gray-700/50 transition-all"
              @click="clickVariety(g.variety)"
            >
              <div class="flex items-center gap-2 mb-3">
                <span class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: g.color.replace('0.35', '1').replace('0.25', '1') }" />
                <span class="text-sm font-bold text-gray-200">{{ g.variety }}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between"><span class="text-gray-500">价格合计</span><span class="text-gray-300 font-mono">¥{{ fmt(g.totalAmount) }}</span></div>
                <div class="flex justify-between">
                  <span class="text-gray-500">占比</span>
                  <span class="text-gray-300 font-mono">{{ store.totalAmount ? (g.totalAmount / store.totalAmount * 100).toFixed(1) : 0 }}%</span>
                </div>
                <div class="flex justify-between"><span class="text-gray-500">合约数</span><span class="text-gray-300 font-mono">{{ g.positions.length }}</span></div>
              </div>
            </div>
            <div v-if="!varietyGroups.length" class="text-center text-gray-500 text-sm py-12">暂无持仓数据</div>
          </template>

          <!-- 品种内合约列表 -->
          <template v-else>
            <div
              v-for="p in selectedGroup?.positions"
              :key="p.id"
              class="bg-gray-700/30 rounded-xl p-4 border border-gray-700/50 cursor-pointer hover:bg-gray-700/50 transition-all"
              @click="clickContract(p.id)"
            >
              <div class="flex items-center gap-2 mb-3">
                <span class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: p.color.replace('0.35', '1').replace('0.25', '1') }" />
                <span class="text-sm font-bold text-gray-200">{{ p.contractCode }}</span>
              </div>
              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between"><span class="text-gray-500">合约名称</span><span class="text-gray-300">{{ p.contractName }}</span></div>
                <div class="flex justify-between"><span class="text-gray-500">价格</span><span class="text-gray-300 font-mono">¥{{ fmt(p.price) }}</span></div>
                <div class="flex justify-between"><span class="text-gray-500">占用</span><span class="text-gray-300 font-mono">¥{{ fmt(p.amount) }}</span></div>
              </div>
            </div>
          </template>

        </div>

        <!-- 品种底部合计 -->
        <div v-if="selectedVariety && selectedGroup" class="flex-shrink-0 border-t border-gray-700/50 px-5 py-3 text-xs text-gray-500 flex justify-between">
          <span>合计：¥{{ fmt(selectedGroup.totalAmount) }}</span>
          <span>占比：{{ store.totalAmount ? (selectedGroup.totalAmount / store.totalAmount * 100).toFixed(1) : 0 }}%</span>
        </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-active > div:last-child,
.drawer-leave-active > div:last-child {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from > div:last-child,
.drawer-leave-to > div:last-child {
  transform: translateX(100%);
}
</style>
