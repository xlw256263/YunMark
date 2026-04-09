# Vue 3 前端项目从零搭建指南

> **目标**: 搭建一个企业级 Vue 3 前端项目，完整对接 FastAPI 后端（用户注册/登录/信息管理）
>
> **技术栈**: Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus + Axios
>
> **后端接口概览**:
> | 接口 | 方法 | 说明 |
> |---|---|---|
> | `/api/v1/auth/register` | POST | 用户注册 |
> | `/api/v1/auth/token` | POST | 登录获取JWT（OAuth2 form） |
> | `/api/v1/users/me` | GET | 获取当前用户信息（需Bearer Token） |
> | `/api/v1/users/me` | PUT | 更新当前用户信息（需Bearer Token） |
> | `/api/v1/users/me` | DELETE | 删除当前用户（需Bearer Token） |

---

## 第一步：创建 Vue 3 项目

在命令行中执行（注意：Windows 下建议使用 PowerShell 或 Git Bash）：

```bash
# 进入你想存放前端代码的目录，例如与后端同级
cd C:\Users\shumeng\Desktop\求职\2026\FastAPI_demo\

# 使用 Vite 创建 Vue + TypeScript 项目
# 项目名: frontend（或你喜欢的名字）
npm create vite@latest frontend -- --template vue-ts

# 进入项目目录
cd frontend

# 安装基础依赖
npm install
```

> **解释**: `vue-ts` 模板会自动生成一个包含 Vue 3 + TypeScript + Vite 的基础项目结构，
> 比手动创建所有文件快得多，且配置已经过社区验证。

---

## 第二步：安装核心依赖

```bash
# --- 路由管理 ---
npm install vue-router@4

# --- 状态管理 (Pinia 是 Vuex 的下一代替代品) ---
npm install pinia

# --- HTTP 请求库 ---
npm install axios

# --- UI 组件库 (Element Plus，企业级后台常用) ---
npm install element-plus
npm install @element-plus/icons-vue

# --- OAuth2 form 编码 ---
npm install qs
npm install -D @types/qs

# --- 开发工具依赖 ---
npm install -D @types/node
```

> **为什么选这些**:
> - `vue-router`: Vue 官方路由，实现页面跳转和路由守卫（如登录拦截）
> - `pinia`: Vue 官方推荐的状态管理库，API 简洁，完美支持 TypeScript
> - `axios`: 最流行的 HTTP 客户端，支持拦截器（自动附加 token、统一错误处理）
> - `element-plus`: 成熟的组件库，提供表单、表格、弹窗等现成组件
> - `qs`: 将对象编码为 `application/x-www-form-urlencoded` 格式（登录接口需要）

---

## 第三步：创建企业级目录结构

删除 Vite 模板生成的 `src/components/HelloWorld.vue`，然后按照以下结构创建文件：

```
frontend/
├── src/
│   ├── api/                         # 所有后端 API 调用集中在这里
│   │   ├── auth.ts                  # 认证相关接口（登录、注册）
│   │   └── user.ts                  # 用户相关接口（获取/更新/删除个人信息）
│   ├── layouts/                     # 页面布局组件
│   │   └── DefaultLayout.vue        # 默认布局（导航栏 + 内容区）
│   ├── router/                      # 路由配置
│   │   └── index.ts                 # 路由定义 + 导航守卫
│   ├── stores/                      # Pinia 状态管理
│   │   └── user.ts                  # 用户状态（token、用户信息）
│   ├── types/                       # TypeScript 类型定义
│   │   └── user.ts                  # 用户相关类型和接口
│   ├── utils/                       # 工具函数
│   │   └── request.ts               # Axios 封装（拦截器、统一错误处理）
│   ├── views/                       # 页面级组件（每个文件对应一个路由页面）
│   │   ├── HomeView.vue             # 首页
│   │   ├── LoginView.vue            # 登录页
│   │   ├── RegisterView.vue         # 注册页
│   │   └── ProfileView.vue          # 个人信息页
│   ├── App.vue                      # 根组件
│   └── main.ts                      # 应用入口
├── vite.config.ts                   # Vite 配置（含代理）
└── tsconfig.json                    # TypeScript 配置
```

