/**
 * 分类相关 API 接口
 */
import request from './request'
import type { Category, CategoryCreate, CategoryUpdate } from '@/types'

/**
 * 获取所有分类
 * GET /bookmarks/categories/list
 */
export const getCategories = () => {
  return request.get<Category[]>('/bookmarks/categories/list')
}

/**
 * 创建分类
 * POST /bookmarks/categories
 * @param data - 分类数据
 */
export const createCategory = (data: CategoryCreate) => {
  return request.post<Category>('/bookmarks/categories', data)
}

/**
 * 更新分类
 * PUT /bookmarks/categories/:id
 * @param id - 分类ID
 * @param data - 更新数据
 */
export const updateCategory = (id: number, data: CategoryUpdate) => {
  return request.put<Category>(`/bookmarks/categories/${id}`, data)
}

/**
 * 删除分类
 * DELETE /bookmarks/categories/:id
 * @param id - 分类ID
 */
export const deleteCategory = (id: number) => {
  return request.delete<{ message: string }>(`/bookmarks/categories/${id}`)
}
