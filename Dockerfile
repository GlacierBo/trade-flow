# ==============================================================================
# TradeFlow 多阶段 Dockerfile 【优化版】
# 优化点：分层缓存、镜像瘦身、安全加固、构建提速、精简指令
# ==============================================================================

# ---------------------------------------------------------------------------
# Stage 1: 前端构建 (Vue3 + Vite) - alpine 原生极速，无需改动
# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-build

WORKDIR /build/frontend

# 优先拷贝依赖文件，最大化缓存
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

# 拷贝源码 & 构建
COPY frontend/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: Python 运行环境（最终镜像）
# 优化apt + 分层顺序优化 + 安全配置
# ---------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app/backend

# 安装 curl 并清理缓存（使用 Debian 官方源）
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 3. Python 全局优化：禁用pyc、开启缓冲
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DATABASE_TYPE=sqlite \
    PORT=3001 \
    # 设置 UTF-8 语言环境，解决中文乱码问题
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 4. 优先拷贝依赖文件，利用Docker缓存（代码变更不重跑pip）
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5. 拷贝后端源码
COPY backend/ ./

# 6. 拷贝前端静态产物
COPY --from=frontend-build /build/frontend/dist ./public

# 7. 提前创建数据目录，统一权限
RUN mkdir -p /app/data

EXPOSE 3001

# 健康检查（保留原逻辑，curl已就绪）
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:3001/docs || exit 1

# 启动命令（保留原有逻辑）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]