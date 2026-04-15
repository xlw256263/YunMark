# Docker & Docker Compose 全栈部署完全指南
## —— FastAPI + Vue3 项目从零到上线

---

## 📚 第一部分：Docker 核心概念（先理解再动手）

### 1.1 什么是容器？

**比喻理解：**
- **传统虚拟机** = 整个房子（包含地基、水电、房间、家具）
- **Docker 容器** = 精装公寓包（共用水电系统，每个单元独立封闭）

容器共享宿主机的操作系统内核，但进程空间相互隔离，启动秒级 vs 分钟级。

### 1.2 三大核心概念关系图

```
┌─────────────────────────────────────────────────────────────┐
│                     你的代码                                  │
│   (FastAPI backend / Vue3 frontend)                        │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dockerfile（食谱）                         │
│  FROM → WORKDIR → COPY → RUN → CMD 各指令                    │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
                  构建执行
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   镜像 Image（成品照片）                      │
│  只读模板，可以多次复制使用                                 │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
                  实例化
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   容器 Container（实际端出来的菜）            │
│  运行的实例，可以增删改查                                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Docker Compose 的作用

想象你要同时运行：
- MySQL 数据库
- FastAPI 后端
- Vue3 前端
- Redis 缓存
- Nginx 反向代理

如果没有 Docker Compose，你需要手动输入几十条 `docker run` 命令，而且还要处理依赖顺序、网络互通等问题。**Compose 就是一个 YAML 文件，把 everything 打包编排好。**

```yaml
services:
  mysql: {配置}
  backend: {配置}
  frontend: {配置}
```
一键启动全部服务！

---

## 🏗️ 第二部分：后端 Dockerfile 详解

### 2.1 分析你的后端结构

```bash
back/
├── app/
│   ├── __init__.py
│   ├── main.py          # 入口文件
│   ├── config.py        # 配置文件
│   ├── core/            # 安全、异常处理
│   ├── db/              # 数据库连接
│   ├── models/          # 数据模型
│   ├── schemas/         # 请求响应 schema
│   ├── services/        # 业务逻辑
│   └── api/v1/          # API 路由
├── requirements.txt      # Python 依赖
└── Dockerfile           # ← 我们要写的文件
```

### 2.2 最简版本起步（先跑起来）

在 `back/Dockerfile` 中写入：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

CMD ["python", "app/main.py"]
```

**逐行深度解析：**

| 指令 | 英文原意 | 实际作用 | 为什么要这样 |
|------|---------|---------|-------------|
| `FROM python:3.11-slim` | 来自 Python 3.11 精简版 | 提供运行环境 | 不用自己装 Python，直接复用官方测试好的环境 |
| `WORKDIR /app` | 工作目录设为/app | 后续命令都在此执行 | 统一路径，避免写绝对路径 |
| `COPY . .` | 复制当前所有文件到/app | 把你的代码放进容器 | `.` = 当前目录，`.` = 目标目录（容器的根是 `/app`） |
| `CMD [...]` | 命令 | 容器启动时执行的程序 | 这是容器唯一的"使命" |

> **关键点：** `CMD` 后面的列表有两种写法：
> - **exec 格式**（推荐）：`["python", "app/main.py"]` - 更简洁，不会启动 shell
> - **shell 格式**：`RUN python app/main.py` - 会启动 bash/sh 执行

### 2.3 为什么这个简单版本不行？

运行一下试试就会发现问题：

❌ **问题 1：没有安装依赖**
```
ModuleNotFoundError: No module named 'fastapi'
```
你的 `requirements.txt` 里的包都没装。

❌ **问题 2：镜像体积大**
包含了 Python 的完整安装，不是最小化。

❌ **问题 3：无法调试**
日志缓冲、错误提示都不友好。

❌ **问题 4：每次改代码都要重构建**
代码和依赖混在一起，缓存无法利用。

### 2.4 工程化版本（推荐生产前开发用）

