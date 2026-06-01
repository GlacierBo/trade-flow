<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAllocatorStore } from '../stores/allocator'

const store = useAllocatorStore()

onMounted(() => store.init())

// ========== 拖拽状态 ==========
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

// ========== 新增弹窗 ==========
const showBucketForm = ref(false)
const bucketName = ref('')
const bucketAmount = ref('')

function openBucketForm() {
  bucketName.value = ''
  bucketAmount.value = ''
  showBucketForm.value = true
}

function submitBucket() {
  if (!bucketName.value.trim() || !bucketAmount.value) return
  store.addBucket(bucketName.value.trim(), Number(bucketAmount.value))
  showBucketForm.value = false
}

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

// ========== 比例计算 ==========
const gridStyle = computed(() => {
  const n = store.buckets.length
  if (!n) return {}
  // 计算每行放几个：用平方根估算
  const cols = Math.max(1, Math.ceil(Math.sqrt(n)))
  const total = store.totalTarget || 1
  return {
    gridTemplateColumns: `repeat(${cols}, 1fr)`,
    gridAutoRows: '1fr',
  }
})

function bucketWeight(bucket) {
  return store.totalTarget > 0 ? bucket.targetAmount / store.totalTarget : 0
}

// 计算每个方块的 grid span
function bucketSpan(bucket) {
  const w = bucketWeight(bucket)
  // 至少占 1 格，按比例分配
  const cols = Math.max(1, Math.ceil(Math.sqrt(store.buckets.length)))
  const span = Math.max(1, Math.round(w * cols))
  return Math.min(span, cols)
}

// ========== 方块详情弹窗 ==========
const detailBucketId = ref(null)
const detailBucket = computed(() =>
  detailBucketId.value != null ? store.bucketById(detailBucketId.value) : null
)
const detailContracts = computed(() =>
  detailBucketId.value != null ? store.bucketContracts(detailBucketId.value) : []
)
const detailTotal = computed(() =>
  detailBucketId.value != null ? store.bucketTotal(detailBucketId.value) : 0
)

function openDetail(bucketId) {
  detailBucketId.value = bucketId
}

function fmt(v) {
  return Number(v || 0).toFixed(2)
}
</script>

