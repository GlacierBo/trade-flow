const API_BASE = '/api'

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  const data = await response.json()

  if (!data.success) {
    throw new Error(data.error || '请求失败')
  }

  return data.data
}

// ============================================
// 交易 API
// ============================================

// 获取所有交易记录（按买入单号分组）
export async function fetchTrades(userId) {
  try {
    return await request(`/trades?user_id=${userId}`)
  } catch (error) {
    console.error('加载交易记录失败:', error)
    throw new Error('加载交易记录失败')
  }
}

// 创建交易记录
export async function createTrade(data, userId) {
  try {
    const isBuy = data.shares > 0

    const body = {
      contract: data.contract,
      name: data.name,
      price: data.price,
      shares: data.shares,
      fee_rate: data.fee_rate || 0.0002,
      min_fee: data.min_fee || 0.2,
      user_id: userId,
    }

    if (!isBuy) {
      body.buy_order_no = data.buy_order_no
    }

    return await request('/trades', {
      method: 'POST',
      body: JSON.stringify(body),
    })
  } catch (error) {
    console.error('创建交易失败:', error)
    throw new Error(error.message || '保存失败')
  }
}

// 删除交易记录
export async function deleteTrade(id, userId) {
  try {
    return await request(`/trades/${id}?user_id=${userId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('删除交易失败:', error)
    throw new Error(error.message || '删除失败')
  }
}

// ============================================
// 持仓 API
// ============================================

// 获取所有持仓
export async function fetchPositions(userId) {
  try {
    return await request(`/positions?user_id=${userId}`)
  } catch (error) {
    console.error('加载持仓失败:', error)
    throw new Error('加载持仓失败')
  }
}

// 更新持仓最新价格
export async function updatePositionPrice(positionId, price, userId) {
  try {
    return await request(`/positions/${positionId}/price`, {
      method: 'PUT',
      body: JSON.stringify({ price, user_id: userId }),
    })
  } catch (error) {
    console.error('更新价格失败:', error)
    throw new Error('更新价格失败')
  }
}

// 清仓
export async function clearPosition(positionId, userId) {
  try {
    return await request(`/positions/${positionId}?user_id=${userId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('清仓失败:', error)
    throw new Error('清仓失败')
  }
}

// ============================================
// 持仓比例 API
// ============================================

// 获取所有持仓比例项目
export async function fetchPortfolioItems(userId) {
  try {
    return await request(`/portfolio?user_id=${userId}`)
  } catch (error) {
    console.error('加载持仓项目失败:', error)
    throw new Error('加载持仓项目失败')
  }
}

// 创建持仓比例项目
export async function createPortfolioItem(data, userId) {
  try {
    return await request('/portfolio', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        contract: data.contract,
        tag: data.tag || '',
        price: parseFloat(data.price),
        user_id: userId,
      }),
    })
  } catch (error) {
    console.error('创建持仓项目失败:', error)
    throw new Error(error.message || '保存失败')
  }
}

// 删除持仓比例项目
export async function deletePortfolioItem(id, userId) {
  try {
    return await request(`/portfolio/${id}?user_id=${userId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('删除持仓项目失败:', error)
    throw new Error(error.message || '删除失败')
  }
}

// ============================================
// 交易标签 API
// ============================================

// 获取所有交易标签
export async function fetchTradeTags(userId) {
  try {
    return await request(`/trade-tags?user_id=${userId}`)
  } catch (error) {
    console.error('加载交易标签失败:', error)
    throw new Error('加载交易标签失败')
  }
}

// 删除交易标签
export async function deleteTradeTag(tagId, userId) {
  try {
    return await request(`/trade-tags/${tagId}?user_id=${userId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('删除标签失败:', error)
    throw new Error('删除标签失败')
  }
}

// 创建或更新交易标签
export async function upsertTradeTag(contract, name, userId) {
  try {
    return await request('/trade-tags', {
      method: 'POST',
      body: JSON.stringify({
        contract,
        name,
        user_id: userId,
      }),
    })
  } catch (error) {
    console.error('更新标签失败:', error)
    return { status: 'error', message: error.message }
  }
}

// ============================================
// 合约 API
// ============================================

// 获取合约列表
export async function fetchContracts(userId) {
  try {
    return await request(`/contracts?user_id=${userId}`)
  } catch (error) {
    console.error('加载合约列表失败:', error)
    throw new Error('加载合约列表失败')
  }
}

// 新增合约
export async function createContract(code, name, userId) {
  try {
    return await request('/contracts', {
      method: 'POST',
      body: JSON.stringify({ code, name, user_id: userId }),
    })
  } catch (error) {
    console.error('新增合约失败:', error)
    throw new Error(error.message || '新增失败')
  }
}

// 更新合约
export async function updateContract(oldCode, code, name, userId) {
  try {
    return await request(`/contracts/${oldCode}`, {
      method: 'PUT',
      body: JSON.stringify({ code, name, user_id: userId }),
    })
  } catch (error) {
    console.error('更新合约失败:', error)
    throw new Error(error.message || '更新失败')
  }
}

// 删除合约
export async function deleteContract(code, userId) {
  try {
    return await request(`/contracts/${code}?user_id=${userId}`, {
      method: 'DELETE',
    })
  } catch (error) {
    console.error('删除合约失败:', error)
    throw new Error(error.message || '删除失败')
  }
}

// ============================================
// 用户认证 API
// ============================================

export async function verifyLogin(username, password) {
  try {
    return await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  } catch (error) {
    console.error('登录验证失败:', error)
    throw new Error('登录验证失败')
  }
}

export async function registerUser(username) {
  try {
    return await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username }),
    })
  } catch (error) {
    console.error('注册失败:', error)
    throw new Error(error.message || '注册失败')
  }
}

export async function changePassword(userId, oldPassword, newPassword) {
  try {
    return await request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        old_password: oldPassword,
        new_password: newPassword,
      }),
    })
  } catch (error) {
    console.error('修改密码失败:', error)
    throw new Error(error.message || '修改密码失败')
  }
}

export async function resetUserPassword(userId) {
  try {
    return await request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
    })
  } catch (error) {
    console.error('重置密码失败:', error)
    throw new Error(error.message || '重置密码失败')
  }
}

export async function fetchUsers(page = 1, pageSize = 20) {
  try {
    return await request(`/auth/users?page=${page}&page_size=${pageSize}`)
  } catch (error) {
    console.error('获取用户列表失败:', error)
    throw new Error('获取用户列表失败')
  }
}
