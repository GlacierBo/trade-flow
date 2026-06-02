import { defineStore } from 'pinia'

const STORAGE_KEY = 'tradeflow-contracts'

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function save(contracts) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(contracts))
}

export const useContractStore = defineStore('contract', {
  state: () => ({
    contracts: [],
  }),

  getters: {
    contractList: (state) => state.contracts,
  },

  actions: {
    init() {
      this.contracts = load()
    },
    _save() { save(this.contracts) },

    addContract(code, name) {
      if (this.contracts.find(c => c.code === code)) return false
      this.contracts.push({ code, name })
      this._save()
      return true
    },

    removeContract(code) {
      this.contracts = this.contracts.filter(c => c.code !== code)
      this._save()
    },

    updateContract(oldCode, code, name) {
      const c = this.contracts.find(x => x.code === oldCode)
      if (c) {
        c.code = code
        c.name = name
        this._save()
        return true
      }
      return false
    },
  },
})
