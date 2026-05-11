import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase 配置缺失，请检查 .env 文件')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 获取所有交易记录（按买入单号分组）
export async function fetchTrades() {
  try {
    // 获取所有买入记录
    const { data: buyTrades, error: buyError } = await supabase
      .from('stock_trades')
      .select('*')
      .eq('trade_type', 'buy')
      .order('created_at', { ascending: false })

    if (buyError) throw buyError

    // 为每个买入记录查询关联的卖出记录
    const tradesWithSells = await Promise.all(
      buyTrades.map(async (buy) => {
        const { data: sells, error: sellError } = await supabase
          .from('stock_trades')
          .select('*')
          .eq('buy_order_no', buy.buy_order_no)
          .eq('trade_type', 'sell')
          .order('created_at', { ascending: true })

        if (sellError) throw sellError

        return {
          ...buy,
          sells: sells || []
        }
      })
    )

    return tradesWithSells
  } catch (error) {
    console.error('加载交易记录失败:', error)
    throw new Error('加载交易记录失败')
  }
}

// 创建交易记录
export async function createTrade(data) {
  try {
    const isBuy = data.shares > 0
    
    if (isBuy) {
      // 买入操作：生成买入单号
      const tradeDate = new Date().toISOString().split('T')[0]
      
      // 调用 PostgreSQL 函数生成买入单号
      const { data: orderNo, error: orderError } = await supabase.rpc(
        'generate_buy_order_no',
        { p_trade_date: tradeDate }
      )

      if (orderError) throw orderError

      // 计算金额和手续费
      const amount = data.price * Math.abs(data.shares)
      const fee = Math.max(Math.abs(amount) * data.fee_rate, data.min_fee || 0.2)
      const netAmount = amount + fee

      // 插入交易记录
      const { data: trade, error: insertError } = await supabase
        .from('stock_trades')
        .insert([{
          buy_order_no: orderNo,
          contract: data.contract,
          name: data.name,
          price: data.price,
          shares: data.shares,
          remaining_shares: data.shares,
          amount: amount,
          fee: fee,
          net_amount: netAmount,
          trade_type: 'buy',
          trade_date: tradeDate,
          realized_profit: 0,
          single_profit: 0
        }])
        .select()
        .single()

      if (insertError) throw insertError

      return { status: 'success', trade_id: trade.id }
    } else {
      // 卖出操作：必须提供 buy_order_no
      if (!data.buy_order_no) {
        throw new Error('卖出操作必须提供买入单号')
      }

      // 查询对应的买入记录
      const { data: buyRecord, error: buyError } = await supabase
        .from('stock_trades')
        .select('*')
        .eq('buy_order_no', data.buy_order_no)
        .eq('trade_type', 'buy')
        .single()

      if (buyError || !buyRecord) {
        throw new Error('找不到对应的买入记录')
      }

      const sellShares = Math.abs(data.shares)
      
      // 验证卖出数量
      if (sellShares > buyRecord.remaining_shares) {
        throw new Error(`卖出数量不能超过剩余可卖数量 (${buyRecord.remaining_shares})`)
      }

      // 计算单笔收益
      const amount = data.price * sellShares
      const fee = Math.max(Math.abs(amount) * (data.fee_rate || 0.0002), data.min_fee || 0.2)
      const singleProfit = (data.price - buyRecord.price) * sellShares - fee

      const tradeDate = new Date().toISOString().split('T')[0]

      // 插入卖出记录
      const { data: trade, error: insertError } = await supabase
        .from('stock_trades')
        .insert([{
          buy_order_no: data.buy_order_no,
          contract: buyRecord.contract,
          name: buyRecord.name,
          price: data.price,
          shares: -sellShares,
          remaining_shares: 0,
          amount: -amount,
          fee: fee,
          net_amount: -(amount + fee),
          trade_type: 'sell',
          trade_date: tradeDate,
          realized_profit: 0,
          single_profit: singleProfit
        }])
        .select()
        .single()

      if (insertError) throw insertError

      // 更新买入记录的 remaining_shares 和 realized_profit
      const { error: updateError } = await supabase
        .from('stock_trades')
        .update({
          remaining_shares: buyRecord.remaining_shares - sellShares,
          realized_profit: buyRecord.realized_profit + singleProfit
        })
        .eq('id', buyRecord.id)

      if (updateError) throw updateError

      return { status: 'success', trade_id: trade.id }
    }
  } catch (error) {
    console.error('创建交易失败:', error)
    throw new Error(error.message || '保存失败')
  }
}