---

## 第四步：编写核心代码

按依赖顺序编写——**先写底层（类型、工具），再写上层（页面）**。

### 4.1 类型定义 `src/types/user.ts`

```typescript
/**
 * 用户相关 TypeScript 类型定义
 * 这些类型与后端 Pydantic Schema 一一对应
 */

/** 注册时提交的数据 —— 对应后端 UserCreate Schema */
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

/** 登录时提交的数据 —— 对应后端 OAuth2PasswordRequestForm */
export interface LoginRequest {
  username: string   // 注意：OAuth2 form 标准要求字段名为 username（实际传邮箱）
  password: string
}

/** 更新用户信息 —— 对应后端 UserUpdate Schema */
export interface UpdateUserRequest {
  username?: string
  email?: string
  password?: string
}

/** 后端返回的用户信息 —— 对应后端 UserResponse Schema */
export interface UserInfo {
  id: number
  username: string
  email: string
  is_active: number  // 1=正常，0=禁用
}

/** Token 响应 —— 对应后端 TokenResponse Schema */
export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
  email: string
}

/** 前端登录表单 —— 用户输入的数据结构 */
export interface LoginForm {
  email: string   // 用户输入邮箱
  password: string
}

/** 前端注册表单 */
export interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string  // 前端独有的确认密码字段
}
```

### 4.2 Axios 封装 `src/utils/request.ts`

```typescript
/**
 * Axios 请求封装 —— 企业级项目核心基础设施
 *
 * 职责：
 * 1. 请求拦截器：自动从 localStorage 读取 JWT Token 并附加到请求头
 * 2. 响应拦截器：统一处理 HTTP 错误（401 跳登录、409 提示冲突等）
 *
 * 好处：组件里不用重复写 token 附加和错误处理逻辑
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

// ===================== 创建 Axios 实例 =====================

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',   // API 基础路径，开发环境通过 Vite 代理转发
  timeout: 10000,       // 超时时间 10 秒
})

// ===================== 请求拦截器 =====================

service.interceptors.request.use(
  (config) => {
    // 自动附加 JWT Token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求配置有误:', error)
    return Promise.reject(error)
  }
)

// ===================== 响应拦截器 =====================

service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 请求成功，直接返回 data（调用方不需要写 response.data）
    return response.data
  },
  (error) => {
    const { response } = error

    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('access_token')
          localStorage.removeItem('user_info')
          window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 409:
          // FastAPI 的 409 错误在 detail 字段
          ElMessage.warning(response.data?.detail || '资源已存在')
          break
        case 422:
          // FastAPI 参数校验错误
          const detail = response.data?.detail
          if (Array.isArray(detail)) {
            ElMessage.warning(detail[0]?.msg || '参数格式错误')
          } else {
            ElMessage.warning(detail || '参数格式错误')
          }
          break
        case 500:
          ElMessage.error('服务器异常')
          break
        default:
          ElMessage.error(response.data?.detail || `请求失败 (${response.status})`)
      }
    } else {
      // 请求没发出去（断网、超时、跨域配置错误）
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时')
      } else {
        ElMessage.error('网络连接异常')
      }
    }

    return Promise.reject(error)
  }
)

export default service
```

### 4.3 API 接口层

#### `src/api/auth.ts`

