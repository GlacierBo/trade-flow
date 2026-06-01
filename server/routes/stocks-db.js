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

// 搜索股票
router.get("/search", async (req, res) => {
  try {
    const { q } = req.query;
    if (!q || typeof q !== "string") {
      return res.status(400).json({ success: false, error: "Missing q" });
    }
    const stocks = await market.searchStocks(q);
    for (const s of stocks) tryUpsert(s);
    res.json({ success: true, data: stocks });
  } catch (err) {
    console.error("search error:", err.message);
    res.status(502).json({ success: false, error: "行情服务暂不可用，请稍后重试" });
  }
});

// 查询单只股票
router.get("/:code", async (req, res) => {
  try {
    const { code } = req.params;
    const stock = await market.getStock(code);
    if (stock && stock.name) {
      stock.code = code;
      tryUpsert(stock);
    }
    res.json({ success: true, data: stock });
  } catch (err) {
    console.error("getStock error:", err.message);
    res.status(502).json({ success: false, error: "行情服务暂不可用，请稍后重试" });
  }
});

// 批量查询
router.post("/batch", async (req, res) => {
  try {
    const { codes } = req.body;
    if (!Array.isArray(codes) || !codes.length) {
      return res.status(400).json({ success: false, error: "Missing codes" });
    }
    const stocks = await market.getStocks(codes);
    for (const s of stocks) tryUpsert(s);
    res.json({ success: true, data: stocks });
  } catch (err) {
    console.error("batch error:", err.message);
    res.status(502).json({ success: false, error: "行情服务暂不可用，请稍后重试" });
  }
});

module.exports = router;
