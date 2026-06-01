const express = require("express");
const db = require("../db");
const eastmoney = require("../lib/eastmoney");

const router = express.Router();

// 搜索股票
router.get("/search", async (req, res, next) => {
  try {
    const { q } = req.query;
    if (!q || typeof q !== "string") {
      return res.status(400).json({ success: false, error: "Missing q" });
    }
    const stocks = await eastmoney.searchStocks(q);
    for (const s of stocks) {
      if (s.code && s.name) await db.upsertStock(s);
    }
    res.json({ success: true, data: stocks });
  } catch (err) {
    next(err);
  }
});

// 查询单只股票
router.get("/:code", async (req, res, next) => {
  try {
    const { code } = req.params;
    const stock = await eastmoney.getStock(code);
    if (stock && stock.name) {
      stock.code = code;
      await db.upsertStock(stock);
    }
    res.json({ success: true, data: stock });
  } catch (err) {
    next(err);
  }
});

// 批量查询
router.post("/batch", async (req, res, next) => {
  try {
    const { codes } = req.body;
    if (!Array.isArray(codes) || !codes.length) {
      return res.status(400).json({ success: false, error: "Missing codes" });
    }
    const stocks = await eastmoney.getStocks(codes);
    for (const s of stocks) {
      if (s.code && s.name) await db.upsertStock(s);
    }
    res.json({ success: true, data: stocks });
  } catch (err) {
    next(err);
  }
});

module.exports = router;
