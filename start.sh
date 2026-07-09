#!/bin/bash
# TradeFlow 一键启动脚本 (Git Bash / Linux / macOS)
# Usage: bash start.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_LOG="/tmp/tradeflow-backend.log"
FRONTEND_LOG="/tmp/tradeflow-frontend.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Helper: kill process on a given port ──
kill_port() {
    local port=$1
    local pids

    # Try lsof first (Linux/Mac)
    if command -v lsof &>/dev/null; then
        pids=$(lsof -ti:"$port" 2>/dev/null)
    # Fallback: netstat + awk (Git Bash / Windows)
    elif command -v netstat &>/dev/null; then
        pids=$(netstat -ano 2>/dev/null | grep ":$port " | awk '{print $NF}' | sort -u)
    fi

    if [ -z "$pids" ]; then
        return 0
    fi

    # Filter out PID 0 (netstat artifact on Windows)
    local valid_pids
    valid_pids=$(echo "$pids" | grep -v '^0$')
    [ -z "$valid_pids" ] && return 0

    local pid_list
    pid_list=$(echo "$valid_pids" | tr '\n' ' ' | sed 's/  *$//')
    echo -e "  ⚠️  端口 $port 被占用 (PID: $pid_list)，正在释放..."

    for pid in $valid_pids; do
        # Windows (Git Bash / MSYS) → use dash-style to avoid MSYS path conversion
        if command -v taskkill &>/dev/null; then
            taskkill -f -pid "$pid" &>/dev/null || true
        # Linux / Mac → kill
        else
            kill "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
        fi
    done

    sleep 1
    echo -e "  ✅ 端口 $port 已释放"
}

cleanup() {
    echo ""
    echo -e "${YELLOW}正在关闭服务...${NC}"
    [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null && echo -e "${GREEN}后端已停止${NC}"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && echo -e "${GREEN}前端已停止${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   TradeFlow 一键启动${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ── Check dependencies ──
echo -e "${YELLOW}[1/5] 检查环境...${NC}"
if ! command -v python &>/dev/null; then
    echo -e "${RED}  ❌ 未找到 python，请安装 Python 3.10+${NC}"
    exit 1
fi
if ! command -v node &>/dev/null; then
    echo -e "${RED}  ❌ 未找到 node，请安装 Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}  ✅ Python $(python --version | cut -d' ' -f2)${NC}"
echo -e "${GREEN}  ✅ Node $(node --version)${NC}"

# ── Check & free ports ──
echo ""
echo -e "${YELLOW}[2/5] 检查端口占用...${NC}"
kill_port 3001
kill_port 5173

# ── Install backend deps if needed ──
echo ""
echo -e "${YELLOW}[3/5] 检查后端依赖...${NC}"
if pip list 2>/dev/null | grep -q fastapi; then
    echo -e "${GREEN}  ✅ 后端依赖已安装${NC}"
else
    echo -e "${YELLOW}  正在安装后端依赖...${NC}"
    cd "$BACKEND_DIR"
    pip install -r requirements.txt -q
    echo -e "${GREEN}  ✅ 后端依赖安装完成${NC}"
fi

# ── Install frontend deps if needed ──
echo ""
echo -e "${YELLOW}[4/5] 检查前端依赖...${NC}"
if [ -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${GREEN}  ✅ 前端依赖已安装${NC}"
else
    echo -e "${YELLOW}  正在安装前端依赖...${NC}"
    cd "$FRONTEND_DIR"
    npm install --silent
    echo -e "${GREEN}  ✅ 前端依赖安装完成${NC}"
fi

# ── Start services ──
echo ""
echo -e "${YELLOW}[5/5] 启动服务...${NC}"

# Backend
cd "$BACKEND_DIR"
python -m main &> "$BACKEND_LOG" &
BACKEND_PID=$!
echo -e "  📦 后端启动中 (PID: $BACKEND_PID)..."

for i in $(seq 1 30); do
    if curl -sf http://localhost:3001/docs > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ 后端已启动 → http://localhost:3001${NC}"
        echo -e "${GREEN}     API 文档  → http://localhost:3001/docs${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}  ❌ 后端启动超时，请查看日志: tail -f $BACKEND_LOG${NC}"
    fi
    sleep 1
done

# Frontend
cd "$FRONTEND_DIR"
npm run dev &> "$FRONTEND_LOG" &
FRONTEND_PID=$!
echo -e "  🎨 前端启动中 (PID: $FRONTEND_PID)..."

for i in $(seq 1 30); do
    if curl -sf http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}  ✅ 前端已启动 → http://localhost:5173${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}  ❌ 前端启动超时，请查看日志: tail -f $FRONTEND_LOG${NC}"
    fi
    sleep 1
done

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}   TradeFlow 已就绪！${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "  前端:  ${GREEN}http://localhost:5173${NC}"
echo -e "  后端:  ${GREEN}http://localhost:3001${NC}"
echo -e "  Swagger: ${GREEN}http://localhost:3001/docs${NC}"
echo -e ""
echo -e "  账号: ${YELLOW}admin${NC} / ${YELLOW}admin${NC}  (管理员)"
echo -e "         ${YELLOW}user001${NC} / ${YELLOW}123456${NC}  (普通用户)"
echo -e ""
echo -e "  按 ${RED}Ctrl+C${NC} 停止所有服务"
echo -e "${CYAN}========================================${NC}"

# Wait for either process to exit
wait
