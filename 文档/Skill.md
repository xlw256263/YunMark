深度思考
```用户要求创建一份详细的全栈开发 Skill 文档，基于"云藏智能收藏夹"项目经验，需要按照要求的8个章节结构输出，包含系统架构、后端模块、前端模块、问题解决方案、设计理念、可复用代码等内容。
```
# 云藏智能收藏夹 — 全栈开发 Skill 文档

## 1. Skill 元信息

| 项目 | 内容 |
|------|------|
| **Skill 名称** | `fullstack-bookmark-platform-builder` |
| **适用场景** | 个人书签管理、团队知识库、资源导航站、内容聚合平台、社区分享系统 |
| **技术栈** | 后端：FastAPI + JWT + MySQL + Redis + Celery<br>前端：Vue3 + Vite + TypeScript + Pinia + Element Plus |
| **前置要求** | Python 3.9+ 基础、Vue 3 Composition API 基础、Docker 基础、SQL 基础 |
| **预估交付时间** | Phase 1（核心功能）2-3 天<br>Phase 2（缓存+异步）1-2 天<br>Phase 3（高级特性）2-3 天 |

---

## 2. 系统架构全景图

```mermaid
graph TB
    subgraph 客户端层
        Web[Web 浏览器<br>Vue3 SPA]
        Plugin[浏览器插件<br>快速收藏]
    end

    subgraph 网关层
        Nginx[Nginx 反向代理<br>静态资源 + 负载均衡]
    end

    subgraph 应用层
        API[FastAPI 后端<br>RESTful + GraphQL]
        Worker[Celery Worker<br>异步任务]
    end

    subgraph 数据层
        MySQL[(MySQL 8.0<br>主数据存储)]
        Redis[(Redis 7.x<br>缓存 + 队列 + 限流)]
    end

    subgraph 外部服务
        LLM[LLM 服务<br>Ollama / Gemini]
        Mail[邮件服务<br>注册验证]
    end

    Web --> Nginx
    Plugin --> Nginx
    Nginx --> API
    API --> MySQL
    API --> Redis
    API -.->|异步任务| Worker
    Worker --> Redis
    Worker --> MySQL
    Worker --> LLM
    API --> Mail
```


**核心设计理念**：
- **分层架构**：前端 SPA → Nginx → FastAPI → 数据库/缓存
- **异步解耦**：耗时操作（链接检测、LLM 标签生成）通过 Celery 异步处理
- **缓存优先**：热点数据（标签列表、用户信息）走 Redis 缓存

---

## 3. 后端核心模块提炼

### 3.1 认证与授权

**问题**：如何安全地实现用户认证，并区分普通用户和管理员？

**解决方案**：使用 JWT + OAuth2PasswordBearer + 角色扩展

```python
# app/core/security.py
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status

SECRET_KEY = "your-secret-key"  # 生产环境使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)
```


**为什么这样做**：
- `OAuth2PasswordBearer` 是 FastAPI 内置的认证方案，自动处理 `Authorization: Bearer <token>` 头部
- JWT 无状态，适合前后端分离架构
- 短期过期（30 分钟）降低 Token 泄露风险

**管理员角色扩展**：
```python
# 在 JWT payload 中携带角色
token_data = {
    "sub": user.email,
    "user_id": user.id,
    "role": user.role  # "user" 或 "admin"
}
access_token = create_access_token(token_data)
```


### 3.2 数据模型设计

**问题**：标签和分类的关系如何设计才能既灵活又可管理？

**核心决策**：
- **标签全局化**：由管理员统一维护，所有用户共享同一套标签体系
- **分类私有化**：每个用户可创建自己的分类，用于个人组织管理
- **书签关系**：1 个书签 → 1 个分类（可选） + N 个标签

**原因**：
- 标签全局化便于社区内容聚合和筛选（如所有人搜 "AI" 标签都能看到相关书签）
- 分类私有化满足用户个性化组织需求（不同人的"技术"分类可能内容不同）

```python
# app/models/bookmark.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# 书签-标签关联表（多对多）
bookmark_tag = Table(
    'bookmark_tag',
    Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    url = Column(String(2048), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    favicon = Column(String(500), nullable=True)
    click_count = Column(Integer, default=0)
    
    # 关系
    user = relationship("User", back_populates="bookmarks")
    category = relationship("Category", back_populates="bookmarks")
    tags = relationship("Tag", secondary=bookmark_tag, back_populates="bookmarks")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    
    user = relationship("User", back_populates="categories")
    bookmarks = relationship("Bookmark", back_populates="category")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # 管理员创建
    
    bookmarks = relationship("Bookmark", secondary=bookmark_tag, back_populates="tags")
```


### 3.3 RESTful API 设计

**书签 CRUD 规范**：

