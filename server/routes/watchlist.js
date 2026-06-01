const express = require("express");
const db = require("../db");
const market = require("../api-client/market");

const router = express.Router();

// 获取自选列表（含最新行情）
router.get("/", async (req, res) => {
  try {
    const data = await db.getWatchlist();
    res.json({ success: true, data });
  } catch (err) {
    console.error("getWatchlist error:", err.message);
    res.json({ success: true, data: [] });
  }
});

// 添加自选：查一次行情存入 stocks，再写入 watchlist
router.post("/", async (req, res) => {
  try {
    const { code, name } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: "缺少股票代码" });
    }
    let stockName = name;
    try {
      const stock = await market.getStock(code);
      if (stock?.name) {
        stockName = stock.name;
        stock.code = code;
        await db.insertStock(stock);
      }
    } catch (err) {
      console.error("fetch stock error:", err.message);
    }
    await db.addWatchlist(code, stockName || code).catch((e) =>
      console.error("addWatchlist error:", e.message)
    );
    res.json({ success: true, data: { code, name: stockName || code } });
  } catch (err) {
    console.error("add error:", err.message);
    res.json({ success: true, data: { code: req.body.code, name: req.body.name || req.body.code } });
  }
});

// 删除自选
router.delete("/:code", async (req, res) => {
  try {
    await db.removeWatchlist(req.params.code);
    res.json({ success: true });
  } catch (err) {
    console.error("removeWatchlist error:", err.message);
    res.json({ success: true });
  }
});

// 手动刷新所有自选行情
router.post("/refresh", async (req, res) => {
  try {
    const items = await db.getWatchlistCodes().catch(() => []);
    const codes = items.map((i) => i.code);
    if (!codes.length) {
      return res.json({ success: true, data: [] });
    }
    const stocks = await market.getStocks(codes);
    for (const s of stocks) {
      if (s.code && s.name) {
        await db.insertStock(s);
      }
    }
    const updated = await db.getWatchlist().catch(() => []);
    res.json({ success: true, data: updated });
  } catch (err) {
    console.error("refresh error:", err.message);
    res.json({ success: true, data: [] });
  }
});

// 定时刷新任务（10 分钟一次）
let _timer = null;
function startScheduler() {
  if (_timer) return;
  console.log("[scheduler] 自选行情每 10 分钟自动刷新");
  const tick = async () => {
    try {
      const items = await db.getWatchlistCodes().catch(() => []);
      if (!items.length) return;
      const stocks = await market.getStocks(items.map((i) => i.code));
      for (const s of stocks) {
        if (s.code && s.name) await db.insertStock(s);
      }
      console.log(`[scheduler] ✓ ${stocks.length} 只股票行情已更新`);
    } catch (err) {
      console.error("[scheduler] 刷新失败:", err.message);
    }
  };
  tick(); // 启动立即执行一次
  _timer = setInterval(tick, 10 * 60 * 1000);
}
router.startScheduler = startScheduler;

module.exports = router;
