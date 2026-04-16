/**
 * 书签相关 API 接口
 */
import request from './request'
import type { Bookmark, BookmarkCreate, BookmarkUpdate, BookmarkListResponse } from '@/types'

/**
 * 获取书签列表
 * GET /bookmarks
 * @param params - 查询参数（分页、分类、标签、搜索）
 */
export const getBookmarks = (params?: {
  page?: number
  page_size?: number
  category_id?: number
  tag_ids?: number[]
  title?: string  // 搜索关键词
}) => {
  return request.get<BookmarkListResponse>('/bookmarks', { params })
}

/**
 * 获取单个书签详情
 * GET /bookmarks/:id
 * @param id - 书签ID
 */
export const getBookmark = (id: number) => {
  return request.get<Bookmark>(`/bookmarks/${id}`)
}

/**
 * 创建新书签
 * POST /bookmarks
 * @param data - 书签数据
 */
export const createBookmark = (data: BookmarkCreate) => {
  return request.post<Bookmark>('/bookmarks', data)
}

/**
 * 更新书签
 * PUT /bookmarks/:id
 * @param id - 书签ID
 * @param data - 更新数据
 */
export const updateBookmark = (id: number, data: BookmarkUpdate) => {
  return request.put<Bookmark>(`/bookmarks/${id}`, data)
}

/**
 * 删除书签
 * DELETE /bookmarks/:id
 * @param id - 书签ID
 */
export const deleteBookmark = (id: number) => {
  return request.delete<{ message: string }>(`/bookmarks/${id}`)
}

/**
 * 增加书签点击次数
 * PATCH /bookmarks/:id/click
 * @param id - 书签ID
 */
export const incrementClickCount = (id: number) => {
  return request.patch<{ id: number; click_count: number }>(`/bookmarks/${id}/click`)
}
