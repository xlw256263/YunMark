/**
 * 标签相关 API 接口
 */
import request from './request'
import type { Tag, TagCreate } from '@/types'

/**
 * 获取所有标签
 * GET /bookmarks/tags/list
 */
export const getTags = () => {
  return request.get<Tag[]>('/bookmarks/tags/list')
}

/**
 * 创建标签
 * POST /bookmarks/tags
 * @param data - 标签数据
 */
export const createTag = (data: TagCreate) => {
  return request.post<Tag>('/bookmarks/tags', data)
}
