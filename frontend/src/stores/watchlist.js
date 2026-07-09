import { defineStore } from 'pinia'
import { request } from '../api/http'

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
      try {
        this.items = (await request('/watchlist')) || []
        this.lastRefreshed = new Date().toISOString()
      } catch (err) {
        this.error = err.message || '获取自选失败'
      } finally {
        this.loading = false
      }
    },

    async add(code, name) {
      this.loading = true
      try {
        await request('/watchlist', {
          method: 'POST',
          body: JSON.stringify({ code, name }),
        })
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
        await request(`/watchlist/${code}`, { method: 'DELETE' })
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