```python
# app/api/v1/bookmarks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

router = APIRouter()

@router.get("/", response_model=BookmarkListResponse)
def get_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category_id: Optional[int] = None,
    tag_ids: Optional[List[int]] = None
):
    """获取书签列表（支持分页和筛选）"""
    # Service 层处理业务逻辑
    return bookmark_service.get_user_bookmarks(
        db, current_user.id, page, page_size, category_id, tag_ids
    )

@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(
    bookmark_data: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建书签"""
    return bookmark_service.create_bookmark(db, current_user.id, bookmark_data)
```


**点击计数优化**：
```python
@router.patch("/{bookmark_id}/click", status_code=status.HTTP_200_OK)
def increment_click(bookmark_id: int, db: Session = Depends(get_db)):
    """增加点击次数（异步写入，不阻塞）"""
    # 使用 Redis 原子操作先累加，定期同步到 MySQL
    redis_client.incr(f"bookmark:click:{bookmark_id}")
    # 异步任务同步到数据库
    celery_task_sync_clicks.delay(bookmark_id)
    return {"message": "Click recorded"}
```


### 3.4 缓存策略

**问题**：高频访问的数据（如标签列表、用户信息）如何减少数据库压力？

**解决方案**：Cache-Aside 模式

```python
# app/utils/cache.py
import json
from typing import Optional, Any
from app.db.redis import redis_client

def cache_get(key: str) -> Optional[Any]:
    """从 Redis 获取缓存"""
    data = redis_client.get(key)
    return json.loads(data) if data else None

def cache_set(key: str, value: Any, expire: int = 3600):
    """设置缓存（默认 1 小时）"""
    redis_client.setex(key, expire, json.dumps(value))

def cache_delete(key: str):
    """删除缓存"""
    redis_client.delete(key)
```


**使用示例**：
```python
# 获取标签列表（带缓存）
def get_tags(db: Session) -> List[Tag]:
    cache_key = "tags:all"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    tags = db.query(Tag).all()
    tag_list = [TagResponse.from_orm(t).dict() for t in tags]
    cache_set(cache_key, tag_list, expire=7200)  # 2 小时缓存
    return tag_list

# 更新标签后清除缓存
def create_tag(db: Session, tag_data: TagCreate):
    new_tag = Tag(**tag_data.dict())
    db.add(new_tag)
    db.commit()
    cache_delete("tags:all")  # 清除缓存
    return new_tag
```


### 3.5 异步任务

**问题**：如何检测书签链接有效性而不阻塞 API 响应？

**解决方案**：Celery + Redis

```python
# app/tasks/link_checker.py
from celery import Celery
import requests
from app.db.database import SessionLocal
from app.models.bookmark import Bookmark

celery_app = Celery("tasks", broker="redis://localhost:6379/1")

@celery_app.task
def check_bookmark_link(bookmark_id: int):
    """异步检测书签链接是否有效"""
    db = SessionLocal()
    try:
        bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        if not bookmark:
            return {"status": "not_found"}
        
        try:
            response = requests.head(bookmark.url, timeout=5)
            is_valid = response.status_code < 400
            bookmark.is_valid = is_valid
            db.commit()
            return {"status": "checked", "valid": is_valid}
        except Exception as e:
            bookmark.is_valid = False
            db.commit()
            return {"status": "error", "error": str(e)}
    finally:
        db.close()

# 在创建书签时调用
@router.post("/", response_model=BookmarkResponse)
def create_bookmark(bookmark_data: BookmarkCreate, ...):
    new_bookmark = bookmark_service.create(...)
    check_bookmark_link.delay(new_bookmark.id)  # 异步调用
    return new_bookmark
```


### 3.6 LLM 智能标签推荐

**问题**：如何根据书签标题和描述自动推荐标签？

**解决方案**：LangChain + Prompt Engineering

```python
# app/services/llm_tag_service.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import json

PROMPT = """
你是一个书签分类专家。根据以下书签信息，从给定的标签列表中选择最合适的 3-5 个标签。

书签标题：{title}
书签描述：{description}
可用标签：{available_tags}

要求：
1. 只从可用标签中选择，不要创造新标签
2. 返回 JSON 格式：{"tag_ids": [1, 3, 5]}
3. 最多选择 5 个标签
"""

def recommend_tags(title: str, description: str, available_tags: List[Tag]) -> List[int]:
    """使用 LLM 推荐标签"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    prompt = PromptTemplate(
        input_variables=["title", "description", "available_tags"],
        template=PROMPT
    )
    
    response = llm.predict(
        title=title,
        description=description or "无描述",
        available_tags=", ".join([f"{t.id}:{t.name}" for t in available_tags])
    )
    
    try:
        result = json.loads(response)
        return result.get("tag_ids", [])
    except json.JSONDecodeError:
        # 格式错误时返回空列表
        return []
```


---

## 4. 前端核心模块提炼

