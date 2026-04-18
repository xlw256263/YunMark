// front/src/api/admin.ts
import request from './request'
import type { Tag, TagCreate, TagCategory, TagCategoryCreate, TagCategoryUpdate } from '@/types'

/**
 * 管理员 API 模块
 */

// ============ 标签管理 ============

/**
 * 获取所有标签（含使用统计，支持分页）
 */
export function getAdminTags(params?: {
  page?: number
  page_size?: number
  category_id?: number | null
}) {
  return request.get<{
    total: number
    page: number
    page_size: number
    items: Tag[]
  }>('/admin/tags', { params })
}

/**
 * 创建标签
 */
export function createAdminTag(data: TagCreate) {
  return request.post<Tag>('/admin/tags', data)
}

/**
 * 更新标签
 */
export function updateAdminTag(tagId: number, tagName: string, categoryId?: number | null) {
  return request.put<Tag>(`/admin/tags/${tagId}`, null, {
    params: { 
      tag_name: tagName,
      ...(categoryId !== undefined && { category_id: categoryId })
    }
  })
}

/**
 * 删除标签
 */
export function deleteAdminTag(tagId: number) {
  return request.delete(`/admin/tags/${tagId}`)
}

// ============ 标签分类管理 ============

/**
 * 获取所有标签分类（按排序顺序）
 */
export function getAdminTagCategories() {
  return request.get<TagCategory[]>('/admin/tag-categories')
}

/**
 * 获取标签分类详情
 */
export function getAdminTagCategory(categoryId: number) {
  return request.get<TagCategory>(`/admin/tag-categories/${categoryId}`)
}

/**
 * 创建标签分类
 */
export function createAdminTagCategory(data: TagCategoryCreate) {
  return request.post<TagCategory>('/admin/tag-categories', data)
}

/**
 * 更新标签分类
 */
export function updateAdminTagCategory(categoryId: number, data: TagCategoryUpdate) {
  return request.put<TagCategory>(`/admin/tag-categories/${categoryId}`, data)
}

/**
 * 删除标签分类
 */
export function deleteAdminTagCategory(categoryId: number) {
  return request.delete(`/admin/tag-categories/${categoryId}`)
}
