// front/src/api/share.ts
import request from './request'
import type { ShareRecord, ShareListResponse } from '@/types'

/**
 * 创建分享（草稿）
 */
export const createShare = (bookmarkId: number) => {
  return request.post<ShareRecord>('/shares', { bookmark_id: bookmarkId })
}

/**
 * 提交审核
 */
export const submitShare = (shareId: number) => {
  return request.post<ShareRecord>('/shares/submit', { share_id: shareId })
}

/**
 * 取消分享
 */
export const cancelShare = (shareId: number) => {
  return request.post<ShareRecord>('/shares/cancel', { share_id: shareId })
}

/**
 * 获取我的分享列表
 */
export const getMyShares = (params?: {
  page?: number
  page_size?: number
  status?: string
}) => {
  return request.get<ShareListResponse>('/shares/my-shares', { params })
}

/**
 * 管理员：获取待审核列表
 */
export const getPendingShares = (params?: {
  page?: number
  page_size?: number
  status?: string
}) => {
  return request.get<ShareListResponse>('/admin/shares/pending', { params })
}

/**
 * 管理员：审核分享
 */
export const reviewShare = (data: {
  share_id: number
  status: 'approved' | 'rejected'
  review_note?: string
  reject_reason?: string
}) => {
  return request.post<ShareRecord>('/admin/shares/review', data)
}

/**
 * 管理员：下架分享
 */
export const takeDownShare = (shareId: number, reason: string) => {
  return request.post<ShareRecord>(`/admin/shares/${shareId}/take-down`, null, {
    params: { reason }
  })
}

/**
 * 获取官方分享列表（公开接口）
 */
export const getPublicShares = (params?: {
  page?: number
  page_size?: number
  sort?: 'latest' | 'popular'
}) => {
  return request.get<ShareListResponse>('/public/shares', { params })
}