### 4.1 项目初始化

```bash
# 1. 创建 Vite + Vue3 + TypeScript 项目
npm create vite@latest front -- --template vue-ts
cd front

# 2. 安装依赖
npm install vue-router pinia axios element-plus @element-plus/icons-vue

# 3. 配置 vite.config.ts
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000'  // 代理后端 API
    }
  }
})
```


### 4.2 路由守卫

```typescript
// src/router/guards.ts
import { RouteLocationNormalized, NavigationGuardNext } from 'vue-router'
import { useUserStore } from '@/stores/user'

export function authGuard(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
  const userStore = useUserStore()
  const authRoutes = ['/my', '/stats', '/profile']
  
  if (authRoutes.some(r => to.path.startsWith(r)) && !userStore.isLoggedIn) {
    // 未登录，跳转到首页并弹出登录框
    next({ path: '/', query: { login: '1' } })
  } else {
    next()
  }
}

export function adminGuard(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
  const userStore = useUserStore()
  
  if (to.path.startsWith('/admin') && !userStore.isAdmin) {
    next({ path: '/403' })  // 无权限页面
  } else {
    next()
  }
}
```


### 4.3 状态管理

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref<User | null>(null)
  
  const isLoggedIn = computed(() => !!accessToken.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
  
  function setUserInfo(token: string, user: User) {
    accessToken.value = token
    userInfo.value = user
    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(user))
  }
  
  function logout() {
    accessToken.value = ''
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }
  
  function restoreFromStorage() {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    if (token && userStr) {
      accessToken.value = token
      userInfo.value = JSON.parse(userStr)
    }
  }
  
  return { accessToken, userInfo, isLoggedIn, isAdmin, setUserInfo, logout, restoreFromStorage }
})
```


### 4.4 标签选择组件（核心）

**问题**：如何限制用户只能从管理员定义的标签库中选择？

```vue
<!-- src/components/TagSelector.vue -->
<template>
  <el-select
    v-model="selectedTags"
    multiple
    filterable
    placeholder="选择标签（仅管理员标签库）"
    @change="handleTagChange"
  >
    <el-option
      v-for="tag in adminTags"
      :key="tag.id"
      :label="tag.name"
      :value="tag.id"
    >
      <span>{{ tag.name }}</span>
      <span class="tag-usage">({{ tag.usage_count }})</span>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBookmarkStore } from '@/stores/bookmark'

const props = defineProps<{
  modelValue: number[]
}>()

const emit = defineEmits(['update:modelValue'])
const bookmarkStore = useBookmarkStore()

const selectedTags = ref(props.modelValue)
const adminTags = computed(() => bookmarkStore.tags)  // 标签列表来自 Store（后端接口）

const handleTagChange = (tags: number[]) => {
  selectedTags.value = tags
  emit('update:modelValue', tags)
}

onMounted(async () => {
  // 加载管理员标签库
  if (adminTags.value.length === 0) {
    await bookmarkStore.fetchTags()
  }
})
</script>
```


**为什么这样做**：
- `multiple` 属性支持多选
- 选项列表来自后端接口，用户无法自定义输入（与 `allow-create` 模式区分）
- 显示使用次数帮助用户了解标签热度

### 4.5 统计图表集成

```typescript
// src/views/StatsView.vue
import * as echarts from 'echarts'
import { onMounted, ref } from 'vue'

const chartRef = ref<HTMLElement>()

onMounted(async () => {
  const chart = echarts.init(chartRef.value)
  
  const statsData = await fetchStats()
  
  const option = {
    title: { text: '分类占比' },
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '50%',
      data: statsData.categories.map(c => ({
        value: c.count,
        name: c.name
      }))
    }]
  }
  
  chart.setOption(option)
})
```


---

## 5. 问题与解决方案

### 问题 1：Pinia Store 方法与 API 导入命名冲突导致无限递归

**现象**：调用 `createCategory` 时报 `RangeError: Maximum call stack size exceeded`

**原因**：Store 方法名与 API 函数名相同，导致自我调用

**解决方案**：导入时使用别名
```typescript
import { createCategory as createCategoryApi } from '@/api/category'

async function createCategory(data: CategoryCreate) {
  const newCategory = await createCategoryApi(data)  // 明确调用 API
  categories.value.push(newCategory)
}
```


### 问题 2：Axios 全局 Content-Type 覆盖导致登录失败

**现象**：登录接口返回 401，后端无法解析表单数据

**原因**：全局设置了 `Content-Type: application/json`，但 OAuth2 登录需要 `application/x-www-form-urlencoded`

**解决方案**：移除默认 Content-Type，让各请求自己指定
```typescript
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  // 不设置默认 Content-Type
})

