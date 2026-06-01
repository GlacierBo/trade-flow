// 东方财富行情 API 直调（使用 stock-api 的 fetch 工具）
const fetch = require("../utils/fetch").default;

const QUERY_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get";
const SUGGEST_URL = "https://searchapi.eastmoney.com/api/suggest/get";
const SUGGEST_TOKEN = "D43BF722C8E33BDC906FB84D85E326E8";

const FIELDS = [
  "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f10",
  "f12", "f14", "f15", "f16", "f17", "f18", "f20", "f21", "f69",
].join(",");

function codeToSecid(code) {
  if (code.startsWith("SH")) return `1.${code.slice(2)}`;
  if (code.startsWith("SZ")) return `0.${code.slice(2)}`;
  return code;
}

function toNum(v) {
  if (v === undefined || v === null || v === "-") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function parseQuote(q) {
  return {
    code: q.f12 || "",
    name: q.f14 || "---",
    price: toNum(q.f2),
    changePercent: toNum(q.f3),  // 如 0.5 = 0.5%
    open: toNum(q.f17),
    high: toNum(q.f15),
    low: toNum(q.f16),
    yesterday: toNum(q.f18),
    volume: toNum(q.f5),
    amount: toNum(q.f6),
    amplitude: toNum(q.f7),
    turnoverRate: toNum(q.f8),
    totalMarketCap: toNum(q.f20),
    source: "eastmoney",
  };
}

async function requestJson(url) {
  const response = await fetch
    .get(url)
    .set("Accept", "application/json,text/plain,*/*")
    .set("Referer", "https://quote.eastmoney.com/");
  return JSON.parse(response.text);
}

async function getStock(code) {
  const secid = codeToSecid(code);
  const url = `${QUERY_URL}?fltt=2&secids=${encodeURIComponent(secid)}&fields=${FIELDS}`;
  const data = await requestJson(url);
  const diff = data?.data?.diff;
  if (!diff) return null;
  const quotes = Array.isArray(diff) ? diff : Object.values(diff);
  const q = quotes.find((x) => x.f12);
  return q ? { ...parseQuote(q), code } : null;
}

async function getStocks(codes) {
  if (!codes.length) return [];
  const secids = codes.map(codeToSecid).join(",");
  const url = `${QUERY_URL}?fltt=2&secids=${encodeURIComponent(secids)}&fields=${FIELDS}`;
  const data = await requestJson(url);
  const diff = data?.data?.diff;
  if (!diff) return [];
  const quotes = Array.isArray(diff) ? diff : Object.values(diff);
  const codeMap = {};
  for (const c of codes) {
    if (!c) continue;
    const raw = c.replace(/^(SH|SZ)/, "");
    codeMap[raw] = c;
  }
  return quotes
    .filter((q) => q.f12)
    .map((q) => ({
      ...parseQuote(q),
      code: codeMap[String(q.f12)] || q.f12,
    }));
}

async function searchStocks(keyword) {
  const url = `${SUGGEST_URL}?input=${encodeURIComponent(keyword)}&type=14&token=${SUGGEST_TOKEN}`;
  const data = await requestJson(url);
  const items = data?.QuotationCodeTable?.Data || [];
  const codes = [];
  for (const item of items) {
    const code = item.Code || "";
    const market = item.MktNum || "";
    if (!code) continue;
    if (market === "1") codes.push(`SH${code}`);
    else if (market === "0") codes.push(`SZ${code}`);
  }
  if (!codes.length) return [];
  return getStocks(codes);
}

module.exports = { getStock, getStocks, searchStocks };
