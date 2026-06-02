import { defineStore } from 'pinia'

const API_BASE = '/api/watchlist'
const POLL_INTERVAL = 10 * 60 * 1000

export const useWatchlistStore = defineStore('watchlist', {
  state: () => ({
    items: [],
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
    async fetchWatchlist() {
      this.loading = true
      this.error = ''
      const res = await fetch(API_BASE)
      if (!res.ok) throw new Error('服务未连接')
      const data = await res.json()
      if (!data.success) throw new Error(data.error || '获取自选失败')
      this.items = data.data || []
      this.lastRefreshed = new Date().toISOString()
      this.loading = false
    },

    async add(code, name) {
      this.loading = true
      try {
        const res = await fetch(API_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, name }),
        })
        const data = await res.json()
        if (!data.success) throw new Error(data.error || '添加失败')
        // 重新获取列表以获取最新数据
        await this.fetchWatchlist()
      } catch (err) {
        this.error = err.message || '添加失败'
      } finally {
        this.loading = false
      }
    },

    async remove(code) {
      this.loading = true
      try {
        const res = await fetch(`${API_BASE}/${code}`, { method: 'DELETE' })
        const data = await res.json()
        if (!data.success) throw new Error(data.error || '删除失败')
        this.items = this.items.filter((i) => i.code !== code)
        if (this.items.length === 0) this.stopPolling()
      } catch (err) {
        this.error = err.message || '删除失败'
      } finally {
        this.loading = false
      }
    },

    async refresh() {
      if (this.items.length === 0) return
      try {
        await this.fetchWatchlist()
      } catch (err) {
        this.error = err.message || '刷新失败'
      }
    },

    startPolling() {
      this.stopPolling()
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
