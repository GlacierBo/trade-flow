import { defineStore } from 'pinia'

const STORAGE_KEY = 'tradeflow-allocator'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { totalAmount: 0, buckets: [], positions: [] }
  } catch {
    return { totalAmount: 0, buckets: [], positions: [] }
  }
}

function save(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    totalAmount: state.totalAmount,
    buckets: state.buckets,
    positions: state.positions,
  }))
}

let _id = Date.now()

// 预定义一组深色背景可用的颜色
const COLORS = [
  'rgba(59,130,246,0.25)',   // 蓝
  'rgba(239,68,68,0.25)',    // 红
  'rgba(34,197,94,0.25)',    // 绿
  'rgba(234,179,8,0.25)',    // 黄
  'rgba(168,85,247,0.25)',   // 紫
  'rgba(249,115,22,0.25)',   // 橙
  'rgba(236,72,153,0.25)',   // 粉
  'rgba(20,184,166,0.25)',   // 青
  'rgba(239,68,68,0.18)',
  'rgba(59,130,246,0.18)',
  'rgba(34,197,94,0.18)',
  'rgba(168,85,247,0.18)',
  'rgba(249,115,22,0.18)',
  'rgba(236,72,153,0.18)',
  'rgba(20,184,166,0.18)',
  'rgba(234,179,8,0.18)',
]
let _colorIdx = 0

export const useAllocatorStore = defineStore('allocator', {
  state: () => ({
    totalAmount: 0,
    buckets: [],
    positions: [],
    editingBucket: null,
    detailBucketId: null,
  }),

  getters: {
    // 每个桶的额度上限
    bucketLimit: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      return bucket ? state.totalAmount * bucket.percentage / 100 : 0
    },

    // 每个桶当前已分配总额
    bucketTotal: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return 0
      return state.positions
        .filter((p) => bucket.positionIds.includes(p.id))
        .reduce((s, p) => s + p.amount, 0)
    },

    // 每个桶的已用比例 (actual / limit)
    bucketFillRatio: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return 0
      const limit = state.totalAmount * bucket.percentage / 100
      if (!limit) return 0
      const total = state.positions
        .filter((p) => bucket.positionIds.includes(p.id))
        .reduce((s, p) => s + p.amount, 0)
      return Math.min(total / limit, 1)
    },

    // 是否超额
    bucketOverflow: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return false
      const limit = state.totalAmount * bucket.percentage / 100
      if (!limit) return false
      const total = state.positions
        .filter((p) => bucket.positionIds.includes(p.id))
        .reduce((s, p) => s + p.amount, 0)
      return total > limit
    },

    bucketContracts: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return []
      return state.positions.filter((p) => bucket.positionIds.includes(p.id))
    },

    // 不在任何桶里的仓位
    unassignedPositions: (state) => {
      const assigned = new Set()
      for (const b of state.buckets) {
        for (const pid of b.positionIds) assigned.add(pid)
      }
      return state.positions.filter((p) => !assigned.has(p.id))
    },

    usedPercentage: (state) => {
      return state.buckets.reduce((s, b) => s + b.percentage, 0)
    },
  },

  actions: {
    init() {
      const data = load()
      // 首次使用时填充示例数据
      if (!data.buckets || !data.buckets.length) {
        const sampleBuckets = [
          { id: _id++, name: '半导体', percentage: 25, positionIds: [], color: 'rgba(59,130,246,0.3)' },
          { id: _id++, name: '新能源', percentage: 20, positionIds: [], color: 'rgba(34,197,94,0.3)' },
          { id: _id++, name: '消费', percentage: 18, positionIds: [], color: 'rgba(249,115,22,0.3)' },
          { id: _id++, name: '医药', percentage: 15, positionIds: [], color: 'rgba(236,72,153,0.3)' },
          { id: _id++, name: '金融', percentage: 12, positionIds: [], color: 'rgba(234,179,8,0.25)' },
          { id: _id++, name: '军工', percentage: 10, positionIds: [], color: 'rgba(168,85,247,0.25)' },
        ]
        this.totalAmount = 100000
        this.buckets = sampleBuckets
        this.positions = []
        save(this)
        return
      }
      this.totalAmount = data.totalAmount || 0
      this.buckets = data.buckets || []
      this.positions = data.positions || []
    },

    _save() {
      save(this)
    },

    setTotalAmount(v) {
      this.totalAmount = Number(v)
      this._save()
    },

    addBucket(name, percentage) {
      this.buckets.push({
        id: _id++,
        name,
        percentage: Number(percentage),
        positionIds: [],
        color: COLORS[_colorIdx++ % COLORS.length],
      })
      this._save()
    },

    removeBucket(id) {
      this.buckets = this.buckets.filter((b) => b.id !== id)
      if (this.editingBucket === id) this.editingBucket = null
      this._save()
    },

    updateBucketPercentage(id, percentage) {
      const bucket = this.buckets.find((b) => b.id === id)
      if (!bucket) return
      bucket.percentage = Number(percentage)
      this._save()
    },

    addPosition(code, name, amount) {
      this.positions.push({
        id: _id++,
        code,
        name,
        amount: Number(amount),
      })
      this._save()
    },

    removePosition(id) {
      this.positions = this.positions.filter((p) => p.id !== id)
      for (const b of this.buckets) {
        b.positionIds = b.positionIds.filter((pid) => pid !== id)
      }
      this._save()
    },

    dropIntoBucket(positionId, bucketId) {
      const bucket = this.buckets.find((b) => b.id === bucketId)
      if (!bucket) return
      for (const b of this.buckets) {
        b.positionIds = b.positionIds.filter((pid) => pid !== positionId)
      }
      bucket.positionIds.push(positionId)
      this._save()
    },

    removeFromBucket(positionId, bucketId) {
      const bucket = this.buckets.find((b) => b.id === bucketId)
      if (!bucket) return
      bucket.positionIds = bucket.positionIds.filter((pid) => pid !== positionId)
      this._save()
    },

    setEditingBucket(id) {
      this.editingBucket = id
    },
    clearEditing() {
      this.editingBucket = null
    },
    setDetailBucket(id) {
      this.detailBucketId = id
    },
    clearDetail() {
      this.detailBucketId = null
    },
  },
})
