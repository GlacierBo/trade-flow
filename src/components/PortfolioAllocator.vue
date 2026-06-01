<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useAllocatorStore } from '../stores/allocator'

const store = useAllocatorStore()
onMounted(() => {
  store.init()
  nextTick(calcLayout)
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})

// ========== 热力图布局 ==========
const gridRef = ref(null)
const layout = ref([])

// 简单 squarified treemap 算法
function squarify(items, cx, cy, cw, ch) {
  if (!items.length || cw <= 0 || ch <= 0) return
  const total = items.reduce((s, i) => s + i.pct, 0)
  if (!total) return

  // 按 pct 降序
  const sorted = [...items].sort((a, b) => b.pct - a.pct)
  const rows = []
  let row = []
  let rowSum = 0

  for (const item of sorted) {
    const pct = item.pct / total
    const testRow = [...row, item]
    const testSum = rowSum + pct

    // 评估当前行和加入后的宽高比
    const worstRow = worstAspectRatio(row, rowSum, cw, ch)
    const worstTest = worstAspectRatio(testRow, testSum, cw, ch)

    if (row.length && worstTest > worstRow) {
      rows.push({ items: row, sum: rowSum })
      row = [item]
      rowSum = pct
    } else {
      row.push(item)
      rowSum += pct
    }
  }
  if (row.length) rows.push({ items: row, sum: rowSum })

  // 分配实际位置
  let y = cy
  for (const r of rows) {
    const rh = ch * (r.sum / total)
    let x = cx
    const iw = cw / r.items.length
    for (const item of r.items) {
      item.x = x
      item.y = y
      item.w = iw
      item.h = rh
      x += iw
    }
    y += rh
  }
}

function worstAspectRatio(items, sum, cw, ch) {
  if (!items.length || !sum) return Infinity
  const w = sum > 0 ? cw : cw / items.length
  const h = sum > 0 ? ch * sum : ch / items.length
  const r = w / h
  return Math.max(r, 1 / r)
}

function calcLayout() {
  if (!gridRef.value || !store.buckets.length || !store.totalAmount) {
    layout.value = []
    return
  }
  const rect = gridRef.value.getBoundingClientRect()
  const cw = rect.width - 32  // padding
  const ch = rect.height - 32
  if (cw <= 0 || ch <= 0) return

  const items = store.buckets.map((b) => ({
    id: b.id,
    pct: b.percentage || 0.01,
    x: 0, y: 0, w: 0, h: 0,
  }))

  squarify(items, 0, 0, cw, ch)
  layout.value = items
}

// ========== 拖拽 ==========
const dragPosId = ref(null)
function onDragStart(e, posId) {
  dragPosId.value = posId
  e.dataTransfer.effectAllowed = 'move'
}
function onDragOver(e) {
  e.preventDefault()
  e.dataTransfer.dropEffect = 'move'
}
function onDrop(e, bucketId) {
  e.preventDefault()
  if (dragPosId.value != null) {
    store.dropIntoBucket(dragPosId.value, bucketId)
    dragPosId.value = null
  }
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
  nextTick(calcLayout)
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
  nextTick(calcLayout)
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
    nextTick(calcLayout)
  }
}

// ========== 新增合约弹窗 ==========
const showPosForm = ref(false)
const posCode = ref('')
const posName = ref('')
const posAmount = ref('')
function openPosForm() {
  posCode.value = ''
  posName.value = ''
  posAmount.value = ''
  showPosForm.value = true
}
function submitPos() {
  if (!posCode.value.trim() || !posName.value.trim() || !posAmount.value) return
  store.addPosition(posCode.value.trim(), posName.value.trim(), Number(posAmount.value))
  showPosForm.value = false
}

// ========== 窗口变化重新布局 ==========
let resizeTimer
const onResize = () => {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(calcLayout, 100)
}

// ========== 详情弹窗 ==========
const detailBucket = computed(() =>
  store.detailBucketId != null ? store.buckets.find((b) => b.id === store.detailBucketId) : null
)
const detailContracts = computed(() =>
  store.detailBucketId != null ? store.bucketContracts(store.detailBucketId) : []
)
const detailLimit = computed(() =>
  store.detailBucketId != null ? store.bucketLimit(store.detailBucketId) : 0
)
const detailTotal = computed(() =>
  store.detailBucketId != null ? store.bucketTotal(store.detailBucketId) : 0
)
const detailOverflow = computed(() =>
  store.detailBucketId != null ? store.bucketOverflow(store.detailBucketId) : false
)

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

// 品种变更自动重排
watch(() => store.buckets.map(b => b.percentage + b.positionIds.length).join(','), () => {
  nextTick(calcLayout)
})
</script>

