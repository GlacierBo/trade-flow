import { defineStore } from 'pinia'

const STORAGE_KEY = 'tradeflow-allocator'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { buckets: [], positions: [] }
  } catch {
    return { buckets: [], positions: [] }
  }
}

function save(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    buckets: state.buckets,
    positions: state.positions,
  }))
}

let _id = Date.now()

export const useAllocatorStore = defineStore('allocator', {
  state: () => ({
    buckets: [],
    positions: [],
    selectedBucket: null,
  }),

  getters: {
    totalTarget: (state) => state.buckets.reduce((s, b) => s + b.targetAmount, 0),
    totalAllocated: (state) => state.positions.reduce((s, p) => s + p.amount, 0),

    bucketById: (state) => (id) => state.buckets.find((b) => b.id === id),

    bucketContracts: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return []
      return state.positions.filter((p) => bucket.positionIds.includes(p.id))
    },

    bucketTotal: (state) => (bucketId) => {
      const bucket = state.buckets.find((b) => b.id === bucketId)
      if (!bucket) return 0
      return state.positions
        .filter((p) => bucket.positionIds.includes(p.id))
        .reduce((s, p) => s + p.amount, 0)
    },

    // 不在任何桶里的仓位
    unassignedPositions: (state) => {
      const assigned = new Set()
      for (const b of state.buckets) {
        for (const pid of b.positionIds) assigned.add(pid)
      }
      return state.positions.filter((p) => !assigned.has(p.id))
    },
  },

  actions: {
    init() {
      const data = load()
      this.buckets = data.buckets || []
      this.positions = data.positions || []
    },

    _save() {
      save(this)
    },

    addBucket(name, targetAmount) {
      this.buckets.push({
        id: _id++,
        name,
        targetAmount: Number(targetAmount),
        positionIds: [],
      })
      this._save()
    },

    removeBucket(id) {
      this.buckets = this.buckets.filter((b) => b.id !== id)
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
      // 同时从所有桶中移除
      for (const b of this.buckets) {
        b.positionIds = b.positionIds.filter((pid) => pid !== id)
      }
      this._save()
    },

    dropIntoBucket(positionId, bucketId) {
      const bucket = this.buckets.find((b) => b.id === bucketId)
      if (!bucket) return
      // 先从其他桶移除
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

    selectBucket(id) {
      this.selectedBucket = id
    },

    clearSelection() {
      this.selectedBucket = null
    },
  },
})
