"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const constant_1 = require("../../utils/constant");
const fetch_1 = __importDefault(require("../../utils/fetch"));
const provider_1 = require("../shared/provider");
const common_code_1 = __importDefault(require("./transforms/common-code"));
const stock_1 = require("./transforms/stock");
const quoteFields = "f12,f14,f2,f3,f15,f16,f18";
const suggestToken = "D43BF722C8E33BDC906FB84D85E326E8";
async function getStocks(codes) {
    const normalizedCodes = (0, provider_1.normalizeCodes)(codes);
    if (normalizedCodes.length === 0) {
        return [];
    }
    return Promise.all(normalizedCodes.map(fetchOneStock));
}
const Eastmoney = {
    async getStock(code) {
        const [stock] = await getStocks([code]);
        return stock || createMissingStock(code);
    },
    getStocks,
    async searchStocks(key) {
        const response = await requestJson(`https://searchapi.eastmoney.com/api/suggest/get?input=${encodeURIComponent(key)}&type=14&token=${suggestToken}`);
        const codes = (response.QuotationCodeTable?.Data || [])
            .map(parseSuggestCode)
            .filter(Boolean);
        return getStocks(codes);
    },
    async inspectStock(code) {
        return (0, provider_1.createStockInspection)("eastmoney", code, Eastmoney.getStock);
    },
};
async function fetchOneStock(code) {
    const apiCode = common_code_1.default.transform(code);
    const response = await requestJson(`https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=${encodeURIComponent(apiCode)}&fields=${quoteFields}`);
    const [quote] = getQuoteRows(response);
    if (!quote?.f12) {
        return createMissingStock(code);
    }
    return (0, stock_1.parseEastmoneyStock)(code, quote);
}
function parseSuggestCode(item) {
    const quoteId = item.QuoteID || "";
    const code = item.Code || quoteId.split(".")[1] || "";
    const market = item.MktNum || quoteId.split(".")[0] || "";
    if (!code)
        return "";
    if (market === "1")
        return `SH${code}`;
    if (market === "0")
        return `SZ${code}`;
    return "";
}
function createMissingStock(code) {
    return { ...constant_1.DEFAULT_STOCK, code };
}
async function requestJson(url) {
    const response = await fetch_1.default
        .get(url)
        .set("Accept", "application/json,text/plain,*/*")
        .set("Referer", "https://quote.eastmoney.com/");
    return JSON.parse(response.text);
}
function getQuoteRows(response) {
    const diff = response.data?.diff;
    if (!diff)
        return [];
    if (Array.isArray(diff))
        return diff;
    return Object.values(diff);
}
exports.default = Eastmoney;
//# sourceMappingURL=index.js.map