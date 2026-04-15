/**
 * Axios 请求封装
 * 包含请求拦截器、响应拦截器、统一错误处理
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/**
 * 创建 axios 实例
 * 配置基础URL和超时时间
 */
const request = axios.create({
  // API 基础路径，从环境变量读取，默认为 /api/v1
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  // 请求超时时间：10秒
  timeout: 10000,
  // 注意：不在这里设置默认 Content-Type，让各个请求自己指定
})

/**
 * 不需要认证的接口列表
 */
const PUBLIC_APIS = [
  '/auth/token',      // 登录
  '/auth/register',   // 注册
  '/bookmarks/tags/list',  // 获取标签列表（公开）
]

/**
 * 请求拦截器
 * 在发送请求前自动添加 JWT Token
 */
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 检查是否是公开接口（不需要 token）
    const isPublicApi = PUBLIC_APIS.some(api => config.url?.includes(api))
    
    // 只有非公开接口才添加 token
    if (!isPublicApi) {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  (error: AxiosError) => {
    // 请求错误处理
    console.error('请求配置错误:', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 统一处理响应数据和错误
 */
request.interceptors.response.use(
  // 成功响应：直接返回 data
  (response) => response.data,
  
  // 错误响应：统一错误处理
  (error: AxiosError) => {
    const { status, data } = error.response || {}

    // 根据 HTTP 状态码进行不同处理
    switch (status) {
      case 401:
        // 未授权：Token 过期或无效
        // 只在当前路由需要认证时才提示并跳转
        const currentPath = router.currentRoute.value.path
        const authRoutes = ['/my/bookmarks', '/stats', '/profile']
        const needsAuth = authRoutes.some(route => currentPath.startsWith(route))
        
        if (needsAuth) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          
          // 跳转到登录页，并携带当前路径以便登录后返回
          router.push({ 
            path: '/', 
            query: { 
              login: '1',
              redirect: currentPath 
            } 
          })
          
          // 只在需要认证的页面被拦截时才提示
          ElMessage.warning('登录已过期，请重新登录')
        }
        // 如果是在登录页面或首页，不提示，让组件自己处理错误
        break
        
      case 403:
        // 禁止访问：权限不足
        router.push('/403')
        ElMessage.error('无权访问该资源')
        break
        
      case 404:
        // 资源不存在
        ElMessage.error((data as any)?.detail || '请求的资源不存在')
        break
        
      case 409:
        // 数据冲突（如用户名/邮箱已存在）
        // 不在这里处理，让组件自己显示错误信息
        break
        
      case 422:
        // 参数校验失败
        // 不在这里处理，让组件自己显示错误信息
        break
        
      case 500:
        // 服务器内部错误
        ElMessage.error('服务器异常，请稍后重试')
        break
        
      default:
        // 其他错误：只在非 401/409/422 时显示通用错误
        if (status !== 401 && status !== 409 && status !== 422) {
          ElMessage.error((data as any)?.detail || '网络异常，请稍后重试')
        }
    }

    return Promise.reject(error)
  }
)

// 导出 axios 实例
export default request
