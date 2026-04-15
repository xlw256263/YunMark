/**
 * 认证相关 API 接口
 * 注意：登录接口使用 application/x-www-form-urlencoded 格式
 */
import request from './request'
import type { TokenResponse, UserCreate, User } from '@/types'

/**
 * 用户登录
 * POST /auth/token
 * @param email - 邮箱地址（后端字段名为 username）
 * @param password - 密码
 * 
 * 注意：此接口使用 OAuth2 标准格式，Content-Type 为 application/x-www-form-urlencoded
 */
export const login = (email: string, password: string) => {
  // 使用 URLSearchParams 构建表单数据（不需要额外安装 qs 库）
  const formData = new URLSearchParams({
    username: email, // 注意：后端 OAuth2 表单字段名叫 username，实际传邮箱
    password: password,
  })
  
  return request.post<TokenResponse>(
    '/auth/token',
    formData,
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }
  )
}

/**
 * 用户注册
 * POST /auth/register
 * @param data - 用户注册信息（用户名、邮箱、密码）
 */
export const register = (data: UserCreate) => {
  return request.post<User>('/auth/register', data)
}
