// 统一行情接口：优先用 EastMoney（字段全），失败后自动切换到腾讯/新浪
const eastmoney = require("./eastmoney");
const { stocks: providers } = require("../providers");
const { DEFAULT_STOCK } = require("../utils/constant");

const auto = providers.auto;

// 将 stock-api 的 7 字段格式转为统一 14 字段格式
function normalizeStock(s) {
  return {
    code: s.code || "",
    name: s.name || "---",
    price: s.now ?? null,
    changePercent: s.percent != null ? s.percent * 100 : null, // 0.01 → 1%
    open: null,
    high: s.high ?? null,
    low: s.low ?? null,
    yesterday: s.yesterday ?? null,
    volume: null,
    amount: null,
    amplitude: null,
    turnoverRate: null,
    totalMarketCap: null,
    source: s.source || "auto",
  };
}

// 统一搜索
async function searchStocks(keyword) {
  try {
    // 优先用 eastmoney 搜索（字段全）
    const em = await eastmoney.searchStocks(keyword);
    if (em.length > 0) return em;
  } catch {}
  // 降级：用 auto provider 搜索（多源 failover）
  try {
    const results = await auto.searchStocks(keyword);
    return results.filter((s) => s.name && s.name !== DEFAULT_STOCK.name).map(normalizeStock);
  } catch {
    return [];
  }
}

// 统一批量查询
async function getStocks(codes) {
  if (!codes.length) return [];
  // 先试试 eastmoney
  try {
    const em = await eastmoney.getStocks(codes);
    if (em.length > 0) return em;
  } catch {}
  // 降级：用 auto provider
  try {
    const results = await auto.getStocks(codes);
    return results
      .filter((s) => s.name && s.name !== DEFAULT_STOCK.name)
      .map(normalizeStock);
  } catch {
    return codes.map((c) => ({ code: c, name: "---" }));
  }
}

// 统一单只查询
async function getStock(code) {
  const stocks = await getStocks([code]);
  return stocks[0] || null;
}

module.exports = { searchStocks, getStocks, getStock };
