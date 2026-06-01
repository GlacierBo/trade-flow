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