// 删除交易记录
export async function deleteTrade(id) {
  try {
    // 先查询交易记录
    const { data: trade, error: fetchError } = await supabase
      .from('stock_trades')
      .select('*')
      .eq('id', id)
      .single()

    if (fetchError || !trade) {
      throw new Error('交易记录不存在')
    }

    if (trade.trade_type === 'buy') {
      // 检查是否有卖出记录
      const { data: sells, error: sellError } = await supabase
        .from('stock_trades')
        .select('id')
        .eq('buy_order_no', trade.buy_order_no)
        .eq('trade_type', 'sell')

      if (sellError) throw sellError

      if (sells && sells.length > 0) {
        throw new Error(`该买入记录已有 ${sells.length} 笔卖出，不能删除。请先删除所有关联的卖出记录。`)
      }

      // 删除买入记录（触发器会自动重算持仓）
      const { error: deleteError } = await supabase
        .from('stock_trades')
        .delete()
        .eq('id', id)

      if (deleteError) throw deleteError
    } else {
      // 删除卖出记录
      // 先恢复买入记录
      const { data: buyRecord, error: buyError } = await supabase
        .from('stock_trades')
        .select('*')
        .eq('buy_order_no', trade.buy_order_no)
        .eq('trade_type', 'buy')
        .single()

      if (buyError || !buyRecord) {
        throw new Error('找不到对应的买入记录')
      }

      const sellShares = Math.abs(trade.shares)

      // 恢复买入记录的 remaining_shares 和 realized_profit
      const { error: updateError } = await supabase
        .from('stock_trades')
        .update({
          remaining_shares: buyRecord.remaining_shares + sellShares,
          realized_profit: buyRecord.realized_profit - trade.single_profit
        })
        .eq('id', buyRecord.id)

      if (updateError) throw updateError

      // 删除卖出记录（触发器会自动重算持仓）
      const { error: deleteError } = await supabase
        .from('stock_trades')
        .delete()
        .eq('id', id)

      if (deleteError) throw deleteError
    }

    return { status: 'success' }
  } catch (error) {
    console.error('删除交易失败:', error)
    throw new Error(error.message || '删除失败')
  }
}

// 获取所有持仓
export async function fetchPositions() {
  try {
    const { data, error } = await supabase
      .from('stock_positions')
      .select('*')
      .gt('total_shares', 0)
      .order('updated_at', { ascending: false })

    if (error) throw error

    return data || []
  } catch (error) {
    console.error('加载持仓失败:', error)
    throw new Error('加载持仓失败')
  }
}

// 更新持仓最新价格
export async function updatePositionPrice(positionId, price) {
  try {
    // 先获取持仓信息
    const { data: position, error: fetchError } = await supabase
      .from('stock_positions')
      .select('*')
      .eq('id', positionId)
      .single()

    if (fetchError || !position) {
      throw new Error('持仓不存在')
    }

    // 更新价格、市值、盈亏
    const marketValue = position.total_shares * price
    const unrealizedProfit = (price - position.avg_cost) * position.total_shares
    const profitRate = position.avg_cost > 0 
      ? (unrealizedProfit / (position.avg_cost * position.total_shares) * 100)
      : 0

    const { error: updateError } = await supabase
      .from('stock_positions')
      .update({
        latest_price: price,
        market_value: marketValue,
        profit_rate: profitRate,
        updated_at: new Date().toISOString()
      })
      .eq('id', positionId)

    if (updateError) throw updateError

    return { status: 'success' }
  } catch (error) {
    console.error('更新价格失败:', error)
    throw new Error('更新价格失败')
  }
}

// 清仓
export async function clearPosition(positionId) {
  try {
    // 获取持仓信息
    const { data: position, error: fetchError } = await supabase
      .from('stock_positions')
      .select('*')
      .eq('id', positionId)
      .single()

    if (fetchError || !position) {
      throw new Error('持仓不存在')
    }

    // 删除该合约的所有交易记录
    const { error: deleteError } = await supabase
      .from('stock_trades')
      .delete()
      .eq('contract', position.contract)

    if (deleteError) throw deleteError

    // 触发器会自动删除持仓记录（因为持仓为零）
    return { status: 'success' }
  } catch (error) {
    console.error('清仓失败:', error)
    throw new Error('清仓失败')
  }
}
