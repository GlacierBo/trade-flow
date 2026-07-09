/**
 * 共享 HTTP 请求工具
 * 统一 API 请求的错误处理和响应解析
 */

const API_BASE = '/api'

export class ApiError extends Error {
  constructor(message) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * 发送 API 请求
 * @param {string} url - API 路径（如 /trades）或完整 URL
 * @param {object} options - fetch 选项
 * @returns {Promise<any>} 响应数据中的 data 字段
 */
export async function request(url, options = {}) {
  const fullUrl = url.startsWith('http') || url.startsWith('/api')
    ? url
    : `${API_BASE}${url}`

  const response = await fetch(fullUrl, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  const data = await response.json()

  if (!data.success) {
    throw new ApiError(data.error || '请求失败')
  }

  return data.data
}
