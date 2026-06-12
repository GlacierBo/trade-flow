# ==============================================================================
# TradeFlow 多阶段 Dockerfile
# ==============================================================================
# Stage 1: 构建前端 (Vue 3 + Vite)
# Stage 2: Python 应用 + 预先构建的前端静态资源
#
# 使用方法:
#   docker build -t tradeflow .
#   docker run -p 3001:3001 -v ./data:/app/data tradeflow
# ==============================================================================

# ---------------------------------------------------------------------------
# Stage 1: 前端构建
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-build

WORKDIR /build/frontend

# 先安装依赖（利用 Docker 层缓存）
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund 2>/dev/null || npm install --no-audit --no-fund

# 复制源码并构建
COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Python 应用
# ---------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app/backend

# 安装系统依赖（curl 用于 healthcheck）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（利用层缓存）
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源代码
COPY backend/ ./

# 复制前端构建产物到 public 目录（FastAPI 从此目录提供静态文件）
COPY --from=frontend-build /build/frontend/dist ./public

# 创建数据目录（存放 SQLite 数据库文件）
RUN mkdir -p /app/data

# 环境变量默认值
ENV PYTHONUNBUFFERED=1 \
    DATABASE_TYPE=sqlite \
    PORT=3001

EXPOSE 3001

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3001/docs || exit 1

# 使用 uvicorn 直接启动（避免 main.py 中的 reload=True）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