```typescript
/**
 * 认证 API：登录、注册
 * 对应后端：POST /auth/token, POST /auth/register
 */

import request from '@/utils/request'
import Qs from 'qs'
import type { LoginRequest, RegisterRequest, TokenResponse, UserInfo } from '@/types/user'

/**
 * 用户登录
 *
 * 注意：后端 /auth/token 使用 OAuth2PasswordRequestForm，
 * 只能解析 application/x-www-form-urlencoded 格式
 * 所以需要 Qs.stringify 将 { username, password } 编码为 "username=xxx&password=xxx"
 */
export function login(data: LoginRequest): Promise<TokenResponse> {
  return request.post('/auth/token', Qs.stringify(data), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

/**
 * 用户注册
 * 后端用 Pydantic UserCreate 解析 JSON body
 */
export function register(data: RegisterRequest): Promise<UserInfo> {
  return request.post('/auth/register', data)
}
```

#### `src/api/user.ts`

```typescript
/**
 * 用户 API：获取/更新/删除当前用户
 * 对应后端：GET/PUT/DELETE /users/me
 * 所有接口都需要 Bearer Token
 */

import request from '@/utils/request'
import type { UpdateUserRequest, UserInfo } from '@/types/user'

/** 获取当前登录用户信息 */
export function getCurrentUser(): Promise<UserInfo> {
  return request.get('/users/me')
}

/** 更新当前用户信息（只传需要修改的字段） */
export function updateCurrentUser(data: UpdateUserRequest): Promise<UserInfo> {
  return request.put('/users/me', data)
}

/** 软删除当前用户（is_active 设为 0） */
export function deleteCurrentUser(): Promise<void> {
  return request.delete('/users/me')
}
```

### 4.4 状态管理 `src/stores/user.ts`

```typescript
/**
 * 用户 Pinia Store
 * 管理登录状态、token、用户信息，提供登录/注册/登出方法
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getCurrentUser } from '@/api'
import type { LoginForm, RegisterForm, UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  // ===================== State =====================

  const userInfo = ref<UserInfo | null>(null)
  // 从 localStorage 恢复 token，刷新页面后保持登录
  const token = ref<string | null>(localStorage.getItem('access_token'))

  // ===================== Getters =====================

  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  // ===================== Actions =====================

  /**
   * 登录流程：
   * 1. 调用 /auth/token 获取 JWT
   * 2. 保存 token 到 localStorage
   * 3. 调用 /users/me 获取完整用户信息
   */
  async function loginUser(form: LoginForm) {
    const res = await loginApi({
      username: form.email,   // OAuth2 标准要求字段名为 username
      password: form.password,
    })

    token.value = res.access_token
    localStorage.setItem('access_token', res.access_token)

    // 获取完整用户信息
    await fetchUserInfo()
  }

  /** 注册（注册成功后不自动登录，让用户去登录页） */
  async function registerUser(form: RegisterForm) {
    await registerApi({
      username: form.username,
      email: form.email,
      password: form.password,
    })
  }

  /** 获取当前用户详情 */
  async function fetchUserInfo() {
    const user = await getCurrentUser()
    userInfo.value = user
  }

  /** 登出：清除 Pinia 状态和 localStorage */
  function logout() {
    token.value = null
    userInfo.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  // ===================== 页面加载时自动恢复 =====================

  if (token.value) {
    fetchUserInfo().catch(() => logout())
  }

  return {
    userInfo, token, isLoggedIn,
    loginUser, registerUser, fetchUserInfo, logout,
  }
})
```

### 4.5 路由配置 `src/router/index.ts`

```typescript
/**
 * 路由配置 + 导航守卫（登录拦截）
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true },  // 需要登录
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

/**
 * 全局前置守卫 —— 类似后端中间件
 * 未登录用户访问需要认证的页面时，重定向到登录页
 */
router.beforeEach((to, _from, next) => {
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 记住用户原本想访问的页面，登录后可以跳回来
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
```

### 4.6 页面组件

#### `src/views/LoginView.vue`