```dockerfile
# ============================================================
# 阶段一：依赖安装层（构建器阶段）
# ============================================================
FROM python:3.11-slim as builder

# 环境变量设置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /tmp

# 单独复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================================
# 阶段二：运行镜像层（最终交付阶段）
# ============================================================
FROM python:3.11-slim

# 安装系统级依赖（pymysql 编译需要 C 工具链）
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 从 builder 阶段复制已安装的 Python 包
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 复制应用代码
COPY ./app /app/app

# 暴露端口（文档说明，不代表自动开启防火墙规则）
EXPOSE 8000

# 健康检查（让 Docker 知道你的服务何时就绪）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# 启动命令（使用 uvicorn 异步服务器）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.5 分层构建原理图解

```
构建过程示意图（Docker 会从上到下逐层构建并缓存）

┌──────────────────────────────────────┐
│  Layer 1: python:3.11-slim           │ ← 基础镜像，几乎不变
│  (基础系统库 + Python 解释器)           │   ✅ 缓存命中
└──────────────────────────────────────┘
              ↓ 继承自上一层
┌──────────────────────────────────────┐
│  Layer 2: 安装系统依赖                │   ⚠️ 只有第一次运行需要
│  gcc, mysql-dev, pkg-config         │   ❌ 下次要重新执行
└──────────────────────────────────────┘
              ↓ 继承自上一层
┌──────────────────────────────────────┐
│  Layer 3: 安装 Python 依赖             │   🔄 依赖变了才刷新
│  pip install -r requirements.txt     │   ✅ 没变就用缓存
└──────────────────────────────────────┘
              ↓ 继承自上一层
┌──────────────────────────────────────┐
│  Layer 4: 复制应用代码                │   🔥 改代码就刷新
│  COPY ./app /app/app                 │   （这一层总是重建）
└──────────────────────────────────────┘
              ↓
        最终镜像 ~180MB
