/**
 * 标签相关 API 接口
 */
import request from './request'
import type { Tag } from '@/types'

/**
 * 获取所有标签（公开接口）
 */
export const getTags = () => {
  return request.get<Tag[]>('/bookmarks/tags/list')
}

/**
 * 获取当前用户使用的标签
 */
export const getMyTags = () => {
  return request.get<Tag[]>('/bookmarks/tags/my-tags')
}

/**
 * 创建标签
 * POST /bookmarks/tags
 * @param data - 标签数据
 */
export const createTag = (data: TagCreate) => {
  return request.post<Tag>('/bookmarks/tags', data)
}
