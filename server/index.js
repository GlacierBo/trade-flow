"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const routes_1 = __importDefault(require("./routes"));
const error_handler_1 = require("./middleware/error-handler");
const app = (0, express_1.default)();
const PORT = process.env.PORT || 3000;
// 中间件
app.use(express_1.default.json());
// API 路由
app.use("/api", routes_1.default);
// 生产模式：serve 前端静态文件
if (process.env.NODE_ENV === "production") {
    const clientPath = path_1.default.join(__dirname, "../../client/dist");
    app.use(express_1.default.static(clientPath));
    app.get("*", (_req, res) => {
        res.sendFile(path_1.default.join(clientPath, "index.html"));
    });
}
// 错误处理
app.use(error_handler_1.errorHandler);
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
//# sourceMappingURL=index.js.map