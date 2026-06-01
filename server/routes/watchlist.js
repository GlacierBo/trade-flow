const express = require("express");
const db = require("../db");
const market = require("../api-client/market");

const router = express.Router();

async function tryUpsert(stock) {
  try {
    if (stock && stock.code && stock.name) await db.upsertStock(stock);
  } catch (err) {
    console.error("upsertStock skipped:", err.message);
  }
}

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

// 添加自选
router.post("/", async (req, res) => {
  try {
    const { code, name } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: "缺少股票代码" });
    }
    let stockName = name;
    try {
      const stock = await market.getStock(code);
      if (stock && stock.name) {
        stockName = stock.name;
        stock.code = code;
        tryUpsert(stock);
      }
    } catch (err) {
      console.error("fetch stock error:", err.message);
    }
    try {
      await db.addWatchlist(code, stockName || code);
    } catch (dbErr) {
      console.error("addWatchlist error:", dbErr.message);
    }
    res.json({ success: true, data: { code, name: stockName || code } });
  } catch (err) {
    console.error("add watchlist error:", err.message);
    res.status(500).json({ success: false, error: err.message });
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

// 刷新自选行情
router.post("/refresh", async (req, res) => {
  try {
    let items = [];
    try {
      items = await db.getWatchlist();
    } catch (err) {
      console.error("getWatchlist error:", err.message);
    }
    const codes = items.map((i) => i.code);
    if (!codes.length) {
      return res.json({ success: true, data: [] });
    }
    let stocks = [];
    try {
      stocks = await market.getStocks(codes);
    } catch (err) {
      console.error("refresh fetch error:", err.message);
    }
    for (const s of stocks) tryUpsert(s);
    let updated = [];
    try {
      updated = await db.getWatchlist();
    } catch (err) {
      console.error("getWatchlist error:", err.message);
    }
    res.json({ success: true, data: updated });
  } catch (err) {
    console.error("refresh error:", err.message);
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
