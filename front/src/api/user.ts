/**
 * 用户相关 API 接口
 */
import request from './request'
import type { User, UserUpdate } from '@/types'

/**
 * 获取当前用户信息
 * GET /users/me
 */
export const getCurrentUser = () => {
  return request.get<User>('/users/me')
}

/**
 * 更新当前用户信息
 * PUT /users/me
 * @param data - 要更新的字段（可选）
 */
export const updateUser = (data: UserUpdate) => {
  return request.put<User>('/users/me', data)
}

/**
 * 注销账号（软删除）
 * DELETE /users/me
 */
export const deleteUser = () => {
  return request.delete<{ message: string }>('/users/me')
}
