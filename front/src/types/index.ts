/**
 * 云藏智能收藏夹 - TypeScript 类型定义
 * 对应后端 Pydantic Schema 和 API 响应结构
 */

// ==================== 用户相关类型 ====================

/**
 * 用户信息接口
 * 对应后端 UserResponse schema
 */
export interface User {
  /** 用户ID */
  id: number
  /** 用户名 */
  username: string
  /** 邮箱地址 */
  email: string
  /** 账号状态：1=活跃, 0=已禁用 */
  is_active: number
  /** 用户角色（待后端实现） */
  role?: 'user' | 'admin'
  /** 头像URL（待后端实现） */
  avatar?: string | null
  /** 个人简介（待后端实现） */
  bio?: string | null
  /** 注册时间（待后端实现） */
  created_at?: string
}

/**
 * 用户注册请求
 * 对应后端 UserCreate schema
 */
export interface UserCreate {
  /** 用户名 */
  username: string
  /** 邮箱地址 */
  email: string
  /** 密码 */
  password: string
}

/**
 * 用户更新请求
 * 对应后端 UserUpdate schema（所有字段可选）
 */
export interface UserUpdate {
  /** 新用户名 */
  username?: string
  /** 新邮箱 */
  email?: string
  /** 新密码 */
  password?: string
}

/**
 * 个人资料更新请求
 */
export interface UserProfileUpdate {
  /** 新用户名 */
  username?: string
  /** 新邮箱 */
  email?: string
  /** 头像URL */
  avatar?: string
  /** 个人简介 */
  bio?: string
}

/**
 * 密码修改请求
 */
export interface PasswordChange {
  /** 原密码 */
  old_password: string
  /** 新密码 */
  new_password: string
}

/**
 * 头像上传响应
 */
export interface AvatarUploadResponse {
  /** 头像URL */
  avatar_url: string
  /** 提示信息 */
  message: string
}

// ==================== 认证相关类型 ====================

/**
 * Token 响应
 * 对应后端 TokenResponse schema
 */
export interface TokenResponse {
  /** JWT 访问令牌 */
  access_token: string
  /** Token 类型（通常为 "bearer"） */
  token_type: string
  /** 用户名 */
  username: string
  /** 邮箱 */
  email: string
}

// ==================== 书签相关类型 ====================

/**
 * 书签完整信息
 * 对应后端 BookmarkResponse schema
 */
export interface Bookmark {
  /** 书签ID */
  id: number
  /** 所属用户ID */
  user_id: number
  /** 网址URL */
  url: string
  /** 书签标题 */
  title: string
  /** 描述信息 */
  description: string | null
  /** 网站图标URL */
  favicon: string | null
  /** 点击次数 */
  click_count: number
  /** 创建时间 */
  created_at: string
  /** 所属分类（可能为空） */
  category: Category | null
  /** 标签列表 */
  tags: Tag[]
  /** 是否公开分享（待后端实现） */
  is_shared?: boolean
  /** 是否官方推荐（待后端实现） */
  is_featured?: boolean
}

/**
 * 创建书签请求
 * 对应后端 BookmarkCreate schema
 */
export interface BookmarkCreate {
  /** 网址URL（必填） */
  url: string
  /** 书签标题（必填） */
  title: string
  /** 描述信息 */
  description?: string
  /** 网站图标URL */
  favicon?: string
  /** 分类ID */
  category_id?: number
  /** 标签ID列表 */
  tag_ids?: number[]
}

/**
 * 更新书签请求
 * 对应后端 BookmarkUpdate schema（所有字段可选）
 */
export interface BookmarkUpdate {
  /** 新URL */
  url?: string
  /** 新标题 */
  title?: string
  /** 新描述 */
  description?: string
  /** 新图标 */
  favicon?: string
  /** 新分类ID */
  category_id?: number
  /** 新标签ID列表（null表示不更新，数组表示全量替换） */
  tag_ids?: number[] | null
}

/**
 * 书签分页列表响应
 * 对应后端 BookmarkListResponse schema
 */
export interface BookmarkListResponse {
  /** 总记录数 */
  total: number
  /** 当前页码 */
  page: number
  /** 每页数量 */
  page_size: number
  /** 书签列表 */
  items: Bookmark[]
}

/**
 * 点击计数响应
 * 对应后端 ClickCountResponse schema
 */
export interface ClickCountResponse {
  /** 书签ID */
  bookmark_id: number
  /** 更新后的点击次数 */
  click_count: number
}

// ==================== 分类相关类型 ====================

/**
 * 分类信息
 * 对应后端 CategoryResponse schema
 */
export interface Category {
  /** 分类ID */
  id: number
  /** 所属用户ID */
  user_id: number
  /** 分类名称 */
  name: string
}

/**
 * 创建分类请求
 * 对应后端 CategoryCreate schema
 */
export interface CategoryCreate {
  /** 分类名称 */
  name: string
}

/**
 * 更新分类请求
 * 对应后端 CategoryUpdate schema
 */
export interface CategoryUpdate {
  /** 新分类名称 */
  name?: string
}

// ==================== 标签相关类型 ====================

/**
 * 标签分类信息
 * 对应后端 TagCategoryResponse schema
 */
