<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useAllocatorStore } from '../stores/allocator'
import * as echarts from 'echarts'

const store = useAllocatorStore()
const chartRef = ref(null)
let chart = null
let ro = null

onMounted(() => {
  store.init()
  tryInit()
  setTimeout(tryInit, 300)
  setTimeout(tryInit, 1000)
})
onUnmounted(() => {
  ro?.disconnect()
  chart?.dispose()
})

watch([() => store.buckets.length, () => store.totalAmount], () => {
  if (!chart && store.buckets.length && store.totalAmount) tryInit()
}, { flush: 'post' })

watch(() => store.buckets.map(b => b.percentage + (b.usedAmount || 0)).join(','), () => {
  nextTick(updateChart)
})

function tryInit() {
  if (chart) return
  if (!chartRef.value || !chartRef.value.isConnected || !chartRef.value.offsetParent) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  updateChart()
  chart.on('click', (params) => {
    if (params.data?.bucketId != null) {
      store.setEditBucket(params.data.bucketId)
    }
  })
  ro = new ResizeObserver(() => chart?.resize())
  ro.observe(chartRef.value)
}

const chartOption = computed(() => {
  const buckets = store.buckets
  if (!buckets.length || !store.totalAmount) return null

  const data = buckets.map((b) => {
    const fillRatio = store.bucketFillRatio(b.id)
    const overflow = store.bucketOverflow(b.id)
    const rgb = (b.color || 'rgba(59,130,246,0.3)').replace(/rgba?\(([^)]+).*/, '$1').split(',').slice(0, 3).join(',')
    const alpha = overflow ? 0.2 : Math.max(0.04, 0.08 + fillRatio * 0.27)

    return {
      name: b.name,
      value: b.percentage,
      bucketId: b.id,
      itemStyle: {
        color: overflow ? 'rgba(239,68,68,0.2)' : `rgba(${rgb},${alpha})`,
        borderColor: overflow ? 'rgba(239,68,68,0.5)' : 'rgba(75,85,99,0.6)',
        borderWidth: overflow ? 2 : 1,
      },
      label: {
        formatter: () => {
          const lines = [b.name, `${b.percentage}%`]
          if (showAmounts.value) {
            const used = b.usedAmount || 0
            lines.push(used ? `¥${fmt(used)}` : '¥0')
            if (used) lines.push(`─ ${(fillRatio * 100).toFixed(0)}%`)
          }
          if (overflow) lines.push('⚠️超额')
          return lines.join('\n')
        },
      },
    }
  })

  return {
    tooltip: {
      formatter: (params) => {
        const b = buckets.find(x => x.id === params.data.bucketId)
        if (!b) return ''
        const limit = store.bucketLimit(b.id)
        const lines = [`<strong>${b.name}</strong>`, `比例：${b.percentage}%`]
        if (showAmounts.value) {
          lines.push(`额度：¥${fmt(limit)}`, `已用：¥${fmt(b.usedAmount || 0)}`)
          if (b.usedAmount) lines.push(`已用比例：${(store.bucketFillRatio(b.id) * 100).toFixed(1)}%`)
          if (store.bucketOverflow(b.id)) {
            lines.push(`<span style="color:#f87171">⚠️ 超额 ${(((b.usedAmount||0) / limit - 1) * 100).toFixed(1)}%</span>`)
          }
        }
        return lines.join('<br/>')
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
const showAmounts = ref(true)
function toggleAmounts() {
  showAmounts.value = !showAmounts.value
  updateChart()
}

// ========== 总金额编辑 ==========
const editTotal = ref(false)
const totalInput = ref(0)
function openEditTotal() {
  totalInput.value = store.totalAmount
  editTotal.value = true
}
function saveTotal() {
  store.setTotalAmount(totalInput.value)
  editTotal.value = false
  updateChart()
}

// ========== 新增品种弹窗 ==========
const showBucketForm = ref(false)
const bucketName = ref('')
const bucketPct = ref('')
function openBucketForm() {
  bucketName.value = ''
  bucketPct.value = ''
  showBucketForm.value = true
}
function submitBucket() {
  if (!bucketName.value.trim() || !bucketPct.value) return
  store.addBucket(bucketName.value.trim(), Number(bucketPct.value))
  showBucketForm.value = false
}

// ========== 编辑已用额度弹窗 ==========
const editAmount = ref(0)
function openEditAmount() {
  const b = store.buckets.find(x => x.id === store.editBucketId)
  editAmount.value = b?.usedAmount || 0
}
function saveEditAmount() {
  if (store.editBucketId != null) {
    store.setBucketUsedAmount(store.editBucketId, Number(editAmount.value))
    store.clearEdit()
    updateChart()
  }
}

// ========== 设置比例弹窗 ==========
const pctInput = ref('')
const editingPctId = ref(null)
function openPctEdit(bucket) {
  pctInput.value = String(bucket.percentage)
  editingPctId.value = bucket.id
}
function savePct() {
  if (editingPctId.value != null) {
    store.updateBucketPercentage(editingPctId.value, Number(pctInput.value))
    editingPctId.value = null
    updateChart()
  }
}

function fmt(v) { return Number(v || 0).toFixed(2) }
</script>

<template>
  <div class="flex flex-col gap-4" style="height: calc(100vh - 8rem); min-height: 500px;">
    <!-- 顶栏 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-400">总金额：</span>
        <template v-if="!editTotal">
          <span
            class="text-2xl font-black text-blue-400 cursor-pointer hover:text-blue-300 transition-colors"
            @click="openEditTotal"
          >{{ showAmounts ? '¥' + fmt(store.totalAmount) : '***' }}</span>
          <button
            class="w-6 h-6 flex items-center justify-center rounded-lg bg-gray-700/50 text-gray-400 hover:text-blue-400 hover:bg-gray-700 transition-all text-sm font-bold leading-none"
            @click="openEditTotal"
          >+</button>
          <button
            class="w-6 h-6 flex items-center justify-center rounded-lg transition-all text-sm"
            :class="showAmounts ? 'bg-gray-700/50 text-gray-400 hover:text-amber-400' : 'bg-amber-500/20 text-amber-400'"
            :title="showAmounts ? '隐藏金额' : '显示金额'"
            @click="toggleAmounts"
          >
            <svg v-if="showAmounts" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          </button>
        </template>
        <template v-else>
          <input v-model.number="totalInput" type="number" class="bg-gray-700/50 border border-blue-500 rounded-xl px-3 py-1.5 text-lg font-black text-blue-400 outline-none w-36" @keydown.enter="saveTotal" />
          <button class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-xs font-bold transition-all" @click="saveTotal">确定</button>
          <button class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300 text-xs font-bold transition-all" @click="editTotal = false">取消</button>
        </template>
        <span class="text-xs text-gray-500 ml-2">已用 {{ store.usedPercentage.toFixed(1) }}%</span>
      </div>
      <button class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95" @click="openBucketForm">+ 新增品种</button>
    </div>

    <!-- ECharts Treemap -->
    <div
      ref="chartRef"
      v-if="store.buckets.length && store.totalAmount"
      class="flex-1 bg-gray-800/20 border border-gray-700/30 rounded-2xl overflow-hidden"
      style="min-height: 400px;"
    />

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center bg-gray-800/30 border border-gray-700/30 rounded-2xl text-gray-500" style="min-height: 400px;">
      <svg class="w-16 h-16 mb-4 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
      </svg>
      <p class="text-sm mb-1">先设置总金额，再新增品种</p>
      <p class="text-xs text-gray-600">品种比例之和不超过 100%</p>
    </div>
  </div>

  <!-- 新增品种弹窗 -->
  <div v-if="showBucketForm" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" @click.self="showBucketForm = false">
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
      <div class="p-5 border-b border-gray-700/50"><h3 class="text-base font-black text-gray-100">新增品种</h3></div>
      <div class="p-5 space-y-4">
        <div><label class="text-xs text-gray-400 font-bold mb-1.5 block">品种名称</label><input v-model="bucketName" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：股票、基金" @keydown.enter="submitBucket" /></div>
        <div><label class="text-xs text-gray-400 font-bold mb-1.5 block">比例 (%)</label><input v-model.number="bucketPct" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：30" min="0" max="100" @keydown.enter="submitBucket" /><p class="text-xs text-gray-600 mt-1">剩余可分配：{{ (100 - store.usedPercentage).toFixed(1) }}%</p></div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showBucketForm = false">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" @click="submitBucket">确定</button>
      </div>
    </div>
  </div>

  <!-- 编辑已用额度弹窗 -->
  <div v-if="store.editBucketId != null" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" @click.self="store.clearEdit()">
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn" @click.stop>
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <div>
          <h3 class="text-lg font-black text-gray-100">{{ store.buckets.find(b => b.id === store.editBucketId)?.name }}</h3>
          <p class="text-xs text-gray-500 mt-0.5">
            比例 {{ store.buckets.find(b => b.id === store.editBucketId)?.percentage }}%
            <span class="mx-1.5">|</span>
            额度 ¥{{ fmt(store.bucketLimit(store.editBucketId)) }}
          </p>
        </div>
        <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="store.clearEdit()">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>

      <div class="p-5 space-y-4">
        <div @click.stop>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">已用额度</label>
          <input v-model.number="editAmount" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" @keydown.enter="saveEditAmount" @click.stop />
        </div>
        <div class="flex items-center gap-2 text-sm" @click.stop>
          <div class="flex-1 h-2 rounded-full bg-gray-700/50 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="store.bucketOverflow(store.editBucketId) ? 'bg-red-400' : 'bg-blue-500'"
              :style="{ width: Math.min((editAmount / store.bucketLimit(store.editBucketId)) * 100, 100) + '%' }"
            />
          </div>
          <span class="text-xs font-mono text-gray-400">{{ store.bucketLimit(store.editBucketId) ? ((editAmount / store.bucketLimit(store.editBucketId)) * 100).toFixed(1) : 0 }}%</span>
        </div>
      </div>

      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="store.clearEdit()">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" @click="saveEditAmount">确定</button>
      </div>
    </div>
  </div>

  <!-- 设置比例弹窗 -->
  <div v-if="editingPctId != null" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50" @click.self="editingPctId = null">
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
      <div class="p-5 border-b border-gray-700/50"><h3 class="text-base font-black text-gray-100">设置比例</h3></div>
      <div class="p-5">
        <p class="text-sm text-gray-300 mb-4">品种：{{ store.buckets.find(b => b.id === editingPctId)?.name }}</p>
        <label class="text-xs text-gray-400 font-bold mb-1.5 block">比例 (%)</label>
        <input v-model.number="pctInput" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100" min="0" max="100" @keydown.enter="savePct" />
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="editingPctId = null">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" @click="savePct">确定</button>
      </div>
    </div>
  </div>
</template>
