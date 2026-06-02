// 股票行情 API（通过本地代理服务器，解决跨域）
// 代理服务器转发到东方财富行情接口

const BASE = '/api'

export class StockApiError extends Error {
  constructor(message) {
    super(message)
    this.name = 'StockApiError'
  }
}

async function request(url) {
  const res = await fetch(url)
  const data = await res.json()
  if (!data.success) {
    throw new StockApiError(data.error || '请求失败')
  }
  return data.data
}

// 搜索股票
export async function searchStocks(keyword, source = 'auto') {
  if (!keyword.trim()) return []
  const data = await request(`${BASE}/stocks/search?q=${encodeURIComponent(keyword)}&source=${source}`)
  return data || []
}

// 查询单只股票
export async function getStock(code) {
  return request(`${BASE}/stocks/${encodeURIComponent(code)}`)
}

// 批量查询股票行情
export async function getStocksBatch(codes) {
  if (!codes.length) return []
  const res = await fetch(`${BASE}/stocks/batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ codes }),
  })
  const data = await res.json()
  if (!data.success) {
    throw new StockApiError(data.error || '查询失败')
  }
  return data.data || []
}
