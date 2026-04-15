# 云藏·智能收藏夹 — 前后端接口对接文档

| 字段 | 内容 |
|------|------|
| 文档版本 | v1.0 |
| 创建日期 | 2026-04-14 |
| 后端框架 | FastAPI 0.109.0 + SQLAlchemy 2.x + MySQL + JWT |
| 前端框架 | Vue 3 + Vite + Pinia + Element Plus + Axios + TypeScript |
| 基础路径 | `http://localhost:8000/api/v1` |

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-14 | 初始版本，基于当前后端已实现 API + PRD 规划的新增接口 |

---

## 目录

1. [通用约定](#1-通用约定)
2. [认证模块（Auth）](#2-认证模块auth)
3. [用户模块（User）](#3-用户模块user)
4. [书签模块（Bookmark）](#4-书签模块bookmark)
5. [分类模块（Category）](#5-分类模块category)
6. [标签模块（Tag）](#6-标签模块tag)
7. [统计模块（Stats）— 待开发](#7-统计模块stats--待开发)
8. [公开分享模块（Public）— 待开发](#8-公开分享模块public--待开发)
9. [管理员模块（Admin）— 待开发](#9-管理员模块admin--待开发)
10. [前端 Axios 封装规范](#10-前端-axios-封装规范)
11. [前端 TypeScript 类型定义](#11-前端-typescript-类型定义)
12. [错误码对照表](#12-错误码对照表)

---

## 1. 通用约定

### 1.1 请求格式

- 所有接口使用 `application/json`（登录接口除外，使用 `application/x-www-form-urlencoded`）
- 字符编码：`UTF-8`
- 认证接口：`POST /api/v1/auth/token` 使用 OAuth2 标准格式，Body 传 `username`（实际为邮箱）+ `password`

### 1.2 认证方式

所有需要登录的接口，需在请求头携带 JWT Token：

```
Authorization: Bearer <access_token>
```

Token 有效期：**30 分钟**（可配置 `ACCESS_TOKEN_EXPIRE_MINUTES`）

### 1.3 统一响应结构

**成功响应**：直接返回 Pydantic Schema 定义的 JSON 对象

```json
{
  "id": 1,
  "username": "xiaoming",
  "email": "xiaoming@email.com",
  "is_active": 1
}
```

**分页响应**：

```json
{
  "total": 48,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```

**错误响应**：

```json
{
  "detail": "具体错误信息"
}
```

### 1.4 跨域配置

后端 CORS 已配置，允许的 Origin：

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

前端开发服务器默认 `5173` 端口，已在白名单内。

---

## 2. 认证模块（Auth）

**基础路径**：`/api/v1/auth`

### 2.1 用户注册

| 属性 | 值 |
|------|---|
| 方法 | `POST` |
| 路径 | `/auth/register` |
| 认证 | 无需登录 |
| 状态 | ✅ 已实现 |

**请求体** `UserCreate`：

```json
{
  "username": "xiaoming",
  "email": "xiaoming@email.com",
  "password": "securepassword123"
}
```

**成功响应** `200` `UserResponse`：

```json
{
  "id": 1,
  "username": "xiaoming",
  "email": "xiaoming@email.com",
  "is_active": 1
}
```

**错误响应**：

| 状态码 | detail | 说明 |
|--------|--------|------|
| 409 | Username already exists | 用户名已存在 |
| 409 | Email already exists | 邮箱已存在 |

---

### 2.2 用户登录

| 属性 | 值 |
|------|---|
| 方法 | `POST` |
| 路径 | `/auth/token` |
| 认证 | 无需登录 |
| 状态 | ✅ 已实现 |

> ⚠️ 注意：此接口使用 OAuth2 标准格式，**Content-Type 为 `application/x-www-form-urlencoded`**，不是 JSON。

**请求体**（Form 表单）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | string | ✅ | 用户邮箱（注意：字段名叫 username，实际传邮箱） |
| `password` | string | ✅ | 用户密码 |

**成功响应** `200` `TokenResponse`：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "username": "xiaoming",
  "email": "xiaoming@email.com"
}
```

**错误响应**：

| 状态码 | detail | 说明 |
|--------|--------|------|
| 401 | Incorrect email or password | 邮箱或密码错误 |
| 401 | Inactive user | 账号已被禁用 |

---

## 3. 用户模块（User）

**基础路径**：`/api/v1/users`

### 3.1 获取当前用户信息

| 属性 | 值 |
|------|---|
| 方法 | `GET` |
| 路径 | `/users/me` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**成功响应** `200` `UserResponse`：

```json
{
  "id": 1,
  "username": "xiaoming",
  "email": "xiaoming@email.com",
  "is_active": 1
}
```

---

### 3.2 更新当前用户信息

| 属性 | 值 |
|------|---|
| 方法 | `PUT` |
| 路径 | `/users/me` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**请求体** `UserUpdate`（所有字段可选，只更新提供的字段）：

```json
{
  "username": "new_name",
  "email": "new@email.com",
  "password": "newpassword123"
}
```

**成功响应** `200` `UserResponse`：

```json
{
  "id": 1,
  "username": "new_name",
  "email": "new@email.com",
  "is_active": 1
}
```

---

### 3.3 注销账号

| 属性 | 值 |
|------|---|
| 方法 | `DELETE` |
| 路径 | `/users/me` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

> 此为**软删除**，将 `is_active` 设为 0，不会真正删除数据。

**成功响应** `200`：

```json
{
  "message": "User account deleted successfully"
}
```

---

## 4. 书签模块（Bookmark）

**基础路径**：`/api/v1/bookmarks`

### 4.1 获取书签列表（分页）

| 属性 | 值 |
|------|---|
| 方法 | `GET` |
| 路径 | `/bookmarks` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | ❌ | 1 | 页码（≥1） |
| `page_size` | int | ❌ | 10 | 每页数量（1-100） |
| `category_id` | int | ❌ | null | 按分类 ID 过滤 |
| `tag_ids` | int[] | ❌ | null | 按标签 ID 列表过滤（OR 逻辑） |

**请求示例**：

```
GET /bookmarks?page=1&page_size=20&category_id=3
```

**成功响应** `200` `BookmarkListResponse`：

```json
{
  "total": 48,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "url": "https://developer.mozilla.org",
      "title": "MDN Web Docs",
      "description": "权威的前端开发文档",
      "favicon": null,
      "category_id": 1,
      "tag_ids": [1, 2],
      "click_count": 128,
      "created_at": "2026-03-01T10:00:00",
      "category": {
        "id": 1,
        "user_id": 1,
        "name": "技术"
      },
      "tags": [
        { "id": 1, "name": "前端" },
        { "id": 2, "name": "文档" }
      ]
    }
  ]
}
```

> ⚠️ 注意：响应中的 `tag_ids` 字段来自 `BookmarkBase`，值为标签 ID 数组。`tags` 字段为嵌套的完整标签对象数组。前端展示时优先使用 `tags` 字段。

---

### 4.2 创建书签

| 属性 | 值 |
|------|---|
| 方法 | `POST` |
| 路径 | `/bookmarks` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**请求体** `BookmarkCreate`：

```json
{
  "url": "https://developer.mozilla.org",
  "title": "MDN Web Docs",
  "description": "权威的前端开发文档",
  "favicon": null,
  "category_id": 1,
  "tag_ids": [1, 2]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 书签链接地址 |
| `title` | string | ✅ | 书签标题 |
| `description` | string | ❌ | 描述 |
| `favicon` | string | ❌ | 网站图标 URL |
| `category_id` | int | ❌ | 所属分类 ID（需是当前用户已有的分类） |
| `tag_ids` | int[] | ❌ | 标签 ID 列表（标签必须已存在于全局标签库） |

**成功响应** `200` `BookmarkResponse`（同 4.1 中的单个 item 结构）

**错误响应**：

| 状态码 | detail | 说明 |
|--------|--------|------|
| 404 | Category not found | 分类不存在或不属于当前用户 |
| 404 | Tag not found | 标签不存在（tag_ids 中的 ID 必须已存在） |

---

### 4.3 获取单个书签

| 属性 | 值 |
|------|---|
| 方法 | `GET` |
| 路径 | `/bookmarks/{bookmark_id}` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**成功响应** `200` `BookmarkResponse`

**错误响应**：

| 状态码 | detail | 说明 |
|--------|--------|------|
| 404 | Bookmark not found | 书签不存在或不属于当前用户 |

---

### 4.4 更新书签

| 属性 | 值 |
|------|---|
| 方法 | `PUT` |
| 路径 | `/bookmarks/{bookmark_id}` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**请求体** `BookmarkUpdate`（所有字段可选）：

```json
{
  "title": "新标题",
  "category_id": 2,
  "tag_ids": [3, 4, 5]
}
```

> `tag_ids` 为**全量替换**：传入新列表会替换原有全部标签。传 `null` 表示不更新标签。

**成功响应** `200` `BookmarkResponse`

---

### 4.5 删除书签

| 属性 | 值 |
|------|---|
| 方法 | `DELETE` |
| 路径 | `/bookmarks/{bookmark_id}` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

> 此为**硬删除**，数据将从数据库永久移除。

**成功响应** `200`：

```json
{
  "message": "Bookmark deleted successfully"
}
```

---

### 4.6 增加点击次数

| 属性 | 值 |
|------|---|
| 方法 | `PATCH` |
| 路径 | `/bookmarks/{bookmark_id}/click` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

> 每次调用 `click_count + 1`。前端在用户点击书签打开链接时调用。

**成功响应** `200` `ClickCountResponse`：

```json
{
  "bookmark_id": 1,
  "click_count": 129
}
```

---

## 5. 分类模块（Category）

### 5.1 获取分类列表

| 属性 | 值 |
|------|---|
| 方法 | `GET` |
| 路径 | `/bookmarks/categories/list` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**成功响应** `200` `List[CategoryResponse]`：

```json
[
  { "id": 1, "user_id": 1, "name": "技术" },
  { "id": 2, "user_id": 1, "name": "设计" },
  { "id": 3, "user_id": 1, "name": "工具" }
]
```

---

### 5.2 创建分类

| 属性 | 值 |
|------|---|
| 方法 | `POST` |
| 路径 | `/bookmarks/categories` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**请求体** `CategoryCreate`：

```json
{
  "name": "阅读"
}
```

**成功响应** `200` `CategoryResponse`：

```json
{
  "id": 4,
  "user_id": 1,
  "name": "阅读"
}
```

---

### 5.3 更新分类

| 属性 | 值 |
|------|---|
| 方法 | `PUT` |
| 路径 | `/bookmarks/categories/{category_id}` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**请求体** `CategoryUpdate`：

```json
{
  "name": "新技术"
}
```

**成功响应** `200` `CategoryResponse`

---

### 5.4 删除分类

| 属性 | 值 |
|------|---|
| 方法 | `DELETE` |
| 路径 | `/bookmarks/categories/{category_id}` |
| 认证 | ✅ 需要 Bearer Token |
| 状态 | ✅ 已实现 |

**成功响应** `200`：

```json
{
  "message": "Category deleted successfully"
}
```

---

## 6. 标签模块（Tag）

### 6.1 获取所有标签

| 属性 | 值 |
|------|---|
| 方法 | `GET` |
| 路径 | `/bookmarks/tags/list` |
| 认证 | ❌ 无需登录 |
| 状态 | ✅ 已实现 |

**成功响应** `200` `List[TagResponse]`：

```json
[
  { "id": 1, "name": "前端" },
  { "id": 2, "name": "文档" },
  { "id": 3, "name": "AI" },
  { "id": 4, "name": "Python" }
]
```

> 标签是**全局共享**的，所有用户共用同一标签池。

---

### 6.2 创建标签

| 属性 | 值 |
|------|---|
| 方法 | `POST` |
| 路径 | `/bookmarks/tags` |
| 认证 | ❌ 无需登录 |
| 状态 | ✅ 已实现 |

**请求体** `TagCreate`：

```json
{
  "name": "Rust"
}
```

> **幂等设计**：如果同名标签已存在，直接返回已有标签，不会创建重复项。

**成功响应** `200` `TagResponse`：

```json
{
  "id": 5,
  "name": "Rust"
}
```

---

## 7. 统计模块（Stats）— 待开发

> 以下接口需在后端新增。前端 Phase 3 开发时使用。

**基础路径**：`/api/v1/stats`

### 7.1 获取统计概览

```
GET /stats/overview?start_date=2026-04-01&end_date=2026-04-14
```

**期望响应**：

```json
{
  "total_bookmarks": 128,
  "new_this_period": 5,
  "total_clicks": 342,
  "category_count": 6
}
```

### 7.2 获取点击热力图数据

```
GET /stats/click-heatmap?start_date=2026-03-01&end_date=2026-04-14
```

**期望响应**：

```json
{
  "data": [
    { "date": "2026-04-01", "count": 5 },
    { "date": "2026-04-02", "count": 8 },
    ...
  ]
}
```

### 7.3 获取分类占比

```
GET /stats/category-distribution
```

**期望响应**：

```json
[
  { "category_name": "技术", "count": 45, "percentage": 35.2 },
  { "category_name": "工具", "count": 26, "percentage": 20.3 },
  ...
]
```

### 7.4 获取热门书签 Top N

```
GET /stats/top-bookmarks?limit=10&start_date=2026-04-01&end_date=2026-04-14
```

**期望响应**：

```json
[
  { "id": 1, "title": "MDN", "url": "...", "click_count": 128 },
  { "id": 2, "title": "Dribbble", "url": "...", "click_count": 96 },
  ...
]
```

### 7.5 获取 24 小时时段分布

```
GET /stats/hourly-distribution
```

**期望响应**：

```json
[
  { "hour": 0, "count": 3 },
  { "hour": 1, "count": 1 },
  ...
  { "hour": 23, "count": 5 }
]
```

### 7.6 导出 CSV

```
GET /stats/export-csv?start_date=2026-04-01&end_date=2026-04-14
```

**期望响应**：`text/csv` 格式文件下载

---

## 8. 公开分享模块（Public）— 待开发

> 以下接口需在后端新增。前端 Phase 2 开发时使用。

**基础路径**：`/api/v1/bookmarks`

### 8.1 获取公开书签列表

```
GET /bookmarks/public?page=1&page_size=20&sort=latest
```

**查询参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | int | 页码 |
| `page_size` | int | 每页数量 |
| `sort` | string | 排序方式：`latest`（最新）/ `popular`（热门） |

**期望响应**：同 `BookmarkListResponse`，但包含 `is_shared: true` 的书签。

### 8.2 获取官方精选

```
GET /bookmarks/featured?limit=3
```

**期望响应**：

```json
[
  {
    "id": 1,
    "title": "MDN",
    "url": "...",
    "description": "...",
    "click_count": 2300,
    "editor_note": "前端开发必备文档",
    "featured_at": "2026-04-10"
  }
]
```

### 8.3 获取热门排行

```
GET /bookmarks/top?limit=10
```

**期望响应**：按 `click_count` 降序排列的公开书签列表。

### 8.4 设为公开分享

```
POST /bookmarks/{bookmark_id}/share
```

**期望响应**：将书签标记为 `is_shared=true`。

### 8.5 取消公开分享

```
DELETE /bookmarks/{bookmark_id}/share
```

### 8.6 点赞

```
POST /bookmarks/{bookmark_id}/like
```

**期望响应**：

```json
{
  "bookmark_id": 1,
  "like_count": 57
}
```

> 需要登录，同一用户对同一书签只能点赞一次。

---

## 9. 管理员模块（Admin）— 待开发

> 以下接口需在后端新增。需后端先实现 `role` 字段（`user` / `admin`）。

**基础路径**：`/api/v1/admin`

### 9.1 获取待审核分享列表

```
GET /admin/shares/pending?page=1&page_size=20&status=pending
```

**期望响应**：

```json
{
  "total": 15,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 101,
      "user": { "id": 1, "username": "小明" },
      "bookmark": { "title": "Vue 3 文档", "url": "https://vuejs.org" },
      "submitted_at": "2026-04-14T10:30:00",
      "status": "pending"
    }
  ]
}
```

### 9.2 通过审核

```
PUT /admin/shares/{share_id}/approve
```

### 9.3 驳回审核

```
PUT /admin/shares/{share_id}/reject
```

**请求体**：

```json
{
  "reason": "内容不符合社区规范"
}
```

### 9.4 获取黑名单列表

```
GET /admin/blacklist
```

### 9.5 新增黑名单规则

```
POST /admin/blacklist
```

**请求体**：

```json
{
  "type": "domain",
  "pattern": "xxx-bad-site.com",
  "reason": "违规内容"
}
```

或正则匹配：

```json
{
  "type": "regex",
  "pattern": ".*illegal.*",
  "reason": "关键词过滤"
}
```

### 9.6 删除黑名单规则

```
DELETE /admin/blacklist/{rule_id}
```

### 9.7 获取官方推荐管理列表

```
GET /admin/official
```

### 9.8 更新推荐状态

```
PUT /admin/official/{bookmark_id}
```

**请求体**：

```json
{
  "is_featured": true,
  "weight": 10,
  "editor_note": "前端开发必备文档"
}
```

### 9.9 获取全局统计

```
GET /admin/stats
```

**期望响应**：

```json
{
  "total_users": 128,
  "total_bookmarks": 5420,
  "total_shared": 342,
  "active_today": 45,
  "violation_trend": [
    { "date": "2026-04-01", "count": 2 },
    ...
  ],
  "top_categories": [
    { "name": "技术", "count": 2100 },
    ...
  ]
}
```

---

## 10. 前端 Axios 封装规范

### 10.1 实例创建

```typescript
// src/api/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
})
```

### 10.2 请求拦截器

```typescript
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)
```

### 10.3 响应拦截器

```typescript
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const { status, data } = error.response || {}

    switch (status) {
      case 401:
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        router.push({ path: '/', query: { login: '1' } })
        ElMessage.warning('登录已过期，请重新登录')
        break
      case 403:
        router.push('/403')
        ElMessage.error('无权访问该资源')
        break
      case 404:
        ElMessage.error(data?.detail || '请求的资源不存在')
        break
      case 409:
        ElMessage.warning(data?.detail || '数据冲突')
        break
      case 422:
        // 字段校验失败
        const detail = data?.detail
        if (Array.isArray(detail)) {
          ElMessage.error(detail.map((d: any) => d.msg).join('；'))
        } else {
          ElMessage.error(detail || '参数校验失败')
        }
        break
      default:
        ElMessage.error(data?.detail || '网络异常，请稍后重试')
    }

    return Promise.reject(error)
  }
)

export default request
```

### 10.4 登录接口特殊处理

登录使用 `application/x-www-form-urlencoded` 格式，需要用 `URLSearchParams` 构建请求体：

```typescript
// src/api/auth.ts
import request from './request'
import qs from 'qs'  // 或使用 URLSearchParams

export const login = (email: string, password: string) => {
  return request.post('/auth/token',
    new URLSearchParams({
      username: email,  // 注意：后端 OAuth2 表单字段名叫 username
      password: password,
    }),
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }
  )
}

export const register = (data: { username: string; email: string; password: string }) => {
  return request.post('/auth/register', data)
}
```

---

## 11. 前端 TypeScript 类型定义

```typescript
// src/types/index.ts

// ============ 用户 ============

export interface User {
  id: number
  username: string
  email: string
  is_active: number
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserUpdate {
  username?: string
  email?: string
  password?: string
}

// ============ Token ============

export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
  email: string
}

// ============ 书签 ============

export interface Bookmark {
  id: number
  user_id: number
  url: string
  title: string
  description: string | null
  favicon: string | null
  click_count: number
  created_at: string
  category: Category | null
  tags: Tag[]
}

export interface BookmarkCreate {
  url: string
  title: string
  description?: string
  favicon?: string
  category_id?: number
  tag_ids?: number[]
}

export interface BookmarkUpdate {
  url?: string
  title?: string
  description?: string
  favicon?: string
  category_id?: number
  tag_ids?: number[] | null
}

export interface BookmarkListResponse {
  total: number
  page: number
  page_size: number
  items: Bookmark[]
}

export interface ClickCountResponse {
  bookmark_id: number
  click_count: number
}

// ============ 分类 ============

export interface Category {
  id: number
  user_id: number
  name: string
}

export interface CategoryCreate {
  name: string
}

export interface CategoryUpdate {
  name?: string
}

// ============ 标签 ============

export interface Tag {
  id: number
  name: string
}

export interface TagCreate {
  name: string
}

// ============ 统计（待后端实现）============

export interface StatsOverview {
  total_bookmarks: number
  new_this_period: number
  total_clicks: number
  category_count: number
}

export interface HeatmapData {
  date: string
  count: number
}

export interface CategoryDistribution {
  category_name: string
  count: number
  percentage: number
}

// ============ 公开分享（待后端实现）============

export interface FeaturedBookmark {
  id: number
  title: string
  url: string
  description: string | null
  click_count: number
  editor_note?: string
  featured_at: string
}

// ============ 管理员（待后端实现）============

export enum AuditStatus {
  Pending = 'pending',
  Approved = 'approved',
  Rejected = 'rejected',
}

export interface AuditItem {
  id: number
  user: { id: number; username: string }
  bookmark: { title: string; url: string }
  submitted_at: string
  status: AuditStatus
}

export interface BlacklistRule {
  id: number
  type: 'domain' | 'regex'
  pattern: string
  reason: string
  created_at: string
}

export interface AdminStats {
  total_users: number
  total_bookmarks: number
  total_shared: number
  active_today: number
}
```

---

## 12. 错误码对照表

| HTTP 状态码 | 含义 | 前端处理方式 |
|-------------|------|-------------|
| 200 | 成功 | 正常使用 response.data |
| 401 | 未认证/Token 过期 | 清除本地 token，跳转登录页 |
| 403 | 无权限 | 跳转 403 页面 |
| 404 | 资源不存在 | Toast 提示 + 可选跳转 |
| 409 | 数据冲突（重复） | Toast 警告，展示 detail 信息 |
| 422 | 请求参数校验失败 | 解析 `detail` 数组，展示具体字段错误 |
| 500 | 服务器内部错误 | Toast 提示"服务器异常" |

---

## 13. 当前接口实现状态汇总

| 模块 | 接口 | 状态 | 优先级 |
|------|------|------|--------|
| 认证 | POST `/auth/register` | ✅ 已实现 | P0 |
| 认证 | POST `/auth/token` | ✅ 已实现 | P0 |
| 用户 | GET `/users/me` | ✅ 已实现 | P0 |
| 用户 | PUT `/users/me` | ✅ 已实现 | P0 |
| 用户 | DELETE `/users/me` | ✅ 已实现 | P0 |
| 书签 | GET `/bookmarks` | ✅ 已实现 | P0 |
| 书签 | POST `/bookmarks` | ✅ 已实现 | P0 |
| 书签 | GET `/bookmarks/{id}` | ✅ 已实现 | P1 |
| 书签 | PUT `/bookmarks/{id}` | ✅ 已实现 | P1 |
| 书签 | DELETE `/bookmarks/{id}` | ✅ 已实现 | P1 |
| 书签 | PATCH `/bookmarks/{id}/click` | ✅ 已实现 | P1 |
| 分类 | GET `/bookmarks/categories/list` | ✅ 已实现 | P0 |
| 分类 | POST `/bookmarks/categories` | ✅ 已实现 | P0 |
| 分类 | PUT `/bookmarks/categories/{id}` | ✅ 已实现 | P1 |
| 分类 | DELETE `/bookmarks/categories/{id}` | ✅ 已实现 | P1 |
| 标签 | GET `/bookmarks/tags/list` | ✅ 已实现 | P0 |
| 标签 | POST `/bookmarks/tags` | ✅ 已实现 | P1 |
| 统计 | GET `/stats/overview` | 🔴 待开发 | P1 |
| 统计 | GET `/stats/click-heatmap` | 🔴 待开发 | P2 |
| 统计 | GET `/stats/category-distribution` | 🔴 待开发 | P2 |
| 统计 | GET `/stats/top-bookmarks` | 🔴 待开发 | P2 |
| 统计 | GET `/stats/hourly-distribution` | 🔴 待开发 | P2 |
| 统计 | GET `/stats/export-csv` | 🔴 待开发 | P2 |
| 公开 | GET `/bookmarks/public` | 🔴 待开发 | P1 |
| 公开 | GET `/bookmarks/featured` | 🔴 待开发 | P1 |
| 公开 | GET `/bookmarks/top` | 🔴 待开发 | P1 |
| 公开 | POST `/bookmarks/{id}/share` | 🔴 待开发 | P1 |
| 公开 | POST `/bookmarks/{id}/like` | 🔴 待开发 | P1 |
| 管理 | GET `/admin/shares/pending` | 🔴 待开发 | P2 |
| 管理 | PUT `/admin/shares/{id}/approve` | 🔴 待开发 | P2 |
| 管理 | PUT `/admin/shares/{id}/reject` | 🔴 待开发 | P2 |
| 管理 | CRUD `/admin/blacklist` | 🔴 待开发 | P2 |
| 管理 | CRUD `/admin/official` | 🔴 待开发 | P2 |
| 管理 | GET `/admin/stats` | 🔴 待开发 | P2 |

> P0 = Phase 1 必需（当前后端已全部实现）
> P1 = Phase 2 需要
> P2 = Phase 3 需要

---

## 14. 后端待扩展字段建议

### 14.1 User 表新增字段

```python
role = Column(Enum('user', 'admin'), default='user')  # 角色
avatar = Column(String(500), nullable=True)            # 头像 URL
bio = Column(Text, nullable=True)                      # 个人简介
created_at = Column(DateTime, default=utcnow)          # 注册时间
```

### 14.2 Bookmark 表新增字段

```python
is_shared = Column(Boolean, default=False)             # 是否公开分享
shared_at = Column(DateTime, nullable=True)            # 公开时间
is_featured = Column(Boolean, default=False)           # 是否官方推荐
sort_order = Column(Integer, default=0)               # 排序权重
```

### 14.3 新增表

| 表名 | 说明 |
|------|------|
| `likes` | 点赞记录表（user_id + bookmark_id 联合主键） |
| `audit_records` | 审核记录表（share_id, status, reason, admin_id, created_at） |
| `blacklist_rules` | 黑名单规则表（type, pattern, reason, created_at） |
| `click_logs` | 点击日志表（bookmark_id, user_id, clicked_at, hour）— 用于统计 |
