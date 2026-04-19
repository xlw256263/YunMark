/**
 * 数据统计相关 API 接口
 */
import request from './request'
import type {
  StatsOverview,
  CategoryDistribution,
  TopBookmark,
  HeatmapData,
  TagUsageStat
} from '@/types'

/**
 * 获取数据概览
 * GET /statistics/overview
 */
export const getStatisticsOverview = () => {
  return request.get<StatsOverview>('/statistics/overview')
}

/**
 * 获取分类分布数据
 * GET /statistics/category-distribution
 */
export const getCategoryDistribution = () => {
  return request.get<CategoryDistribution[]>('/statistics/category-distribution')
}

/**
 * 获取热门书签
 * GET /statistics/top-bookmarks
 * @param limit - 返回数量，默认10
 */
export const getTopBookmarks = (limit: number = 10) => {
  return request.get<TopBookmark[]>('/statistics/top-bookmarks', {
    params: { limit }
  })
}

/**
 * 获取创建趋势
 * GET /statistics/creation-trend
 * @param days - 天数范围，默认30天
 */
export const getCreationTrend = (days: number = 30) => {
  return request.get<HeatmapData[]>('/statistics/creation-trend', {
    params: { days }
  })
}

/**
 * 获取标签使用统计
 * GET /statistics/tag-usage
 * @param limit - 返回数量，默认15
 */
export const getTagUsageStats = (limit: number = 15) => {
  return request.get<TagUsageStat[]>('/statistics/tag-usage', {
    params: { limit }
  })
}
