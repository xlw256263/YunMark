/**
 * 用户相关 API 接口
 */
import request from './request'
import type { User, UserUpdate, UserProfileUpdate, PasswordChange, AvatarUploadResponse } from '@/types'

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
 * 更新个人资料
 * PATCH /users/me/profile
 * @param data - 个人资料更新数据
 */
export const updateProfile = (data: UserProfileUpdate) => {
  return request.patch<User>('/users/me/profile', data)
}

/**
 * 修改密码
 * POST /users/me/change-password
 * @param data - 密码修改数据
 */
export const changePassword = (data: PasswordChange) => {
  return request.post<{ message: string }>('/users/me/change-password', data)
}

/**
 * 上传头像
 * POST /users/me/avatar
 * @param file - 头像文件
 */
export const uploadAvatar = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<AvatarUploadResponse>('/users/me/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 注销账号（软删除）
 * DELETE /users/me
 */
export const deleteUser = () => {
  return request.delete<{ message: string }>('/users/me')
}
