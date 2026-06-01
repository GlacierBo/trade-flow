const express = require("express");
const db = require("../db");
const eastmoney = require("../lib/eastmoney");

const router = express.Router();

// 获取自选列表（含最新行情）
router.get("/", async (req, res) => {
  try {
    const data = await db.getWatchlist();
    res.json({ success: true, data });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 添加自选
router.post("/", async (req, res) => {
  try {
    const { code, name } = req.body;
    if (!code) {
      return res.status(400).json({ success: false, error: "缺少股票代码" });
    }
    // 先查行情存到 stocks 表
    const stock = await eastmoney.getStock(code);
    if (stock && stock.name) {
      await db.upsertStock(stock);
    }
    await db.addWatchlist(code, name || stock?.name || code);
    res.json({ success: true, data: { code, name: name || stock?.name || code } });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 删除自选
router.delete("/:code", async (req, res) => {
  try {
    await db.removeWatchlist(req.params.code);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// 刷新自选行情
router.post("/refresh", async (req, res) => {
  try {
    const items = await db.getWatchlist();
    const codes = items.map((i) => i.code);
    if (!codes.length) {
      return res.json({ success: true, data: [] });
    }
    const stocks = await eastmoney.getStocks(codes);
    for (const s of stocks) {
      await db.upsertStock(s);
    }
    const updated = await db.getWatchlist();
    res.json({ success: true, data: updated });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
