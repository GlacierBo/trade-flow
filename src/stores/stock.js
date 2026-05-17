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
    userId: null,
    userRole: '',

    // Admin
    users: [],
    usersTotal: 0,
    usersPage: 1,

    // Password change modal
    passwordModalVisible: false,

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
    toasts: [],

    // Tab
    activeTab: 'trade',

    // Portfolio
    portfolioItems: [],
    portfolioModalVisible: false,
    portfolioPresetData: null
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
    async login(username, password) {
      try {
        const result = await api.verifyLogin(username, password)
        if (!result) {
          this.showToast('用户名或密码错误', 'error')
          return false
        }
        this.isAuthenticated = true
        this.username = result.username
        this.userId = result.id
        this.userRole = result.role
        localStorage.setItem('auth_token', 'db_token')
        localStorage.setItem('username', result.username)
        localStorage.setItem('user_role', result.role)
        localStorage.setItem('user_id', String(result.id))
        return true
      } catch (e) {
        this.showToast(e.message, 'error')
        return false
      }
    },

    async register(username) {
      try {
        const result = await api.registerUser(username)
        if (result.error) {
          this.showToast(result.error, 'error')
          return null
        }
        return result.password
      } catch (e) {
        this.showToast(e.message, 'error')
        return null
      }
    },

    async changePassword(oldPassword, newPassword) {
      if (!this.userId) return false
      try {
        const ok = await api.changePassword(this.userId, oldPassword, newPassword)
        if (ok) {
          this.showToast('密码修改成功', 'success')
          this.passwordModalVisible = false
        } else {
          this.showToast('原密码错误', 'error')
        }
        return ok
      } catch (e) {
        this.showToast(e.message, 'error')
        return false
      }
    },

    logout() {
      this.isAuthenticated = false
      this.username = ''
      this.userId = null
      this.userRole = ''
      this.activeTab = 'trade'
      localStorage.removeItem('auth_token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_role')
      localStorage.removeItem('user_id')
    },

    checkAuth() {
      const token = localStorage.getItem('auth_token')
      const username = localStorage.getItem('username')
      const role = localStorage.getItem('user_role')
      const uid = localStorage.getItem('user_id')
      if (token && username) {
        this.isAuthenticated = true
        this.username = username
        this.userRole = role || ''
        this.userId = uid ? parseInt(uid) : null
      }
    },

    // Admin actions
    async loadUsers(page = 1) {
      try {
        this.usersPage = page
        const result = await api.fetchUsers(page, 20)
        this.users = result.users || []
        this.usersTotal = result.total || 0
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    async resetUserPassword(userId) {
      try {
        const newPassword = await api.resetUserPassword(userId)
        this.showToast(`密码已重置为: ${newPassword}`, 'success')
        return newPassword
      } catch (e) {
        this.showToast(e.message, 'error')
        return null
      }
    },

    openPasswordModal() {
      this.passwordModalVisible = true
    },

    closePasswordModal() {
      this.passwordModalVisible = false
    },

    get isAdmin() {
      return this.userRole === 'admin'
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

    // Tab actions
    setActiveTab(tab) {
      this.activeTab = tab
    },

    // Portfolio actions
    async loadPortfolioItems() {
      try {
        this.portfolioItems = await api.fetchPortfolioItems()
      } catch (e) {
        console.error('加载持仓项目失败:', e)
      }
    },

    async createPortfolioItem(form) {
      const { name, contract, tag, price } = form
      try {
        const item = await api.createPortfolioItem({ name, contract, tag, price })
        this.showToast('保存成功', 'success')
        this.closePortfolioModal()
        await this.loadPortfolioItems()
        return item
      } catch (e) {
        this.showToast(e.message, 'error')
        throw e
      }
    },

    async deletePortfolioItem(id) {
      try {
        await api.deletePortfolioItem(id)
        this.showToast('已删除', 'success')
        await this.loadPortfolioItems()
      } catch (e) {
        this.showToast(e.message, 'error')
      }
    },

    handlePortfolioTagClick(item) {
      this.portfolioPresetData = {
        name: item.name,
        contract: item.contract,
        tag: item.tag || ''
      }
      this.openPortfolioModal()
    },

    openPortfolioModal() {
      this.portfolioModalVisible = true
    },

    closePortfolioModal() {
      this.portfolioModalVisible = false
      this.portfolioPresetData = null
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
