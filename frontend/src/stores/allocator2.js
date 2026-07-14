import { defineStore } from 'pinia'
import {
  fetchAllocatorPositions,
  createAllocatorPosition,
  updateAllocatorPosition,
  deleteAllocatorPosition,
} from '../api/stock'

const LOCALSTORAGE_KEY = 'tradeflow-allocator2'

function loadLegacyData() {
  try {
    const raw = localStorage.getItem(LOCALSTORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    return data.positions || null
  } catch {
    return null
  }
}

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

let _colorIdx = 0

function nextColor() {
  const c = COLORS[_colorIdx % COLORS.length]
  _colorIdx++
  return c
}

export const useAllocator2Store = defineStore('allocator2', {
  state: () => ({
    positions: [],
    editPositionId: null,
    loading: false,
    loaded: false,
  }),

  getters: {
    totalAmount: (state) => state.positions.reduce((s, p) => s + (p.amount || 0), 0),
    varieties: (state) => [...new Set(state.positions.map(p => p.variety))],
  },

  actions: {
    async init(userId) {
      if (this.loaded) return

      // 先尝试从 localStorage 迁移旧数据
      const legacy = loadLegacyData()
      if (legacy && legacy.length > 0) {
        try {
          for (const pos of legacy) {
            await createAllocatorPosition({
              variety: pos.variety || '',
              contract_code: pos.contractCode || '',
              contract_name: pos.contractName || '',
              price: pos.price || 0,
              amount: pos.amount || 0,
              color: pos.color || nextColor(),
            }, userId)
          }
          // 全部迁移成功后才清除 localStorage
          localStorage.removeItem(LOCALSTORAGE_KEY)
          console.log('[allocator2] 已从 localStorage 迁移', legacy.length, '条数据')
        } catch (e) {
          console.warn('[allocator2] 迁移失败，localStorage 数据已保留，下次可重试', e)
        }
      }

      await this.fetchPositions(userId)
      this.loaded = true
    },

    async fetchPositions(userId) {
      this.loading = true
      try {
        const raw = await fetchAllocatorPositions(userId)
        // API 返回 snake_case，统一映射为前端 camelCase
        this.positions = (raw || []).map(p => ({
          id: p.id,
          variety: p.variety || '',
          contractCode: p.contract_code || p.contractCode || '',
          contractName: p.contract_name || p.contractName || '',
          price: Number(p.price || 0),
          amount: Number(p.amount || 0),
          color: p.color || '',
          user_id: p.user_id,
          created_at: p.created_at,
        }))
        // 恢复颜色索引
        _colorIdx = this.positions.length
      } catch (e) {
        console.warn('[allocator2] 加载失败', e)
      } finally {
        this.loading = false
      }
    },

    async addPosition(variety, contractCode, contractName, price, userId) {
      const pos = await createAllocatorPosition({
        variety,
        contract_code: contractCode,
        contract_name: contractName,
        price: Number(price),
        amount: Number(price),
        color: nextColor(),
      }, userId)
      // API 返回 snake_case，转 camelCase 存入 store
      this.positions.push({
        id: pos.id,
        variety: pos.variety || variety,
        contractCode: pos.contract_code || contractCode,
        contractName: pos.contract_name || contractName,
        price: Number(pos.price || price),
        amount: Number(pos.amount || price),
        color: pos.color || '',
        user_id: pos.user_id,
        created_at: pos.created_at,
      })
    },

    async removePosition(id, userId) {
      await deleteAllocatorPosition(id, userId)
      this.positions = this.positions.filter(p => p.id !== id)
      if (this.editPositionId === id) this.editPositionId = null
    },

    async updatePosition(id, data, userId) {
      // 将前端字段名映射到后端字段名
      const body = {}
      if (data.variety !== undefined) body.variety = data.variety
      if (data.contractCode !== undefined) body.contract_code = data.contractCode
      if (data.contractName !== undefined) body.contract_name = data.contractName
      if (data.price !== undefined) {
        body.price = Number(data.price)
        body.amount = Number(data.price)
      }
      if (data.amount !== undefined) body.amount = Number(data.amount)
      if (data.color !== undefined) body.color = data.color

      const updated = await updateAllocatorPosition(id, body, userId)
      const idx = this.positions.findIndex(p => p.id === id)
      if (idx !== -1) {
        // API 返回 snake_case，映射回 camelCase
        this.positions[idx] = {
          ...this.positions[idx],
          variety: updated.variety ?? this.positions[idx].variety,
          contractCode: updated.contract_code ?? this.positions[idx].contractCode,
          contractName: updated.contract_name ?? this.positions[idx].contractName,
          price: Number(updated.price ?? this.positions[idx].price),
          amount: Number(updated.amount ?? this.positions[idx].amount),
          color: updated.color ?? this.positions[idx].color,
        }
      }
    },

    async replaceAllPositions(positions, userId) {
      // 先创建新数据，全部成功后再删除旧的（防止中途失败丢失数据）
      const created = []
      try {
        for (const pos of positions) {
          const c = await createAllocatorPosition({
            variety: pos.variety || '',
            contract_code: pos.contractCode || pos.contract_code || '',
            contract_name: pos.contractName || pos.contract_name || '',
            price: Number(pos.price || 0),
            amount: Number(pos.amount || 0),
            color: pos.color || nextColor(),
          }, userId)
          created.push({
            id: c.id,
            variety: c.variety || pos.variety || '',
            contractCode: c.contract_code || pos.contractCode || pos.contract_code || '',
            contractName: c.contract_name || pos.contractName || pos.contract_name || '',
            price: Number(c.price || pos.price || 0),
            amount: Number(c.amount || pos.amount || 0),
            color: c.color || pos.color || '',
            user_id: c.user_id,
            created_at: c.created_at,
          })
        }
      } catch (e) {
        // 创建失败，已有的 store 数据不变
        throw e
      }

      // 全部创建成功，再删除旧的
      for (const p of this.positions) {
        await deleteAllocatorPosition(p.id, userId).catch(() => {})
      }
      this.positions = created
    },

    setEditPosition(id) { this.editPositionId = id },
    clearEdit() { this.editPositionId = null },
  },
})
