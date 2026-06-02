<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStockStore } from '../../stores/stock'

const store = useStockStore()
const showPrices = ref(true)

onMounted(() => {
  if (store.portfolioItems.length === 0) {
    store.loadPortfolioItems()
  }
})

const quickItems = computed(() => {
  const seen = new Set()
  return store.portfolioItems.filter(item => {
    const key = `${item.contract}|${item.name}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})

const grandTotal = computed(() => {
  return store.portfolioItems.reduce((sum, i) => sum + parseFloat(i.price), 0)
})

const groupedByTag = computed(() => {
  const groups = {}
  store.portfolioItems.forEach(item => {
    const tag = item.tag || '未分类'
    if (!groups[tag]) {
      groups[tag] = { items: [], subtotal: 0 }
    }
    groups[tag].items.push(item)
    groups[tag].subtotal += parseFloat(item.price)
  })
  return Object.entries(groups)
    .sort(([, a], [, b]) => b.subtotal - a.subtotal)
    .map(([tag, data]) => ({ tag, ...data }))
})

function onDeleteItem(id, name) {
  store.showConfirm(`确定要删除"${name}"吗？`, () => {
    store.deletePortfolioItem(id)
  })
}

function pctOfTotal(price) {
  return grandTotal.value > 0 ? (parseFloat(price) / grandTotal.value) * 100 : 0
}

function barColor(pct) {
  if (pct >= 80) return 'bg-red-500/15'
  if (pct < 30) return 'bg-blue-500/15'
  return 'bg-gray-500/10'
}
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
    <!-- 左侧：快捷列表 -->
    <div class="lg:col-span-2">
      <div class="bg-gray-800/50 rounded-2xl p-4 border border-gray-700/50">
        <h2 class="text-lg font-black text-blue-400 mb-3">合约</h2>

        <div v-if="quickItems.length === 0" class="text-center py-6 text-gray-500 text-sm">
          暂无项目<br>
          <span class="text-xs">添加后会自动显示</span>
        </div>

        <div v-else class="space-y-1.5 max-h-[600px] overflow-y-auto scrollbar-thin">
          <div
            v-for="item in quickItems"
            :key="`${item.contract}-${item.name}`"
            class="group bg-gray-700/30 hover:bg-gray-700/50 border border-gray-600/30 rounded-lg px-2.5 py-2 cursor-pointer transition-all active:scale-95 relative flex items-center justify-between"
            @click="store.handlePortfolioTagClick(item)"
          >
            <div class="flex-1 min-w-0">
              <div class="font-bold text-gray-100 text-xs truncate">
                {{ item.name }}
              </div>
              <div class="text-xs text-gray-400 mt-0.5">{{ item.contract }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：比例计算 -->
    <div class="lg:col-span-10">
      <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden">
        <!-- 头部 -->
        <div class="p-4 border-b border-gray-700/50">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <h2 class="text-lg font-black text-blue-400">持仓比例</h2>
              <button
                @click="showPrices = !showPrices"
                class="text-gray-500 hover:text-gray-300 transition-all active:scale-95 p-1"
                :title="showPrices ? '隐藏金额' : '显示金额'"
              >
                <!-- 眼睛开 -->
                <svg v-if="showPrices" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
                  <path d="M3 12s2-7 9-7 9 7 9 7-2 7-9 7-9-7-9-7z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
                <!-- 眼睛关 -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="w-5 h-5">
                  <path d="M3 12s2-7 9-7 9 7 9 7-2 7-9 7-9-7-9-7z" />
                  <circle cx="12" cy="12" r="3" />
                  <line x1="4" y1="4" x2="20" y2="20" />
                </svg>
              </button>
            </div>
            <button
              @click="store.openPortfolioModal()"
              class="bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 text-white px-5 py-2.5 rounded-xl font-black shadow-lg shadow-blue-500/30 transition-all active:scale-95 text-sm"
            >
              + 新增
            </button>
          </div>
        </div>

        <!-- 列表内容 -->
        <div class="p-4 space-y-4">
          <!-- 空状态 -->
          <div v-if="store.portfolioItems.length === 0" class="text-center py-12 text-gray-500 text-sm">
            暂无持仓数据，点击右上角"新增"添加
          </div>

          <template v-else>
            <!-- 总计（置顶） -->
            <div class="bg-blue-500/10 rounded-xl border border-blue-500/30 px-4 py-3 flex items-center justify-between">
              <span class="font-black text-gray-100">总计</span>
              <div class="flex items-center gap-4 text-sm">
                <span class="text-gray-200 font-bold w-28 text-right">
                  {{ showPrices ? '¥' + grandTotal.toFixed(2) : '****' }}
                </span>
                <span class="text-blue-400 font-black w-16 text-right">100%</span>
              </div>
            </div>

            <!-- 按 Tag 分组 -->
            <div
              v-for="group in groupedByTag"
              :key="group.tag"
              class="bg-gray-700/20 rounded-xl border border-gray-600/30 overflow-hidden"
            >
              <!-- Tag 头部 -->
              <div class="bg-gray-700/40 px-4 py-2.5 flex items-center justify-between">
                <span class="font-black text-gray-100 text-sm">{{ group.tag }}</span>
                <div class="flex items-center gap-4 text-sm">
                  <span class="text-gray-300 font-bold w-28 text-right">
                    {{ showPrices ? '¥' + group.subtotal.toFixed(2) : '****' }}
                  </span>
                  <span class="text-blue-400 font-black w-16 text-right">
                    {{ grandTotal > 0 ? ((group.subtotal / grandTotal) * 100).toFixed(2) : 0 }}%
                  </span>
                </div>
              </div>

              <!-- Tag 内项目列表 -->
              <div class="divide-y divide-gray-700/30">
                <div
                  v-for="item in group.items"
                  :key="item.id"
                  class="relative overflow-hidden"
                >
                  <!-- 进度条底色 -->
                  <div
                    class="absolute left-0 top-0 bottom-0 transition-all"
                    :class="barColor(pctOfTotal(item.price))"
                    :style="{ width: pctOfTotal(item.price) + '%' }"
                  />

                  <!-- 内容 -->
                  <div class="relative z-10 flex items-center justify-between px-4 py-2.5 hover:bg-gray-700/10 transition-colors group/item">
                    <div class="flex items-center gap-3 min-w-0">
                      <button
                        @click="onDeleteItem(item.id, item.name)"
                        class="opacity-0 group-hover/item:opacity-100 text-gray-400 hover:text-red-400 transition-opacity text-base leading-none flex-shrink-0"
                        title="删除"
                      >×</button>
                      <div class="min-w-0">
                        <span class="text-gray-100 text-sm font-bold">{{ item.name }}</span>
                        <span class="text-gray-500 text-xs ml-2">{{ item.contract }}</span>
                      </div>
                    </div>
                    <div class="flex items-center gap-4 text-sm flex-shrink-0">
                      <!-- 价格 -->
                      <span class="text-gray-200 font-bold w-28 text-right">
                        {{ showPrices ? '¥' + parseFloat(item.price).toFixed(2) : '****' }}
                      </span>
                      <!-- 占总计百分比 -->
                      <span class="text-blue-400 font-black w-16 text-right">
                        {{ pctOfTotal(item.price).toFixed(2) }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
