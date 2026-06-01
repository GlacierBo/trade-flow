"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const stocks_1 = __importDefault(require("./stocks"));
const providers_1 = require("../providers");
const router = (0, express_1.Router)();
// 股票相关路由
router.use("/stocks", stocks_1.default);
// 获取可用数据源
router.get("/sources", (_req, res) => {
    res.json({
        success: true,
        data: providers_1.stocks.getSources(),
    });
});
exports.default = router;
//# sourceMappingURL=index.js.map