```vue
<template>
  <div class="login-container">
    <el-card class="login-card" header="用户登录">
      <el-form ref="formRef" :model="loginForm" :rules="rules" label-width="80px">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="loginForm.email" placeholder="请输入邮箱" type="email" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            type="password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="link-row">
        <span>还没有账号？</span>
        <router-link to="/register" class="link">去注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { LoginForm } from '@/types/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginForm>({ email: '', password: '' })

const rules = reactive<FormRules<LoginForm>>({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入合法的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不少于 6 位', trigger: 'blur' },
  ],
})

async function handleLogin() {
  // 1. 前端表单验证
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  // 2. 发起登录
  loading.value = true
  try {
    await userStore.loginUser(loginForm)
    ElMessage.success('登录成功')
    // 3. 跳转：优先跳 redirect 参数指定的页面
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    // 错误已由响应拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}
.login-card { width: 420px; }
.link-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}
.link { color: #409eff; text-decoration: none; }
.link:hover { text-decoration: underline; }
</style>
```

#### `src/views/RegisterView.vue`

```vue
<template>
  <div class="register-container">
    <el-card class="register-card" header="用户注册">
      <el-form ref="formRef" :model="registerForm" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" type="email" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" placeholder="请输入密码" type="password" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRegister" style="width: 100%">
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="link-row">
        <span>已有账号？</span>
        <router-link to="/login" class="link">去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { RegisterForm } from '@/types/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive<RegisterForm>({
  username: '', email: '', password: '', confirmPassword: '',
})

// 自定义验证：两次密码一致
const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = reactive<FormRules<RegisterForm>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度 2-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入合法的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不少于 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
})

async function handleRegister() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.registerUser(registerForm)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch {
    // 错误已由拦截器处理（如邮箱已存在）
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh; background-color: #f0f2f5;
}
.register-card { width: 460px; }
.link-row {
  display: flex; justify-content: flex-end; gap: 8px;
  font-size: 14px; color: #606266;
}
.link { color: #409eff; text-decoration: none; }
.link:hover { text-decoration: underline; }
</style>
```

#### `src/views/HomeView.vue`

```vue
<template>
  <div class="home-container">
    <el-card>
      <template #header><h2>欢迎使用 私人精品网页推荐系统</h2></template>

      <!-- 已登录 -->
      <div v-if="userStore.isLoggedIn && userStore.userInfo" class="user-info">
        <p>你好，<strong>{{ userStore.userInfo.username }}</strong>！</p>
        <p>邮箱：{{ userStore.userInfo.email }}</p>
        <div class="actions" style="margin-top: 20px">
          <el-button type="primary" @click="router.push('/profile')">管理个人信息</el-button>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
      </div>

      <!-- 未登录 -->
      <div v-else class="guest-info">
        <p>请先登录或注册</p>
        <div class="actions" style="margin-top: 20px">
          <el-button type="primary" @click="router.push('/login')">去登录</el-button>
          <el-button @click="router.push('/register')">去注册</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
    })
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/')
  } catch { /* 用户取消 */ }
}
</script>

<style scoped>
.home-container { max-width: 600px; margin: 40px auto; padding: 0 20px; }
.user-info p, .guest-info p { margin: 10px 0; font-size: 16px; }
.actions { display: flex; gap: 12px; }
</style>
```

#### `src/views/ProfileView.vue`

