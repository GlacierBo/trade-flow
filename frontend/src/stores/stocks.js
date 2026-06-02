import { defineStore } from 'pinia'
import { searchStocks, getStock } from '../api/stock-quote'

export const useStocksStore = defineStore('stocks', {
  state: () => ({
    results: [],
    selected: null,
    loading: false,
    error: '',
    lastKeyword: '',
    source: 'auto', // auto | sina | eastmoney
  }),

  actions: {
    setSource(source) {
      this.source = source
    },

    async search(keyword) {
      if (!keyword.trim()) return
      this.loading = true
      this.error = ''
      this.lastKeyword = keyword
      try {
        this.results = await searchStocks(keyword, this.source)
      } catch (err) {
        this.error = err.message || '搜索失败'
        this.results = []
      } finally {
        this.loading = false
      }
    },

    async fetchStock(code) {
      this.loading = true
      this.error = ''
      try {
        this.selected = await getStock(code)
      } catch (err) {
        this.error = err.message || '查询失败'
        this.selected = null
      } finally {
        this.loading = false
      }
    },

    clearResults() {
      this.results = []
      this.lastKeyword = ''
    },

    clearError() {
      this.error = ''
    },
  },
})