```

### 2.6 关键参数详解

| 指令/参数 | 作用 | 什么时候修改 |
|----------|------|-------------|
| `--no-cache-dir` | pip 不缓存 wheel | 减小镜像体积 |
| `rm -rf /var/lib/apt/lists/*` | 清理 apt 缓存 | 必须加，否则增加 100MB+ |
| `EXPOSE 8000` | 文档声明端口 | 根据你服务的实际端口改 |
| `HEALTHCHECK` | 健康检测 | 有 HTTP 接口就能加 |
| `--from=builder` | 多阶段复制 | 用于分离构建和运行 |

### 2.7 常见问题扩展

#### Q1：要不要加 `.dockerignore`？怎么配？

**一定要！** 否则会把不必要的文件塞进镜像，增大体积甚至泄露敏感信息。

`back/.dockerignore`：
```dockerignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.env.local

# Git
.git
.gitignore
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Docker
Dockerfile
.dockerignore

# Docs
*.md
!README.md

# Test
tests/
.pytest_cache/
.coverage

# Misc
*~
.DS_Store
```

#### Q2：如何让日志实时输出？

已经在环境变量里设置了：
```dockerfile
ENV PYTHONUNBUFFERED=1
```
这会让 Python 不缓存 stdout/stderr，日志立即输出到 Docker。

#### Q3：本地修改代码如何不用 rebuild？

在 `docker-compose.yml` 中添加卷挂载（你已经做了）：
```yaml
volumes:
  - ./app:/app/app  # 本地代码 → 容器内映射
```
这样改本地代码，容器内直接生效，无需 rebuild。

#### Q4：如果依赖里有需要编译的包怎么办？

像 `bcrypt`、`pymysql` 这类需要 C 编译的包，必须在镜像中包含编译工具：
```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*
```

---

## 🎨 第三部分：前端 Dockerfile 详解

### 3.1 分析你的前端结构

通常 Vue3 项目结构如下（根据你的实际情况调整）：

```bash
front/
├── public/           # 静态资源
├── src/              # 源码
│   ├── components/
│   ├── views/
│   ├── api/
│   └── main.js
├── package.json      # Node 依赖
├── vite.config.js    # 构建配置
├── nginx.conf        # Nginx 配置 ← 重要！
└── Dockerfile        # ← 我们要写的文件
```

### 3.2 前端构建特点

前端开发分两个阶段：
1. **开发阶段**：Vite dev server，热更新，直接访问 `localhost:5173`
2. **生产阶段**：`npm run build` 生成 `dist/` 静态文件，用 Nginx 托管

**所以前端 Dockerfile 有两种写法：**

---

### 方案 A：开发环境（热更新）

```dockerfile
FROM node:18-alpine

WORKDIR /app

# 复制 package.json 先安装依赖（利用缓存）
COPY package*.json ./

RUN npm install

# 复制源代码
COPY . .

# 启动 Vite 开发服务器
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**适用场景：** 需要热更新调试前端

---

### 方案 B：生产环境（Nginx 托管）⭐推荐

```dockerfile
# ============================================================
# 阶段一：构建阶段
# ============================================================
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖 manifest
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建静态文件
RUN npm run build

# ============================================================
# 阶段二：运行阶段（Nginx）
# ============================================================
FROM nginx:alpine

# 删除 Nginx 默认站点
RUN rm -rf /usr/share/nginx/html/*

# 复制构建产物到 Nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 默认启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 3.3 nginx.conf 配置详解

在你的 `front/nginx.conf` 中写入：

```nginx
server {
    listen       80;
    server_name  localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # 反向代理到后端 API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 防止 XSS 攻击头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**关键配置解释：**

| 配置项 | 作用 |
|--------|------|
| `try_files $uri $uri/ /index.html` | SPA 路由支持，所有不存在的路径都回退到 index.html |
| `/api/` 代理 | 前端发 `/api/xxx` 的请求转发给后端 |
| `gzip on` | 压缩静态文件，加快加载速度 |
| `X-Frame-Options` | 防点击劫持 |

---

## 🔧 第四部分：docker-compose 完整拆解

### 4.1 你的 docker-compose.yml 逐行解读

让我重新给你完整标注每一行的作用：

```yaml
version: '3.8'  # Compose 文件格式版本，建议用 3.8

services:
  # ========================================
  # 服务 1：MySQL 数据库
  # ========================================
  mysql:
    image: mysql:8.0                    # 使用官方 MySQL 8.0 镜像
    container_name: fastapi_mysql       # 容器名称（方便管理）
    restart: always                     # 容器退出后总是重启
    environment:                        # 环境变量
      MYSQL_ROOT_PASSWORD: root         # root 密码
      MYSQL_DATABASE: user              # 初始化时创建的数据库名
      MYSQL_CHARSET: utf8mb4            # 字符集（中文支持）
      MYSQL_COLLATION: utf8mb4_unicode_ci # 排序规则
    ports:                              # 端口映射
      - "3308:3306"                     # 宿主机 3308 → 容器 3306
    volumes:                            # 数据卷（持久化）
      - mysql_data:/var/lib/mysql       # 自定义卷 → MySQL 数据目录
    networks:                           # 加入的网络
      - app_network
    healthcheck:                        # 健康检查
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]  # 检查命令
      interval: 10s                     # 每 10 秒检查一次
      timeout: 5s                       # 超时时间
      retries: 5                        # 失败 5 次算不健康

  # ========================================
  # 服务 2：FastAPI 后端
  # ========================================
  backend:
    build:                              # 从 Dockerfile 构建
      context: ./back                   # Dockerfile 所在目录
      dockerfile: Dockerfile            # Dockerfile 文件名
    container_name: fastapi_backend
    restart: always
    ports:
      - "8000:8000"                     # 暴露 8000 端口
    environment:                        # 运行时环境变量
      - SECRET_KEY=xixihaha-secret-key-keep-it-safe-123456
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=120
      - DATABASE_URL=mysql+pymysql://root:root@mysql:3306/user?charset=utf8
      - DEBUG=False
    depends_on:                         # 依赖服务
      mysql:
        condition: service_healthy      # 等 mysql 健康后再启动
    networks:
      - app_network
    volumes:
      - ./back/app:/app/app             # 本地代码映射（热更新用）

  # ========================================
  # 服务 3：Vue3 前端
  # ========================================
  frontend:
    build:
      context: ./front
      dockerfile: Dockerfile
    container_name: fastapi_frontend
    restart: always
    ports:
      - "80:80"                         # 对外提供 Web 服务
    depends_on:
      - backend
    networks:
      - app_network

# ========================================
# 数据卷定义（持久化）
# ========================================
volumes:
  mysql_data:                           # 命名卷，不在宿主机特定路径
    driver: local                       # 使用本地驱动

# ========================================
# 网络定义
# ========================================
networks:
  app_network:                          # 自定义桥接网络
    driver: bridge                      # 桥接模式，容器间可以通过服务名通信
```

### 4.2 关键概念对照表

| 术语 | docker-compose 对应 | 解释 |
|------|-------------------|------|
| **image** | `image: mysql:8.0` | 直接使用已有镜像 |
| **build** | `build: {context, dockerfile}` | 从 Dockerfile 构建镜像 |
| **ports** | `ports: ["8000:8000"]` | 端口映射，外部访问入口 |
| **volumes** | `volumes: [mysql_data:/...]` | 数据持久化，容器删了数据还在 |
| **networks** | `networks: [app_network]` | 容器间通信网络 |
| **depends_on** | `depends_on: mysql` | 服务启动顺序控制 |
| **environment** | `environment: [...` | 注入环境变量 |
| **healthcheck** | `healthcheck: {...` | 健康检测配置 |

### 4.3 容器间如何通信？

在你的网络中，所有容器都在 `app_network` 下：

```
mysql:3306    ← backend 连接 → 使用服务名：DATABASE_URL=mysql://...@mysql:3306
backend:8000  ← frontend 连接 → nginx 配置 proxy_pass http://backend:8000
frontend:80   ← 浏览器访问  → localhost:80
```

> **记住：同一网络内的容器通过服务名访问，不需要 IP！**

---

## ⌨️ 第五部分：docker-compose 常用命令速查

### 5.1 生命周期管理

| 命令 | 说明 |
|------|------|
| `docker-compose up` | 启动所有服务 |
| `docker-compose up -d` | 后台运行（detached） |
| `docker-compose up --build` | 强制重新构建镜像再启动 |
| `docker-compose up -d --no-deps` | 只启动指定服务，不启动依赖 |
| `docker-compose down` | 停止并删除容器、网络 |
| `docker-compose down -v` | 删除容器 + 网络 + **数据卷**（谨慎！） |
| `docker-compose restart` | 重启所有服务 |
| `docker-compose stop` | 停止服务（保留容器） |
| `docker-compose start` | 启动已停止的服务 |

### 5.2 日志查看

| 命令 | 说明 |
|------|------|
| `docker-compose logs` | 查看所有服务日志 |
| `docker-compose logs -f` | 跟随日志（类似 tail -f） |
| `docker-compose logs -f backend` | 只看某个服务 |
| `docker-compose logs --tail=100` | 只看最近 100 行 |
| `docker-compose logs --since=1h` | 看最近 1 小时的日志 |

### 5.3 其他实用命令

| 命令 | 说明 |
|------|------|
| `docker-compose ps` | 查看所有容器状态 |
| `docker-compose ps -a` | 包括已停止的容器 |
| `docker-compose exec backend sh` | 进入容器内部（bash/shell） |
| `docker-compose exec backend python` | 直接在容器中运行 Python |
| `docker-compose build` | 只构建镜像，不启动 |
| `docker-compose pull` | 拉取最新镜像（不用 build） |
| `docker-compose config` | 验证 yaml 语法正确性 |
| `docker-compose port backend 8000` | 查看端口映射 |

### 5.4 单服务操作示例

```bash
# 只启动后端（需要先有 MySQL）
docker-compose up -d backend

# 只查看后端日志
docker-compose logs -f backend

# 进入后端容器调试
docker-compose exec backend sh

# 在容器内执行 SQL 查询
docker-compose exec mysql mysql -uroot -proot user

# 停止 MySQL（假设后端依赖它，可能会报错）
docker-compose stop mysql
```

---

## 🛠️ 第六部分：遇到问题自己排查的方法论

### 6.1 五步诊断法

```
1️⃣ 看容器状态
   docker-compose ps
   
   └─ UP 正常 / EXited 异常 / UNHEALTHY 健康检查失败
   
2️⃣ 看日志
   docker-compose logs -f <service_name>
   
   └─ 找 ERROR / EXCEPTION / CRITICAL 关键字
   
3️⃣ 进容器调试
   docker-compose exec <service> sh
   
   └─ 能执行哪些命令？pip list? python? curl?
   
4️⃣ 检查网络
   docker network ls
   docker network inspect app_network
   
   └─ 容器是否在同一网络？IP 分配是否正常？
   
5️⃣ 查依赖
   docker-compose config
   
   └─ YAML 有没有语法错误？变量展开对不对？
```

### 6.2 常见错误及解决方案

| 错误现象 | 原因 | 解决方案 |
|---------|------|---------|
| `Cannot connect to the Docker daemon` | Docker 没启动 | `systemctl start docker` 或打开 Docker Desktop |
| `permission denied` 执行 docker 命令 | 用户无权限 | `sudo` 或加到 docker 组 |
| `Address already in use` | 端口被占用 | 换端口或 `lsof -i :8000` 杀进程 |
| `connection refused` 连不上 DB | DB 还没启动完 | 加 `depends_on + condition: service_healthy` |
| `module not found` | 依赖没装 | check `requirements.txt` 是否完整 |
| `OSError: [Errno 24] Too many open files` | 文件句柄限制 | `ulimit -n 65535` 或改 sysctl |
| `Exit code 137` | OOM Killed（内存溢出） | 增加容器内存限制 |

### 6.3 扩展：自定义 Dockerfile 的情况判断

当你需要自己写 Dockerfile 时，问自己这几个问题：

**Q1：有什么语言/框架？**
```
Python → FROM python:x.x-slim
Node.js → FROM node:x-alpine
Go → FROM golang:x AS builder + FROM alpine
Java → FROM maven AS builder + FROM openjdk:x-jre-alpine
```

**Q2：需要编译吗？**
- Python 需要 `gcc` + `*-dev` 包（如 `pymysql`, `bcrypt`）
- Node.js 需要 `python3` + `make`（部分原生模块）
- Go → 交叉编译，`FROM alpine` 即可
- Java → Maven/Gradle 构建，然后 `jre-alpine` 运行

**Q3：需要系统工具吗？**
```dockerfile
RUN apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*
```

**Q4：需要多少内存？**
```yaml
services:
  your_service:
    mem_limit: 512m
    mem_reservation: 256m
```

**Q5：有敏感信息吗？**
```yaml
# docker-compose.yml
environment:
  - DB_PASSWORD=${DB_PASSWORD}  # 从 .env 读取

# .env 文件（不要提交到 git）
DB_PASSWORD=your_secret_password
```

---

## 📖 第七部分：最佳实践清单

### 7.1 Dockerfile 编写规范

- [ ] 使用多阶段构建减少镜像大小
- [ ] 使用具体版本号（`python:3.11.4-slim` 而不是 `python:latest`）
- [ ] 合并 `RUN` 指令减少层数
- [ ] 清理缓存（apt get clean, rm -rf /var/lib/apt/lists/*）
- [ ] 非 root 用户运行（生产环境）
- [ ] 添加 `.dockerignore` 排除无用文件
- [ ] 使用 `HEALTHCHECK` 监控服务状态
- [ ] 避免在镜像中存储敏感信息

### 7.2 docker-compose 规范

- [ ] 使用 `depends_on + condition: service_healthy` 管理依赖
- [ ] 定义自定义网络隔离服务
- [ ] 使用命名卷持久化数据
- [ ] 敏感信息用 `.env` 文件管理
- [ ] 区分 `development` 和 `production` compose 文件
- [ ] 设置合理的 `restart` 策略
- [ ] 明确定义端口映射（开发用）vs 仅内部访问（生产用）

### 7.3 开发 vs 生产环境差异

| 方面 | 开发环境 | 生产环境 |
|------|---------|---------|
| Dockerfile | 简单版，带调试信息 | 多阶段构建，极致优化 |
| volumes | 挂载源码热更新 | 只挂载配置文件/数据 |
| restart | no 或 on-failure | always |
| logging | json-file | json-file + max-size/max-file |
| resources | 不设限 | CPU/Mem limit |
| secrets | 直接写在 yml | 用 Docker Secret / Vault |

---

## 🎯 第八部分：快速上手步骤总结

### 你的项目现在应该有的文件结构

```
FastAPI_demo/
├── back/
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile          ← 新建
│   └── .dockerignore       ← 新建
├── front/
│   ├── src/
│   │   └── ...
│   ├── package.json
│   ├── nginx.conf          ← 自建
│   ├── Dockerfile          ← 新建
│   └── .dockerignore       ← 可选
├── docker-compose.yml      ← 已有
└── .env                    ← 自建（存放敏感信息）
```

### 从零到运行 7 步走

```bash
# 1. 准备文件
cd back && touch Dockerfile .dockerignore
cd ../front && touch Dockerfile nginx.conf .dockerignore

# 2. 填入各自 Dockerfile 内容

# 3. 创建 .env 文件（敏感信息）
cat > .env << EOF
SECRET_KEY=xixihaha-secret-key-keep-it-safe-123456
MYSQL_ROOT_PASSWORD=root
DATABASE_URL=mysql+pymysql://root:root@mysql:3306/user?charset=utf8
EOF

# 4. 验证配置
docker-compose config

# 5. 构建并启动
docker-compose up -d --build

# 6. 查看状态
docker-compose ps

# 7. 查看日志（前几次启动看看）
docker-compose logs -f backend
docker-compose logs -f mysql
```

### 访问地址

- 前端：http://localhost
- 后端 API：http://localhost:8000
- Swagger Docs：http://localhost:8000/docs
- MySQL 客户端连接：`localhost:3308`（注意端口映射）

---

## 🚀 第九部分：进阶方向（了解即可）

1. **镜像优化** - 使用 Distroless / Crunchybase 镜像缩小到几 MB
2. **CI/CD集成** - GitHub Actions 自动构建推送 Docker Hub
3. **镜像仓库** - Docker Hub私有仓库 / Harbor / AWS ECR
4. **Kubernetes** - 容器编排扩展到集群级别
5. **服务网格** - Istio 做流量管理/熔断/链路追踪
6. **监控告警** - Prometheus + Grafana + AlertManager
7. **日志收集** - ELK Stack / Loki + Promtail + Grafana

---

## 📝 附录：速查表

### Dockerfile 高频指令

| 指令 | 示例 | 说明 |
|------|------|------|
| `FROM` | `FROM python:3.11-slim` | 基础镜像 |
| `RUN` | `RUN apt-get update` | 执行命令 |
| `COPY` | `COPY . .` | 复制文件 |
| `ADD` | `ADD https://... .` | 复制 + 解压/下载 |
| `WORKDIR` | `WORKDIR /app` | 切换目录 |
| `ENV` | `ENV VAR=value` | 设置环境变量 |
| `EXPOSE` | `EXPOSE 8000` | 声明端口 |
| `CMD` | `CMD ["python", "app.py"]` | 启动命令 |
| `ENTRYPOINT` | `ENTRYPOINT ["python"]` | 入口点（可被覆盖） |
| `ARG` | `ARG VERSION=1.0` | 构建时参数 |
| `USER` | `USER nobody` | 切换用户 |
| `HEALTHCHECK` | `HEALTHCHECK ...` | 健康检查 |

### docker-compose 高频字段

| 字段 | 说明 |
|------|------|
| `image` | 镜像名 |
| `build` | 从 Dockerfile 构建 |
| `ports` | 端口映射 |
| `volumes` | 数据卷 |
| `environment` | 环境变量 |
| `env_file` | 读取.env 文件 |
| `depends_on` | 依赖服务 |
| `networks` | 网络 |
| `restart` | 重启策略 |
| `command` | 覆盖默认命令 |
| `container_name` | 容器名称 |
| `labels` | 标签 |
| `deploy` | 部署配置（Swarm） |

---

**最后提醒：**

> Docker 的核心思想是 **"一次构建，到处运行"**，而 Docker Compose 的核心是 **"一键编排，全栈启动"**。先把基本流程跑通，遇到问题再看日志调试，慢慢就熟练了。

有任何不清楚的地方，随时问我！🎉