```vue
<template>
  <div class="profile-container">
    <el-card header="个人信息">
      <!-- 展示模式 -->
      <div v-if="!editing" class="info-display">
        <p><strong>用户名：</strong>{{ userStore.userInfo?.username }}</p>
        <p><strong>邮箱：</strong>{{ userStore.userInfo?.email }}</p>
        <p><strong>状态：</strong>{{ userStore.userInfo?.is_active === 1 ? '正常' : '已禁用' }}</p>
        <el-button type="primary" @click="startEditing">编辑信息</el-button>
      </div>

      <!-- 编辑模式 -->
      <el-form v-else ref="formRef" :model="editForm" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="输入新用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="输入新邮箱" type="email" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" placeholder="留空则不修改密码" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSave">保存</el-button>
          <el-button @click="editing = false">取消</el-button>
        </el-form-item>
      </el-form>

      <el-divider />
      <el-button type="danger" plain @click="handleDelete">删除账号</el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateCurrentUser, deleteCurrentUser } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const editing = ref(false)

const editForm = reactive({ username: '', email: '', password: '' })

const rules = reactive<FormRules<typeof editForm>>({
  username: [{ min: 2, max: 50, message: '2-50 个字符', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入合法邮箱', trigger: 'blur' }],
  password: [{ min: 6, message: '不少于 6 位', trigger: 'blur' }],
})

onMounted(async () => {
  await userStore.fetchUserInfo()
  if (userStore.userInfo) {
    editForm.username = userStore.userInfo.username
    editForm.email = userStore.userInfo.email
    editForm.password = ''
  }
})

function startEditing() {
  if (userStore.userInfo) {
    editForm.username = userStore.userInfo.username
    editForm.email = userStore.userInfo.email
    editForm.password = ''
  }
  editing.value = true
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const updateData: Record<string, string> = {}
    if (editForm.username) updateData.username = editForm.username
    if (editForm.email) updateData.email = editForm.email
    if (editForm.password) updateData.password = editForm.password

    await updateCurrentUser(updateData)
    ElMessage.success('更新成功')
    editing.value = false
    await userStore.fetchUserInfo()
  } catch { /* 拦截器已处理 */ } finally {
    loading.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除账号吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'error',
    })
    await deleteCurrentUser()
    ElMessage.success('账号已删除')
    userStore.logout()
    router.push('/')
  } catch { /* 用户取消 */ }
}
</script>

<style scoped>
.profile-container { max-width: 500px; margin: 40px auto; padding: 0 20px; }
.info-display p { margin: 12px 0; font-size: 16px; }
</style>
```

### 4.7 布局和入口

#### `src/App.vue`

```vue
<template>
  <router-view />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: #303133;
  background-color: #f5f7fa;
}
</style>
```

#### `src/main.ts`

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
```

### 4.8 配置文件

#### `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    port: 5173,
    open: true,
    // 代理配置：开发环境把 /api 请求转发到后端，解决跨域
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

#### `tsconfig.json` 路径别名

在 `tsconfig.json`（或 `tsconfig.app.json`）的 `compilerOptions` 中添加：

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## 第五步：启动

### 1. 先启动后端

```bash
cd C:\Users\shumeng\Desktop\求职\2026\FastAPI_demo\back
uvicorn app.main:application --host 0.0.0.0 --port 8000 --reload
```

验证：浏览器打开 `http://localhost:8000/docs` 应看到 Swagger UI。

### 2. 启动前端

```bash
cd C:\Users\shumeng\Desktop\求职\2026\FastAPI_demo\frontend
npm run dev
```

浏览器自动打开 `http://localhost:5173`。

---

## 第六步：测试流程

1. **注册** → 填写用户名、邮箱、密码 → 跳转到登录页
2. **登录** → 输入邮箱、密码 → 首页显示用户名
3. **个人信息** → 编辑修改 → 保存成功
4. **退出登录** → 刷新页面 → 回到未登录状态
5. **路由守卫** → 未登录时直接访问 `/profile` → 自动跳登录页
6. **刷新保持登录** → 登录后 F5 刷新 → 仍为登录状态

---

## 常见问题

| 问题 | 解决 |
|------|------|
| CORS 报错 | 检查 `vite.config.ts` 代理配置中 target 是否为 `http://localhost:8000` |
| 登录成功但获取用户信息 401 | 检查浏览器 Network 面板，确认请求头有 `Authorization: Bearer eyJ...` |
| `Cannot find module '@/xxx'` | 确认 `tsconfig.json` 中配了 `paths: { "@/*": ["./src/*"] }` |
| 注册提示邮箱已存在 | 数据库已有该邮箱，换一个或删掉 |
| 后端接口 404 | 确认后端正在运行，且路径前缀是 `/api/v1` |
