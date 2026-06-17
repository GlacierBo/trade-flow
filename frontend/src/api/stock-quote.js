// 股票行情 API（通过本地代理服务器，解决跨域）
// 代理服务器转发到东方财富行情接口

import { request, ApiError as StockApiError } from './http.js'

export { StockApiError }

// 搜索股票
export async function searchStocks(keyword, source = 'auto') {
  if (!keyword.trim()) return []
  const data = await request(`/stocks/search?q=${encodeURIComponent(keyword)}&source=${source}`)
  return data || []
}

// 查询单只股票
export async function getStock(code) {
  return request(`/stocks/${encodeURIComponent(code)}`)
}

// 批量查询股票行情
export async function getStocksBatch(codes) {
  if (!codes.length) return []
  return request('/stocks/batch', {
    method: 'POST',
    body: JSON.stringify({ codes }),
  })
}
