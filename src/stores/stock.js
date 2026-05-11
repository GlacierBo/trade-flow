import { defineStore } from 'pinia'
import * as api from '../api/stock'

export const useStockStore = defineStore('stock', {
  state: () => ({
    trades: [],
    positions: [],
    tags: [],
    searchQuery: '',

    // Auth
    isAuthenticated: false,
    username: '',

    // Trade modal
    tradeModalVisible: false,
    tradeType: 'buy',
    tradePresetData: null, // 预填充数据（从标签点击传入）

    // Sell modal
    sellModalVisible: false,
    sellTarget: null,

    // Confirm modal
    confirmModalVisible: false,
    confirmMessage: '',
    confirmCallback: null,

    // Price modal
    priceModalVisible: false,
    priceTarget: null,
    priceValue: '',

    // Toasts
    toasts: []
  }),

  getters: {
    filteredTrades: (state) => {
      if (!state.searchQuery) return state.trades
      const q = state.searchQuery.toLowerCase()
      return state.trades.filter(t =>
        t.contract.toLowerCase().includes(q) ||
        t.name.toLowerCase().includes(q) ||
        t.buy_order_no.toLowerCase().includes(q)
      )
    }
  },

  actions: {
    // Auth actions
    login(username, password) {
      // 简单的用户名密码验证（实际项目中应该使用后端 API）
      if (username === 'admin' && password === 'admin') {
        this.isAuthenticated = true
        this.username = username
        // 保存到 localStorage
        localStorage.setItem('auth_token', 'admin_token')
        localStorage.setItem('username', username)
        return true
      }
      return false
    },

    logout() {
      this.isAuthenticated = false
      this.username = ''
      localStorage.removeItem('auth_token')
      localStorage.removeItem('username')
    },

    checkAuth() {
      const token = localStorage.getItem('auth_token')
      const username = localStorage.getItem('username')
      if (token && username) {
        this.isAuthenticated = true
        this.username = username
      }
    },

    async loadData() {
      await Promise.all([this.loadTrades(), this.loadPositions(), this.loadTags()])
    },

    async loadTrades() {
      try {
        this.trades = await api.fetchTrades()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    async loadPositions() {
      try {
        this.positions = await api.fetchPositions()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    async loadTags() {
      try {
        this.tags = await api.fetchTradeTags()
      } catch (e) {
        console.error('加载标签失败:', e)
        // 标签加载失败不影响主流程
      }
    },

    async createTrade(form) {
      const { contract, name, price, shares, feeRate, minFee } = form
      try {
        const data = {
          contract,
          name,
          price: parseFloat(price),
          shares: this.tradeType === 'buy' ? parseInt(shares) : -parseInt(shares),
          fee_rate: parseFloat(feeRate) / 100,
          min_fee: minFee || 0.2
        }
        const result = await api.createTrade(data)
        
        // 只在买入时更新标签
        if (this.tradeType === 'buy' && contract && name) {
          await api.upsertTradeTag(contract, name)
          await this.loadTags()
        }
        
        this.showToast('交易成功', 'success')
        this.closeTradeModal()
        await this.loadData()
        return result
      } catch (e) {
        this.showToast(e.message, 'error')
        throw e
      }
    },

    async sellFromBuy(form) {
      const { price, shares, feeRate, minFee, buyOrderNo } = form
      try {
        const data = {
          contract: '',
          name: '',
          price: parseFloat(price),
          shares: -parseInt(shares),
          fee_rate: parseFloat(feeRate) / 100 || 0.0002,
          min_fee: minFee || 0.2,
          buy_order_no: buyOrderNo
        }
        const result = await api.createTrade(data)
        this.showToast('卖出成功', 'success')
        this.closeSellModal()
        await this.loadData()
        return result
      } catch (e) {
        this.showToast(e.message, 'error')
        throw e
      }
    },

    async deleteTrade(id) {
      try {
        await api.deleteTrade(id)
        this.showToast('删除成功', 'success')
        await this.loadData()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    async deleteTag(tagId) {
      try {
        await api.deleteTradeTag(tagId)
        this.showToast('标签已删除', 'success')
        await this.loadTags()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    handleTagClick(tag) {
      // 设置预填充数据（只填充合约代码和名称，不填充价格）
      this.tradePresetData = {
        contract: tag.contract,
        name: tag.name
      }
      this.openTradeModal()
    },

    async updatePrice(positionId, price) {
      try {
        await api.updatePositionPrice(positionId, parseFloat(price))
        this.showToast('价格更新成功', 'success')
        this.closePriceModal()
        await this.loadPositions()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    async clearPosition(positionId) {
      try {
        await api.clearPosition(positionId)
        this.showToast('清仓成功', 'success')
        await this.loadData()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    // Modal controls
    openTradeModal() {
      this.tradeType = 'buy'
      this.tradeModalVisible = true
    },

    closeTradeModal() {
      this.tradeModalVisible = false
      this.tradePresetData = null
    },

    setTradeType(type) {
      this.tradeType = type
    },

    openSellModal(buyOrderNo, buyPrice, remainingShares) {
      this.sellTarget = { buyOrderNo, buyPrice, remainingShares }
      this.sellModalVisible = true
    },

    closeSellModal() {
      this.sellModalVisible = false
      this.sellTarget = null
    },

    showConfirm(message, callback) {
      this.confirmMessage = message
      this.confirmCallback = callback
      this.confirmModalVisible = true
    },

    closeConfirm() {
      this.confirmModalVisible = false
      this.confirmCallback = null
    },

    executeConfirm() {
      if (this.confirmCallback) {
        this.confirmCallback()
        this.closeConfirm()
      }
    },

    openPriceModal(positionId, currentPrice) {
      this.priceTarget = { id: positionId, currentPrice }
      this.priceValue = String(currentPrice)
      this.priceModalVisible = true
    },

    closePriceModal() {
      this.priceModalVisible = false
      this.priceTarget = null
    },

    showToast(msg, type = 'success') {
      const id = Date.now()
      this.toasts.push({ id, msg, type })
      setTimeout(() => {
        this.toasts = this.toasts.filter(t => t.id !== id)
      }, 2500)
    }
  }
})