// 登录时手动指定
export function login(email: string, password: string) {
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  
  return request.post('/auth/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}
```


### 问题 3：Redis 缓存与数据库一致性

**问题**：更新数据后缓存未失效，导致读到旧数据

**解决方案**：写操作后主动清除缓存
```python
def update_bookmark(db: Session, bookmark_id: int, data: BookmarkUpdate):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(bookmark, key, value)
    db.commit()
    
    # 清除缓存
    cache_delete(f"bookmark:{bookmark_id}")
    cache_delete(f"user:{bookmark.user_id}:bookmarks")  # 清除用户列表缓存
    
    return bookmark
```


### 问题 4：LLM 生成标签格式不稳定

**问题**：LLM 有时返回代码块、有时返回纯 JSON，解析失败

**解决方案**：Prompt 中强制要求 JSON 格式 + 容错处理
```python
PROMPT = """
只返回 JSON，不要其他内容：
{"tag_ids": [1, 3, 5]}
"""

def recommend_tags(...) -> List[int]:
    response = llm.predict(...)
    
    # 提取 JSON（处理可能包含的 Markdown 代码块）
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            return result.get("tag_ids", [])
        except json.JSONDecodeError:
            pass
    
    return []  # 失败时返回空列表，不影响主流程
```


### 问题 5：Docker Compose 多服务启动顺序

**问题**：FastAPI 启动时 Redis/MySQL 还没准备好，导致连接失败

**解决方案**：使用 `depends_on` + 健康检查
```yaml
# docker-compose.yml
services:
  mysql:
    image: mysql:8.0
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  api:
    build: ./back
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000
      "
```


### 问题 6：Element Plus 输入框聚焦时出现内边框

**问题**：默认 `box-shadow: inset` 导致视觉不统一

**解决方案**：全局样式覆盖
```css
.el-input__wrapper {
  box-shadow: none !important;
  border: 1px solid #E2E8F0;
}

.el-input__wrapper.is-focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;  /* 外发光 */
}
```


---

## 6. 设计理念与原则

### 关注点分离
- **后端**：Router（路由）→ Service（业务逻辑）→ Model（数据模型）
- **前端**：组件（UI）→ Store（状态）→ API（数据层）
- **好处**：各司其职，易于测试和维护

### 约定优于配置
- FastAPI 的依赖注入（`Depends`）自动处理认证、数据库会话
- Pydantic 模型自动验证请求数据
- 减少样板代码，提升开发效率

### 可扩展性设计
- 标签体系设计为管理员可动态添加，为未来多租户预留
- 分类私有化支持用户个性化组织
- 插件化架构（如浏览器插件快速收藏）

### 用户体验优先
- 骨架屏加载过渡
- 搜索防抖 300ms
- 乐观更新（先更新 UI，再同步后端）
- 空状态插画 + 引导按钮

### 安全合规
- JWT 短期过期（30 分钟）
- 密码 BCrypt 加密存储
- 黑名单正则匹配（URL 过滤）
- 审核流（公开内容需管理员审核）

---

## 7. 可复用代码片段

### FastAPI JWT 中间件
```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user
```


### Vue3 Axios 拦截器
```typescript
// src/api/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
})

// 请求拦截：注入 JWT
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
request.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      router.push({ path: '/', query: { login: '1' } })
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(err.response?.data?.detail || '网络异常')
    }
    return Promise.reject(err)
  }
)

export default request
```


### Docker Compose 完整配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: ./back
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
      "

  worker:
    build: ./back
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - mysql
    command: celery -A app.tasks worker --loglevel=info

  frontend:
    build: ./front
    ports:
      - "3000:80"
    depends_on:
      - api

volumes:
  mysql_data:
```


---

## 8. 总结与改进方向

### 技术亮点
✅ 完整的认证体系（JWT + OAuth2 + 角色权限）  
✅ 合理的标签/分类关系设计（全局 vs 私有）  
✅ 缓存 + 异步任务提升性能  
✅ LLM 智能标签推荐  
✅ 容器化部署（一键启动全栈服务）  

### 未来可迭代方向
- **全文搜索**：集成 Elasticsearch 实现书签内容搜索
- **浏览器插件**：Chrome/Edge 插件，一键收藏当前网页
- **移动端适配**：响应式设计或开发移动端 App
- **社交功能**：收藏分享、点赞、评论、关注
- **数据导出**：支持导出为 HTML/JSON/CSV 格式
- **多租户**：支持团队协作，多人共享书签库

### 适用场景扩展
本 Skill 不仅适用于书签管理系统，还可复用于：
- 团队知识库（标签分类 + 权限控制）
- 资源导航站（公开分享 + 审核流）
- 内容聚合平台（LLM 自动分类 + 推荐）
- 个人笔记系统（Markdown + 标签管理）

---

**文档版本**：v1.0  
**最后更新**：2026-04-15  
**适用项目**：云藏智能收藏夹（FastAPI + Vue3）