// 加载 .env（开发用）
try { require("dotenv").config({ path: require("path").join(__dirname, ".env") }); } catch {}

const express = require("express");
const path = require("path");
const db = require("./db");
const { errorHandler } = require("./middleware/error-handler");

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// 股票查询 API（DB 持久化版）
const stocksRouter = require("./routes/stocks-db");
app.use("/api/stocks", stocksRouter);

// 自选股 API
const watchlistRouter = require("./routes/watchlist");
app.use("/api/watchlist", watchlistRouter);

// 静态页面
app.use(express.static(path.join(__dirname, "public")));

// 错误处理
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`[TradeFlow Server] 运行在 http://localhost:${PORT}`);
});
