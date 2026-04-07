# 私人精品网页推荐系统 - 后端 API

基于 FastAPI + SQLAlchemy + MySQL 的后端服务，提供用户注册、登录认证、用户管理等基础功能。

---

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | MySQL (PyMySQL 驱动) |
| 认证 | JWT (python-jose) + OAuth2 |
| 密码加密 | Passlib (bcrypt) |
| 配置管理 | python-dotenv |
| 数据校验 | Pydantic |

---

## 项目结构

```
back/
├── app/
│   ├── main.py                  # 应用入口，FastAPI 实例、中间件、路由注册
│   ├── config.py                # 全局配置（从 .env 读取）
│   ├── dependencies.py          # FastAPI 依赖（JWT 解析、获取当前用户）
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── api.py           # 路由聚合器，统一注册所有 v1 子路由
│   │       ├── auth.py          # 认证相关接口：登录 /token、注册 /register
│   │       └── users.py         # 用户相关接口：获取/更新/删除当前用户
│   │
│   ├── core/
│   │   ├── security.py          # 密码哈希/验证、JWT token 生成
│   │   └── exceptions.py        # 自定义 HTTP 异常（401/403/404/409）
│   │
│   ├── db/
│   │   ├── base_class.py        # SQLAlchemy Base 声明基类
│   │   └── database.py          # 数据库引擎、会话工厂、表初始化
│   │
│   ├── models/
│   │   └── user.py              # User 数据表模型（ORM）
│   │
│   ├── schemas/
│   │   └── user.py              # Pydantic 请求/响应模型
│   │
│   └── services/
│       ├── auth_service.py      # 认证业务逻辑（用户验证、token 创建）
│       └── user_service.py      # 用户业务逻辑（CRUD）
│
├── .env                         # 环境变量配置（密钥、数据库连接等）
└── README.md                    # 本文件
```

---

## 架构分层说明

项目采用经典的四层架构：

```
请求 → API 层 → Service 层 → Model/DB 层
              ↓
           Schema 校验
```

| 层级 | 目录 | 职责 |
|------|------|------|
| **API 层** | `app/api/v1/` | 定义路由端点，接收请求，调用 Service 处理，返回响应 |
| **Service 层** | `app/services/` | 业务逻辑实现（注册、登录、CRUD） |
| **Model 层** | `app/models/` | 数据库表结构映射（ORM） |
| **Schema 层** | `app/schemas/` | 请求/响应的数据校验与序列化（Pydantic） |
| **Core 层** | `app/core/` | 通用工具：安全加密、自定义异常 |
| **DB 层** | `app/db/` | 数据库连接、会话管理 |
| **依赖层** | `app/dependencies.py` | FastAPI 依赖注入（JWT 解析获取当前用户） |

---

## 快速开始

### 1. 环境准备

需要 Python 3.8+ 和 MySQL 数据库。

### 2. 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv \
            python-jose[cryptography] passlib[bcrypt] pydantic
```

### 3. 配置环境变量

编辑 `.env` 文件：

```ini
SECRET_KEY = "自定义长密钥，生产环境务必更换"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
DATABASE_URL = "mysql+pymysql://用户名:密码@localhost:3306/数据库名?charset=utf8"
```

### 4. 创建数据库

在 MySQL 中创建对应名称的数据库（名称需与 `DATABASE_URL` 一致）。

### 5. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- API 文档：http://localhost:8000/docs
- 根路径：http://localhost:8000/

---

## API 接口一览

### 认证模块 (`/api/v1/auth`)

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/token` | 登录获取 Token（OAuth2 表单） | 否 |

### 用户模块 (`/api/v1/users`)

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| GET | `/api/v1/users/me` | 获取当前用户信息 | 是 (Bearer Token) |
| PUT | `/api/v1/users/me` | 更新当前用户信息 | 是 (Bearer Token) |
| DELETE | `/api/v1/users/me` | 删除当前用户（软删除） | 是 (Bearer Token) |

### 鉴权方式

需要认证的接口，在请求头中携带：

```
Authorization: Bearer <access_token>
```

---

## 后续开发流程

### 新增一个功能模块（以"文章"为例）

#### 第 1 步：定义数据模型

在 `app/models/` 下创建模型文件 `article.py`：

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.base_class import Base

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=True)
    # ...
```

#### 第 2 步：定义 Schema

在 `app/schemas/` 下创建请求/响应模型 `article.py`：

```python
from pydantic import BaseModel

class ArticleCreate(BaseModel):
    title: str
    content: str

class ArticleResponse(ArticleCreate):
    id: int
    class Config:
        from_attributes = True
```

#### 第 3 步：编写 Service 业务逻辑

在 `app/services/` 下创建 `article_service.py`，实现 CRUD 等业务逻辑。

#### 第 4 步：编写 API 路由

在 `app/api/v1/` 下创建 `articles.py`，定义路由端点，调用 Service。

#### 第 5 步：注册路由

在 `app/api/v1/api.py` 中添加：

```python
from app.api.v1 import auth, users, articles

api_router.include_router(articles.router)
```

#### 第 6 步：测试

访问 http://localhost:8000/docs 查看自动生成的 Swagger 文档并在线测试。

---

### 关键代码位置速查

| 需求 | 修改位置 |
|------|----------|
| 新增数据表 | `app/models/` 新增模型文件 |
| 新增 API 接口 | `app/api/v1/` 新增路由文件 |
| 新增业务逻辑 | `app/services/` 新增服务文件 |
| 新增请求/响应结构 | `app/schemas/` 新增 schema 文件 |
| 修改 JWT/密码逻辑 | `app/core/security.py` |
| 新增自定义异常 | `app/core/exceptions.py` |
| 修改数据库连接 | `app/db/database.py` |
| 修改全局配置 | `app/config.py` + `.env` |
| 新增依赖注入 | `app/dependencies.py` |
| 添加新中间件 | `app/main.py` |
| 注册新路由 | `app/api/v1/api.py` |

---

## 数据库说明

- 数据库类型：MySQL
- 驱动：PyMySQL
- 表由 SQLAlchemy 自动创建（`Base.metadata.create_all()`）
- 会话管理：每次请求创建新 Session，请求结束自动关闭

---

## 注意事项

1. **生产环境**：务必更换 `.env` 中的 `SECRET_KEY`，使用强随机密钥
2. **密码策略**：当前无密码强度校验，生产环境建议在 Schema 层添加校验
3. **软删除**：用户删除为软删除（`is_active=0`），并非物理删除
4. **CORS**：当前允许 `localhost:3000` 跨域，前端对接时按需调整 `config.py` 中的 `CORS_ORIGINS`
