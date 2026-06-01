"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const providers_1 = require("../providers");
const router = (0, express_1.Router)();
function getSource(source) {
    switch (source) {
        case "tencent":
            return providers_1.stocks.tencent;
        case "sina":
            return providers_1.stocks.sina;
        case "eastmoney":
            return providers_1.stocks.eastmoney;
        case "auto":
        default:
            return providers_1.stocks.auto;
    }
}
// 搜索股票
router.get("/search", async (req, res, next) => {
    try {
        const { q, source } = req.query;
        if (!q || typeof q !== "string") {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: q",
            });
        }
        const provider = getSource(source);
        const results = await provider.searchStocks(q);
        res.json({
            success: true,
            data: results,
        });
    }
    catch (err) {
        next(err);
    }
});
// 查询单只股票
router.get("/:code", async (req, res, next) => {
    try {
        const { code } = req.params;
        const { source } = req.query;
        const provider = getSource(source);
        const stock = await provider.getStock(code);
        res.json({
            success: true,
            data: stock,
        });
    }
    catch (err) {
        next(err);
    }
});
// 批量查询
router.post("/batch", async (req, res, next) => {
    try {
        const { codes, source } = req.body;
        if (!Array.isArray(codes) || codes.length === 0) {
            return res.status(400).json({
                success: false,
                error: "Missing required parameter: codes (array)",
            });
        }
        if (codes.length > 20) {
            return res.status(400).json({
                success: false,
                error: "Maximum 20 codes per batch request",
            });
        }
        const provider = getSource(source);
        const results = await provider.getStocks(codes);
        res.json({
            success: true,
            data: results,
        });
    }
    catch (err) {
        next(err);
    }
});
exports.default = router;
//# sourceMappingURL=stocks.js.map