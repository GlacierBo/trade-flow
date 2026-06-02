import { defineStore } from 'pinia'

const STORAGE_KEY = 'tradeflow-allocator'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { totalAmount: 0, buckets: [] }
  } catch {
    return { totalAmount: 0, buckets: [] }
  }
}

function save(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    totalAmount: state.totalAmount,
    buckets: state.buckets,
  }))
}

let _id = Date.now()
let _colorIdx = 0

const COLORS = [
  'rgba(59,130,246,0.35)',  // 蓝
  'rgba(239,68,68,0.35)',   // 红
  'rgba(34,197,94,0.35)',   // 绿
  'rgba(234,179,8,0.35)',   // 黄
  'rgba(168,85,247,0.35)',  // 紫
  'rgba(249,115,22,0.35)',  // 橙
  'rgba(236,72,153,0.35)',  // 粉
  'rgba(20,184,166,0.35)',  // 青
  'rgba(59,130,246,0.25)',
  'rgba(239,68,68,0.25)',
  'rgba(34,197,94,0.25)',
  'rgba(168,85,247,0.25)',
  'rgba(249,115,22,0.25)',
  'rgba(236,72,153,0.25)',
  'rgba(20,184,166,0.25)',
  'rgba(234,179,8,0.25)',
]

export const useAllocatorStore = defineStore('allocator', {
  state: () => ({
    totalAmount: 0,
    buckets: [],
    editBucketId: null,
  }),

  getters: {
    bucketLimit: (state) => (bucketId) => {
      const b = state.buckets.find((x) => x.id === bucketId)
      return b ? state.totalAmount * b.percentage / 100 : 0
    },
    bucketFillRatio: (state) => (bucketId) => {
      const b = state.buckets.find((x) => x.id === bucketId)
      if (!b) return 0
      const limit = state.totalAmount * b.percentage / 100
      return limit ? Math.min((b.usedAmount || 0) / limit, 1) : 0
    },
    bucketOverflow: (state) => (bucketId) => {
      const b = state.buckets.find((x) => x.id === bucketId)
      if (!b) return false
      const limit = state.totalAmount * b.percentage / 100
      return limit ? (b.usedAmount || 0) > limit : false
    },
    usedPercentage: (state) => state.buckets.reduce((s, b) => s + b.percentage, 0),
  },

  actions: {
    init() {
      const data = load()
      this.totalAmount = data.totalAmount || 0
      this.buckets = data.buckets || []
    },
    _save() { save(this) },

    setTotalAmount(v) {
      this.totalAmount = Number(v)
      this._save()
    },

    addBucket(name, percentage) {
      this.buckets.push({
        id: _id++,
        name,
        percentage: Number(percentage),
        usedAmount: 0,
        color: COLORS[_colorIdx++ % COLORS.length],
      })
      this._save()
    },

    removeBucket(id) {
      this.buckets = this.buckets.filter((b) => b.id !== id)
      if (this.editBucketId === id) this.editBucketId = null
      this._save()
    },

    updateBucketPercentage(id, percentage) {
      const b = this.buckets.find((x) => x.id === id)
      if (b) { b.percentage = Number(percentage); this._save() }
    },

    setBucketUsedAmount(id, amount) {
      const b = this.buckets.find((x) => x.id === id)
      if (b) { b.usedAmount = Number(amount); this._save() }
    },

    setEditBucket(id) { this.editBucketId = id },
    clearEdit() { this.editBucketId = null },
  },
})
