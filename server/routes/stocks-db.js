const express = require("express");
const market = require("../api-client/market");
const db = require("../db");

const router = express.Router();

// 搜索股票（仅查行情，不存库）
router.get("/search", async (req, res) => {
  try {
    const { q } = req.query;
    if (!q || typeof q !== "string") {
      return res.status(400).json({ success: false, error: "Missing q" });
    }
    const stocks = await market.searchStocks(q);
    res.json({ success: true, data: stocks });
  } catch (err) {
    console.error("search error:", err.message);
    res.status(502).json({ success: false, error: "行情服务暂不可用，请稍后重试" });
  }
});

// 查询单只股票详情（优先 DB，DB 没有则查行情并存入 DB）
router.get("/:code", async (req, res) => {
  try {
    const { code } = req.params;
    // 先看 DB 有没有最新记录
    let stock = await db.getLatestStock(code);
    if (stock) return res.json({ success: true, data: stock });

    // DB 没有则查行情
    stock = await market.getStock(code);
    if (stock?.name) {
      stock.code = code;
      await db.insertStock(stock);
    }
    res.json({ success: true, data: stock });
  } catch (err) {
    console.error("getStock error:", err.message);
    res.status(502).json({ success: false, error: "行情服务暂不可用，请稍后重试" });
  }
});

module.exports = router;
