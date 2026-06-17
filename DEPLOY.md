# TradeFlow 部署文档

## 目录

- [环境要求](#环境要求)
- [前端部署](#前端部署)
- [后端部署](#后端部署)
- [Docker 部署](#docker-部署)
- [Nginx 配置](#nginx-配置)
- [常见问题](#常见问题)

---

## 环境要求

| 组件 | 版本要求 |
|------|----------|
| Node.js | >= 18.x |
| Python | >= 3.10 |
| MySQL | >= 8.0 |
| npm | >= 9.x |
| pip | >= 22.x |

---

## 前端部署

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，按需配置。

### 3. 开发模式

```bash
npm run dev
```

访问 `http://localhost:5173`

### 4. 生产打包

```bash
npm run build
```

打包产物在 `frontend/dist/` 目录。

### 5. 部署静态文件

将 `frontend/dist/` 目录部署到任意静态文件服务器：

- **Nginx**: 参考下方 Nginx 配置
- **Apache**: 将文件复制到 `/var/www/html/`
- **Vercel**: `vercel --prod`
- **GitHub Pages**: 推送到 main 分支自动部署

---

## 后端部署

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=trade_flow
PORT=3001
```

### 3. 初始化数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE trade_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行建表语句
mysql -u root -p trade_flow < sql/schema.sql
```

### 4. 启动服务

#### 方式 1: 直接运行

```bash
python -m app.main
```

#### 方式 2: 使用 uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3001
```

添加 `--reload` 参数支持热重载（开发模式）：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

#### 方式 3: 使用 gunicorn（生产推荐）

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:3001
```

参数说明：
- `-w 4`: 4 个 worker 进程
- `-k uvicorn.workers.UvicornWorker`: 使用 uvicorn 的 worker 类
- `-b 0.0.0.0:3001`: 绑定地址和端口

### 5. 访问 API 文档

服务启动后访问：
- Swagger UI: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`

---

## Systemd 服务配置（Linux）

### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/tradeflow.service
```

### 2. 写入配置

```ini
[Unit]
Description=TradeFlow Backend Service
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=/opt/tradeflow/backend
Environment="PATH=/opt/tradeflow/backend/venv/bin"
ExecStart=/opt/tradeflow/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 3001
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 3. 启动服务

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 设置开机自启
sudo systemctl enable tradeflow

# 启动服务
sudo systemctl start tradeflow

# 查看状态
sudo systemctl status tradeflow

# 查看日志
sudo journalctl -u tradeflow -f
```

---

## Docker 部署

### 后端 Dockerfile

在 `backend/` 目录下创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 3001

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
```

### Docker Compose

在项目根目录创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8
    container_name: tradeflow-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: your_root_password
      MYSQL_DATABASE: trade_flow
      MYSQL_USER: tradeflow
      MYSQL_PASSWORD: your_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backend/sql/schema.sql:/docker-entrypoint-initdb.d/init.sql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

  backend:
    build: ./backend
    container_name: tradeflow-backend
    restart: always
    ports:
      - "3001:3001"
    environment:
      MYSQL_HOST: mysql
      MYSQL_PORT: 3306
      MYSQL_USER: tradeflow
      MYSQL_PASSWORD: your_password
      MYSQL_DATABASE: trade_flow
    depends_on:
      - mysql

  frontend:
    image: nginx:alpine
    container_name: tradeflow-frontend
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend

volumes:
  mysql_data:
```

### 启动 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## Nginx 配置

创建 `nginx.conf` 文件：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # UTF-8 编码（解决中文乱码）
    charset utf-8;
    charset_types text/plain text/css application/json application/javascript text/xml;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://backend:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 禁用压缩传输，避免编码问题
        proxy_set_header Accept-Encoding "";

        # WebSocket 支持（如需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
}
```

### 非 Docker 环境的 Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # UTF-8 编码（解决中文乱码）
    charset utf-8;
    charset_types text/plain text/css application/json application/javascript text/xml;

    # 前端静态文件
    root /opt/tradeflow/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 禁用压缩传输，避免编码问题
        proxy_set_header Accept-Encoding "";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 1000;
}
```

---

## 常见问题

### 1. 数据库连接失败

检查 MySQL 服务是否启动，以及 `.env` 中的数据库配置是否正确。

```bash
# 检查 MySQL 状态
sudo systemctl status mysql

# 测试连接
mysql -u root -p -h localhost
```

### 2. 端口被占用

```bash
# 查看端口占用
lsof -i :3001

# 或 Windows
netstat -ano | findstr :3001
```

### 3. 前端无法访问 API

确保：
1. 后端服务已启动
2. Nginx 配置正确
3. 浏览器控制台无跨域错误

### 4. CORS 跨域问题

开发模式下，Vite 会自动代理 `/api` 请求。生产环境需要配置 Nginx 反向代理。

### 5. 数据库表不存在

执行建表语句：

```bash
mysql -u root -p trade_flow < backend/sql/schema.sql
```

---

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin | 管理员 |
| user001 | 123456 | 普通用户 |

> ⚠️ 部署到生产环境后，请立即修改默认密码！
