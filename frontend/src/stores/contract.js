import { defineStore } from 'pinia'
import * as api from '../api/stock'

export const useContractStore = defineStore('contract', {
  state: () => ({
    contracts: [],
    loading: false,
    error: '',
  }),

  getters: {
    contractList: (state) => state.contracts,
  },

  actions: {
    async fetchContracts(userId) {
      this.loading = true
      this.error = ''
      try {
        this.contracts = await api.fetchContracts(userId)
      } catch (err) {
        this.error = err.message || '加载合约失败'
      } finally {
        this.loading = false
      }
    },

    async addContract(code, name, userId) {
      this.loading = true
      this.error = ''
      try {
        const contract = await api.createContract(code, name, userId)
        this.contracts.unshift(contract)
        return true
      } catch (err) {
        this.error = err.message || '新增失败'
        return false
      } finally {
        this.loading = false
      }
    },

    async updateContract(oldCode, code, name, userId) {
      this.loading = true
      this.error = ''
      try {
        const updated = await api.updateContract(oldCode, code, name, userId)
        const idx = this.contracts.findIndex(c => c.code === oldCode)
        if (idx !== -1) this.contracts.splice(idx, 1, updated)
        return true
      } catch (err) {
        this.error = err.message || '更新失败'
        return false
      } finally {
        this.loading = false
      }
    },

    async removeContract(code, userId) {
      this.loading = true
      this.error = ''
      try {
        await api.deleteContract(code, userId)
        this.contracts = this.contracts.filter(c => c.code !== code)
      } catch (err) {
        this.error = err.message || '删除失败'
      } finally {
        this.loading = false
      }
    },
  },
})
