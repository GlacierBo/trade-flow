import { defineStore } from 'pinia'
import { getStocksBatch } from '../api/stock-quote'

const STORAGE_KEY = 'tradeflow-watchlist'
const POLL_INTERVAL = 10 * 60 * 1000

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function save(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export const useWatchlistStore = defineStore('watchlist', {
  state: () => ({
    items: load(),
    loading: false,
    error: '',
    lastRefreshed: null,
    _timer: null,
  }),

  getters: {
    codes: (state) => state.items.map((i) => i.code),
    isWatched: (state) => (code) => state.items.some((i) => i.code === code),
  },

  actions: {
    add(stock) {
      if (this.items.some((i) => i.code === stock.code)) return
      this.items.push({
        code: stock.code,
        name: stock.name,
        basePrice: stock.yesterday || stock.now,
        latestPrice: stock.now,
        lastUpdated: new Date().toISOString(),
        priceHistory: [{ price: stock.now, time: new Date().toISOString() }],
      })
      save(this.items)
      if (!this._timer) this.startPolling()
    },

    remove(code) {
      this.items = this.items.filter((i) => i.code !== code)
      save(this.items)
      if (this.items.length === 0) this.stopPolling()
    },

    async refresh() {
      if (this.items.length === 0) return
      this.loading = true
      this.error = ''
      try {
        const stocks = await getStocksBatch(this.items.map((i) => i.code))
        const now = new Date().toISOString()
        const map = new Map(stocks.map((s) => [s.code, s]))
        for (const item of this.items) {
          const stock = map.get(item.code)
          if (stock) {
            item.latestPrice = stock.now
            item.lastUpdated = now
            item.priceHistory.push({ price: stock.now, time: now })
            if (item.priceHistory.length > 100) {
              item.priceHistory = item.priceHistory.slice(-100)
            }
          }
        }
        this.lastRefreshed = now
        save(this.items)
      } catch (err) {
        this.error = err.message || '刷新失败'
      } finally {
        this.loading = false
      }
    },

    startPolling() {
      this.stopPolling()
      this.refresh()
      this._timer = setInterval(() => this.refresh(), POLL_INTERVAL)
    },

    stopPolling() {
      if (this._timer) {
        clearInterval(this._timer)
        this._timer = null
      }
    },
  },
})
