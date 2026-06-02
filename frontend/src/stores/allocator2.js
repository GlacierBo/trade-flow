import { defineStore } from 'pinia'

const STORAGE_KEY = 'tradeflow-allocator2'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : { positions: [] }
  } catch {
    return { positions: [] }
  }
}

function save(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    positions: state.positions,
  }))
}

let _id = Date.now()
let _colorIdx = 0

const COLORS = [
  'rgba(59,130,246,0.35)',
  'rgba(239,68,68,0.35)',
  'rgba(34,197,94,0.35)',
  'rgba(234,179,8,0.35)',
  'rgba(168,85,247,0.35)',
  'rgba(249,115,22,0.35)',
  'rgba(236,72,153,0.35)',
  'rgba(20,184,166,0.35)',
  'rgba(59,130,246,0.25)',
  'rgba(239,68,68,0.25)',
  'rgba(34,197,94,0.25)',
  'rgba(168,85,247,0.25)',
  'rgba(249,115,22,0.25)',
  'rgba(236,72,153,0.25)',
  'rgba(20,184,166,0.25)',
  'rgba(234,179,8,0.25)',
]

export const useAllocator2Store = defineStore('allocator2', {
  state: () => ({
    positions: [],
    editPositionId: null,
  }),

  getters: {
    totalAmount: (state) => state.positions.reduce((s, p) => s + (p.amount || 0), 0),

    varieties: (state) => [...new Set(state.positions.map(p => p.variety))],
  },

  actions: {
    init() {
      const data = load()
      this.positions = data.positions || []
    },
    _save() { save(this) },

    addPosition(variety, contractCode, contractName, price) {
      this.positions.push({
        id: _id++,
        variety,
        contractCode,
        contractName,
        price: Number(price),
        amount: Number(price),
        color: COLORS[_colorIdx++ % COLORS.length],
      })
      this._save()
    },

    removePosition(id) {
      this.positions = this.positions.filter(p => p.id !== id)
      if (this.editPositionId === id) this.editPositionId = null
      this._save()
    },

    updatePosition(id, data) {
      const p = this.positions.find(x => x.id === id)
      if (p) {
        Object.assign(p, data)
        if (data.price != null) p.amount = Number(data.price)
        this._save()
      }
    },

    setEditPosition(id) { this.editPositionId = id },
    clearEdit() { this.editPositionId = null },
  },
})