export interface TagCategory {
  /** 分类ID */
  id: number
  /** 分类名称 */
  name: string
  /** 分类描述 */
  description?: string | null
  /** 排序顺序 */
  sort_order: number
  /** 创建时间 */
  created_at: string
}

/**
 * 创建标签分类请求
 */
export interface TagCategoryCreate {
  /** 分类名称 */
  name: string
  /** 分类描述 */
  description?: string
  /** 排序顺序 */
  sort_order?: number
}

/**
 * 更新标签分类请求
 */
export interface TagCategoryUpdate {
  name?: string
  description?: string
  sort_order?: number
}

/**
 * 标签信息
 * 对应后端 TagResponse schema
 */
export interface Tag {
  /** 标签ID */
  id: number
  /** 标签名称 */
  name: string
  /** 所属分类ID */
  category_id?: number | null
  /** 所属分类详情 */
  category?: TagCategory | null
  /** 使用次数统计（管理员接口返回） */
  usage_count?: number
}

/**
 * 创建标签请求
 * 对应后端 TagCreate schema
 */
export interface TagCreate {
  /** 标签名称 */
  name: string
  /** 所属分类ID（可选） */
  category_id?: number | null
}

// ==================== 统计相关类型（待后端实现）====================

/**
 * 统计概览数据
 */
export interface StatsOverview {
  /** 收藏总数 */
  total_bookmarks: number
  /** 本周新增数量 */
  new_this_week: number
  /** 总点击次数 */
  total_clicks: number
  /** 分类数量 */
  total_categories: number
  /** 标签数量 */
  total_tags: number
}

/**
 * 热力图数据点
 */
export interface HeatmapData {
  /** 日期（YYYY-MM-DD） */
  date: string
  /** 点击次数 */
  count: number
}

/**
 * 分类分布数据
 */
export interface CategoryDistribution {
  /** 分类名称 */
  category_name: string
  /** 数量 */
  count: number
  /** 百分比 */
  percentage: number
}

/**
 * 热门书签数据
 */
export interface TopBookmark {
  /** 书签ID */
  id: number
  /** 标题 */
  title: string
  /** URL */
  url: string
  /** 点击次数 */
  click_count: number
}

/**
 * 时段分布数据
 */
export interface HourlyDistribution {
  /** 小时（0-23） */
  hour: number
  /** 点击次数 */
  count: number
}

/**
 * 标签使用统计数据
 */
export interface TagUsageStat {
  /** 标签名称 */
  tag_name: string
  /** 使用次数 */
  usage_count: number
}

// ============ 分享相关类型 ============

export type ShareStatus = 
  | 'draft'        // 草稿
  | 'pending'      // 待审核
  | 'reviewing'    // 审核中
  | 'approved'     // 已通过
  | 'rejected'     // 已驳回
  | 'cancelled'    // 已取消
  | 'taken_down'   // 已下架

export interface ShareRecord {
  id: number
  bookmark_id: number
  user_id: number
  status: ShareStatus
  review_note?: string | null
  reject_reason?: string | null
  submitted_at?: string | null
  reviewed_at?: string | null
  reviewer_id?: number | null
  created_at: string
  updated_at: string
  
  // 嵌套的书签信息
  bookmark_title?: string | null
  bookmark_url?: string | null
  bookmark_description?: string | null
  bookmark_favicon?: string | null
  
  // 用户信息
  username?: string | null
  
  // 审核人信息
  reviewer_username?: string | null
}

export interface ShareListResponse {
  total: number
  page: number
  page_size: number
  items: ShareRecord[]
}

// ==================== 公开分享相关类型（待后端实现）====================

/**
 * 官方精选书签
 */
export interface FeaturedBookmark {
  /** 书签ID */
  id: number
  /** 标题 */
  title: string
  /** URL */
  url: string
  /** 描述 */
  description: string | null
  /** 点击次数 */
  click_count: number
  /** 编辑推荐语 */
  editor_note?: string
  /** 推荐时间 */
  featured_at: string
}

// ==================== 管理员相关类型（待后端实现）====================

/**
 * 审核状态枚举
 */
export enum AuditStatus {
  /** 待审核 */
  Pending = 'pending',
  /** 已通过 */
  Approved = 'approved',
  /** 已驳回 */
  Rejected = 'rejected'
}

/**
 * 审核项
 */
export interface AuditItem {
  /** 审核ID */
  id: number
  /** 用户信息 */
  user: {
    id: number
    username: string
  }
  /** 书签信息 */
  bookmark: {
    title: string
    url: string
  }
  /** 提交时间 */
  submitted_at: string
  /** 审核状态 */
  status: AuditStatus
  /** 驳回原因 */
  reject_reason?: string
}

/**
 * 黑名单规则
 */
export interface BlacklistRule {
  /** 规则ID */
  id: number
  /** 规则类型 */
  type: 'domain' | 'regex'
  /** 匹配模式 */
  pattern: string
  /** 原因 */
  reason: string
  /** 创建时间 */
  created_at: string
}

/**
 * 管理员统计数据
 */
export interface AdminStats {
  /** 总用户数 */
  total_users: number
  /** 总书签数 */
  total_bookmarks: number
  /** 总分享数 */
  total_shared: number
  /** 今日活跃用户 */
  active_today: number
}