<template>
  <div class="flex gap-5 h-[calc(100vh-6rem)]">
    <!-- 左侧 80% -->
    <div class="flex-[4] flex flex-col gap-4 min-w-0">
      <!-- 总金额 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-400">总金额：</span>
          <template v-if="!editTotal">
            <span
              class="text-2xl font-black text-blue-400 cursor-pointer hover:text-blue-300 transition-colors"
              @click="openEditTotal"
            >
              ¥{{ fmt(store.totalAmount) }}
            </span>
            <button
              class="w-5 h-5 flex items-center justify-center rounded-lg bg-gray-700/50 text-gray-400 hover:text-blue-400 hover:bg-gray-700 transition-all text-sm font-bold leading-none"
              @click="openEditTotal"
            >+</button>
          </template>
          <template v-else>
            <input
              v-model.number="totalInput"
              type="number"
              class="bg-gray-700/50 border border-blue-500 rounded-xl px-3 py-1.5 text-lg font-black text-blue-400 outline-none w-36"
              @keydown.enter="saveTotal"
            />
            <button
              class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white text-xs font-bold transition-all"
              @click="saveTotal"
            >确定</button>
            <button
              class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-300 text-xs font-bold transition-all"
              @click="editTotal = false"
            >取消</button>
          </template>
          <span class="text-xs text-gray-500 ml-2">
            已用 {{ store.usedPercentage.toFixed(1) }}%
          </span>
        </div>
        <button
          class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95"
          @click="openBucketForm"
        >
          + 新增品种
        </button>
      </div>

      <!-- 热力图容器 -->
      <div
        ref="gridRef"
        v-if="store.buckets.length && store.totalAmount"
        class="flex-1 relative bg-gray-800/20 border border-gray-700/30 rounded-2xl overflow-hidden"
      >
        <!-- 每个方块 -->
        <div
          v-for="item in layout"
          :key="item.id"
          class="absolute rounded-xl border transition-all duration-300"
          :class="store.bucketOverflow(item.id) ? 'border-red-400/50' : 'border-gray-600/60'"
          :style="{
            left: item.x + 'px',
            top: item.y + 'px',
            width: item.w + 'px',
            height: item.h + 'px',
          }"
          @dragover="onDragOver"
          @drop="(e) => onDrop(e, item.id)"
          @click="store.setDetailBucket(item.id)"
        >
          <!-- 填充层 -->
          <div
            class="absolute inset-0 rounded-xl transition-all duration-500"
            :class="store.bucketOverflow(item.id) ? 'bg-red-500/15' : 'bg-gradient-to-br from-blue-500/8 to-blue-400/15'"
          />
          <!-- 已分配填充（从底部往上） -->
          <div
            v-if="!store.bucketOverflow(item.id)"
            class="absolute bottom-0 left-0 right-0 rounded-b-xl transition-all duration-500"
            :class="store.bucketTotal(item.id) ? 'bg-blue-500/12' : ''"
            :style="{ height: (store.bucketFillRatio(item.id) * 100) + '%' }"
          />

          <!-- 内容 -->
          <div class="relative z-10 flex flex-col items-center justify-center h-full p-2 text-center">
            <div class="text-sm font-black text-gray-100 truncate max-w-full leading-tight">{{ store.buckets.find(b => b.id === item.id)?.name }}</div>
            <div class="text-xs text-gray-500 font-mono mt-0.5">{{ store.buckets.find(b => b.id === item.id)?.percentage }}%</div>
            <div
              class="text-base font-black font-mono mt-1"
              :class="store.bucketOverflow(item.id) ? 'text-red-400' : (store.bucketTotal(item.id) > 0 ? 'text-green-400' : 'text-gray-500')"
            >
              ¥{{ fmt(store.bucketTotal(item.id)) }}
            </div>

            <!-- 进度条 -->
            <div class="w-3/4 h-1 rounded-full bg-gray-700/50 overflow-hidden mt-1">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="store.bucketOverflow(item.id) ? 'bg-red-400' : 'bg-blue-500'"
                :style="{ width: (store.bucketFillRatio(item.id) * 100) + '%' }"
              />
            </div>
          </div>

          <!-- 操作按钮组 -->
          <div class="absolute top-1 left-1 flex gap-1 opacity-0 hover:opacity-100 transition-opacity">
            <button
              class="w-5 h-5 flex items-center justify-center rounded bg-gray-800/80 text-gray-400 hover:text-blue-400 text-xs font-bold"
              title="设置比例"
              @click.stop="openPctEdit(store.buckets.find(b => b.id === item.id))"
            >%</button>
            <button
              class="w-5 h-5 flex items-center justify-center rounded bg-gray-800/80 text-gray-500 hover:text-red-400"
              title="删除"
              @click.stop="store.removeBucket(item.id); nextTick(calcLayout)"
            >
              <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div
        v-else
        class="flex-1 flex flex-col items-center justify-center bg-gray-800/30 border border-gray-700/30 rounded-2xl text-gray-500"
      >
        <svg class="w-16 h-16 mb-4 opacity-30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
        </svg>
        <p class="text-sm mb-1">先设置总金额，再新增品种</p>
        <p class="text-xs text-gray-600">品种比例之和不超过 100%</p>
      </div>
    </div>

    <!-- 右侧 20% -->
    <div class="flex-1 bg-gray-800/50 border border-gray-700/50 rounded-2xl flex flex-col overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-gray-700/50">
        <h3 class="text-sm font-black text-gray-200">持仓合约</h3>
        <button
          class="w-6 h-6 flex items-center justify-center rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-all text-lg font-bold leading-none"
          @click="openPosForm"
          title="新增合约"
        >+</button>
      </div>

      <div class="flex-1 overflow-y-auto divide-y divide-gray-700/30">
        <div
          v-for="pos in store.unassignedPositions"
          :key="pos.id"
          class="px-4 py-2.5 cursor-grab active:cursor-grabbing hover:bg-gray-700/30 transition-colors border-l-2 border-transparent hover:border-blue-500"
          draggable="true"
          @dragstart="(e) => onDragStart(e, pos.id)"
        >
          <div class="flex items-baseline gap-2">
            <span class="text-sm font-bold text-gray-200 truncate">{{ pos.name }}</span>
            <span class="text-xs text-gray-500 font-mono">{{ pos.code }}</span>
          </div>
          <div class="text-xs text-gray-400 mt-0.5">¥{{ fmt(pos.amount) }}</div>
        </div>

        <div v-for="b in store.buckets" :key="'h-' + b.id">
          <div
            v-for="pos in store.bucketContracts(b.id)"
            :key="'p-' + pos.id"
            class="px-4 py-2 opacity-40 hover:opacity-60 transition-opacity"
            :title="'已分配到: ' + b.name"
          >
            <div class="flex items-baseline gap-2">
              <span class="text-xs font-bold text-gray-400 truncate">{{ pos.name }}</span>
              <span class="text-xs text-gray-600 font-mono">{{ pos.code }}</span>
            </div>
          </div>
        </div>

        <div v-if="!store.positions.length" class="flex flex-col items-center justify-center py-12 text-gray-500">
          <p class="text-xs">暂无合约，点击 + 新增</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 新增品种弹窗 -->
  <div
    v-if="showBucketForm"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="showBucketForm = false"
  >
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

  <!-- 设置比例弹窗 -->
  <div
    v-if="editingPctId != null"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="editingPctId = null"
  >
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

  <!-- 新增合约弹窗 -->
  <div
    v-if="showPosForm"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="showPosForm = false"
  >
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-fadeIn">
      <div class="p-5 border-b border-gray-700/50"><h3 class="text-base font-black text-gray-100">新增合约</h3></div>
      <div class="p-5 space-y-4">
        <div><label class="text-xs text-gray-400 font-bold mb-1.5 block">合约代码</label><input v-model="posCode" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：SH510500" @keydown.enter="submitPos" /></div>
        <div><label class="text-xs text-gray-400 font-bold mb-1.5 block">合约名称</label><input v-model="posName" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：中证500ETF" @keydown.enter="submitPos" /></div>
        <div><label class="text-xs text-gray-400 font-bold mb-1.5 block">持仓金额</label><input v-model.number="posAmount" type="number" class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500" placeholder="如：50000" @keydown.enter="submitPos" /></div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all" @click="showPosForm = false">取消</button>
        <button class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all" @click="submitPos">确定</button>
      </div>
    </div>
  </div>

  <!-- 方块详情弹窗 -->
  <div
    v-if="store.detailBucketId != null"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="store.clearDetail()"
  >
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl animate-fadeIn">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <div>
          <h3 class="text-lg font-black text-gray-100">{{ detailBucket?.name }}</h3>
          <p class="text-xs text-gray-500 mt-0.5">
            比例 {{ detailBucket?.percentage }}%
            <span class="mx-1.5">|</span>
            额度 ¥{{ fmt(detailLimit) }}
            <span class="mx-1.5">|</span>
            已用 ¥{{ fmt(detailTotal) }}
            <span class="mx-1.5">|</span>
            <span :class="detailOverflow ? 'text-red-400' : 'text-green-400'">{{ detailLimit ? (detailTotal/detailLimit*100).toFixed(1) : 0 }}%</span>
            <span v-if="detailOverflow" class="text-red-400 ml-1">⚠️ 超额</span>
          </p>
        </div>
        <button class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors" @click="store.clearDetail()">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div class="divide-y divide-gray-700/30 max-h-72 overflow-y-auto">
        <div v-for="pos in detailContracts" :key="pos.id" class="flex items-center justify-between px-5 py-3">
          <div>
            <span class="text-sm font-bold text-gray-200">{{ pos.name }}</span>
            <span class="text-xs text-gray-500 font-mono ml-2">{{ pos.code }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm font-bold font-mono text-green-400">¥{{ fmt(pos.amount) }}</span>
            <button class="w-6 h-6 flex items-center justify-center rounded-lg text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-all" title="移出" @click="store.removeFromBucket(pos.id, store.detailBucketId)"><svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg></button>
          </div>
        </div>
        <div v-if="!detailContracts.length" class="px-5 py-8 text-center text-gray-500 text-sm">暂无合约</div>
      </div>
      <div class="px-5 py-4 border-t border-gray-700/50 flex items-center justify-between">
        <span class="text-sm text-gray-400">合计</span>
        <span class="text-lg font-black font-mono" :class="detailOverflow ? 'text-red-400' : 'text-green-400'">
          ¥{{ fmt(detailTotal) }}
          <span class="text-sm font-normal text-gray-500">/ ¥{{ fmt(detailLimit) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>