<template>
  <div class="flex gap-5 h-[calc(100vh-6rem)]">
    <!-- 左侧 80%：比例方块 -->
    <div class="flex-[4] flex flex-col gap-4 min-w-0">
      <!-- 总金额 + 新增 -->
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-400">
          总目标金额：
          <span class="text-lg font-black text-blue-400">¥{{ fmt(store.totalTarget) }}</span>
          <span class="text-gray-600 mx-2">|</span>
          已分配：
          <span class="text-lg font-black text-green-400">¥{{ fmt(store.totalAllocated) }}</span>
        </div>
        <button
          class="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-95"
          @click="openBucketForm"
        >
          + 新增品种
        </button>
      </div>

      <!-- 方块网格 -->
      <div
        v-if="store.buckets.length"
        class="flex-1 grid gap-3 p-4 bg-gray-800/30 border border-gray-700/30 rounded-2xl"
        :style="gridStyle"
      >
        <div
          v-for="bucket in store.buckets"
          :key="bucket.id"
          class="relative bg-gray-800/70 border-2 border-gray-600/50 rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 group"
          :style="{
            gridColumn: `span ${bucketSpan(bucket)}`,
          }"
          @dragover="onDragOver"
          @drop="(e) => onDrop(e, bucket.id)"
          @click="openDetail(bucket.id)"
        >
          <!-- 比例指示条 -->
          <div
            class="absolute bottom-0 left-0 h-1 rounded-full transition-all duration-500"
            :class="bucketWeight(bucket) > 0.5 ? 'bg-blue-500' : bucketWeight(bucket) > 0.2 ? 'bg-cyan-500' : 'bg-blue-400/60'"
            :style="{ width: (bucketWeight(bucket) * 100) + '%' }"
          />

          <div class="text-center px-2">
            <div class="text-base font-black text-gray-100 truncate max-w-full">{{ bucket.name }}</div>
            <div class="text-xs text-gray-500 mt-0.5">目标 ¥{{ fmt(bucket.targetAmount) }}</div>
            <div class="text-lg font-black font-mono mt-1" :class="store.bucketTotal(bucket.id) > 0 ? 'text-green-400' : 'text-gray-500'">
              ¥{{ fmt(store.bucketTotal(bucket.id)) }}
            </div>
            <div class="text-xs text-gray-500 mt-0.5">
              {{ (bucketWeight(bucket) * 100).toFixed(1) }}%
            </div>
          </div>

          <!-- 拖入提示 -->
          <div class="absolute inset-0 border-2 border-dashed border-blue-400/0 rounded-2xl transition-all hover:border-blue-400/30 pointer-events-none" />

          <!-- 删除按钮 -->
          <button
            class="absolute top-1.5 right-1.5 w-6 h-6 flex items-center justify-center rounded-lg text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-all opacity-0 group-hover:opacity-100"
            title="删除品种"
            @click.stop="store.removeBucket(bucket.id)"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
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
        <p class="text-sm">点击右上角「新增品种」创建分配方块</p>
        <p class="text-xs text-gray-600 mt-2">然后从右侧拖拽合约到方块中</p>
      </div>
    </div>

    <!-- 右侧 20%：持仓列表 -->
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
        <!-- 未分配的持仓 -->
        <div
          v-for="pos in store.unassignedPositions"
          :key="pos.id"
          class="px-4 py-2.5 cursor-grab active:cursor-grabbing hover:bg-gray-700/30 transition-colors"
          draggable="true"
          @dragstart="(e) => onDragStart(e, pos.id)"
        >
          <div class="flex items-baseline gap-2">
            <span class="text-sm font-bold text-gray-200 truncate">{{ pos.name }}</span>
            <span class="text-xs text-gray-500 font-mono">{{ pos.code }}</span>
          </div>
          <div class="text-xs text-gray-400 mt-0.5">
            ¥{{ fmt(pos.amount) }}
          </div>
        </div>

        <!-- 已分配到桶里的持仓（灰色小字显示） -->
        <div
          v-for="b in store.buckets"
          :key="'h-' + b.id"
        >
          <div
            v-for="pos in store.bucketContracts(b.id)"
            :key="'p-' + pos.id"
            class="px-4 py-2 opacity-50"
            :title="'已分配到: ' + b.name"
          >
            <div class="flex items-baseline gap-2">
              <span class="text-xs font-bold text-gray-400 truncate">{{ pos.name }}</span>
              <span class="text-xs text-gray-600 font-mono">{{ pos.code }}</span>
            </div>
          </div>
        </div>

        <!-- 空 -->
        <div
          v-if="!store.positions.length"
          class="flex flex-col items-center justify-center py-12 text-gray-500"
        >
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
      <div class="p-5 border-b border-gray-700/50">
        <h3 class="text-base font-black text-gray-100">新增品种</h3>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">品种名称</label>
          <input
            v-model="bucketName"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500"
            placeholder="如：股票、基金、债券"
            @keydown.enter="submitBucket"
          />
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">目标金额</label>
          <input
            v-model.number="bucketAmount"
            type="number"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500"
            placeholder="如：100000"
            @keydown.enter="submitBucket"
          />
        </div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button
          class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all"
          @click="showBucketForm = false"
        >取消</button>
        <button
          class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all"
          @click="submitBucket"
        >确定</button>
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
      <div class="p-5 border-b border-gray-700/50">
        <h3 class="text-base font-black text-gray-100">新增合约</h3>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约代码</label>
          <input
            v-model="posCode"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500"
            placeholder="如：SH510500"
            @keydown.enter="submitPos"
          />
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">合约名称</label>
          <input
            v-model="posName"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500"
            placeholder="如：中证500ETF"
            @keydown.enter="submitPos"
          />
        </div>
        <div>
          <label class="text-xs text-gray-400 font-bold mb-1.5 block">持仓金额</label>
          <input
            v-model.number="posAmount"
            type="number"
            class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-3 py-2.5 text-sm outline-none focus:border-blue-500 text-gray-100 placeholder-gray-500"
            placeholder="如：50000"
            @keydown.enter="submitPos"
          />
        </div>
      </div>
      <div class="flex gap-3 px-5 pb-5">
        <button
          class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all"
          @click="showPosForm = false"
        >取消</button>
        <button
          class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all"
          @click="submitPos"
        >确定</button>
      </div>
    </div>
  </div>

  <!-- 方块详情弹窗 -->
  <div
    v-if="detailBucketId != null"
    class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
    @click.self="detailBucketId = null"
  >
    <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl animate-fadeIn">
      <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
        <div>
          <h3 class="text-lg font-black text-gray-100">{{ detailBucket?.name }}</h3>
          <p class="text-xs text-gray-500 mt-0.5">
            目标 ¥{{ fmt(detailBucket?.targetAmount) }}
            <span class="mx-1.5">|</span>
            已分配 ¥{{ fmt(detailTotal) }}
            <span class="mx-1.5">|</span>
            {{ detailBucket ? (bucketWeight(detailBucket) * 100).toFixed(1) : 0 }}%
          </p>
        </div>
        <button
          class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors"
          @click="detailBucketId = null"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <div class="divide-y divide-gray-700/30 max-h-72 overflow-y-auto">
        <div
          v-for="pos in detailContracts"
          :key="pos.id"
          class="flex items-center justify-between px-5 py-3"
        >
          <div>
            <span class="text-sm font-bold text-gray-200">{{ pos.name }}</span>
            <span class="text-xs text-gray-500 font-mono ml-2">{{ pos.code }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm font-bold font-mono text-green-400">¥{{ fmt(pos.amount) }}</span>
            <button
              class="w-6 h-6 flex items-center justify-center rounded-lg text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-all"
              title="移出"
              @click="store.removeFromBucket(pos.id, detailBucketId)"
            >
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>
        <div v-if="!detailContracts.length" class="px-5 py-8 text-center text-gray-500 text-sm">
          暂无合约，从右侧拖拽合约到方块中
        </div>
      </div>

      <div class="px-5 py-4 border-t border-gray-700/50 flex justify-end">
        <span class="text-sm text-gray-400">
          合计：
          <span class="text-lg font-black font-mono text-green-400">¥{{ fmt(detailTotal) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>
