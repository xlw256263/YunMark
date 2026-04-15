/**
 * 书签状态管理 Store
 * 管理书签、分类、标签的增删改查
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getBookmarks,
  createBookmark as createBookmarkApi,
  updateBookmark as updateBookmarkApi,
  deleteBookmark as deleteBookmarkApi,
} from '@/api/bookmark'
import { getCategories, createCategory as createCategoryApi } from '@/api/category'
import { getTags } from '@/api/tag'
import type {
  Bookmark,
  BookmarkCreate,
  BookmarkUpdate,
  Category,
  CategoryCreate,
  Tag,
} from '@/types'

export const useBookmarkStore = defineStore('bookmark', () => {
  // ==================== 书签状态 ====================

  /** 书签列表 */
  const bookmarks = ref<Bookmark[]>([])

  /** 总数量 */
  const total = ref(0)

  /** 当前页码 */
  const currentPage = ref(1)

  /** 每页数量 */
  const pageSize = ref(10)

  /** 加载状态 */
  const loading = ref(false)

  // ==================== 分类状态 ====================

  /** 分类列表 */
  const categories = ref<Category[]>([])

  /** 分类加载状态 */
  const categoryLoading = ref(false)

  // ==================== 标签状态 ====================

  /** 标签列表 */
  const tags = ref<Tag[]>([])

  /** 标签加载状态 */
  const tagLoading = ref(false)

  // ==================== 书签操作方法 ====================

  /**
   * 获取书签列表
   * @param params - 查询参数
   */
  async function fetchBookmarks(params?: {
    page?: number
    page_size?: number
    category_id?: number
    tag_ids?: number[]
  }) {
    loading.value = true
    try {
      const response = await getBookmarks({
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
        category_id: params?.category_id,
        tag_ids: params?.tag_ids,
      })

      bookmarks.value = response.items
      total.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
    } catch (error) {
      console.error('获取书签列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建书签
   * @param data - 书签数据
   */
  async function createBookmark(data: BookmarkCreate) {
    loading.value = true
    try {
      // 调用 API 函数（使用别名避免命名冲突）
      const newBookmark = await createBookmarkApi(data)
      bookmarks.value.unshift(newBookmark)
      total.value++
      return newBookmark
    } catch (error) {
      console.error('创建书签失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新书签
   * @param id - 书签ID
   * @param data - 更新数据
   */
  async function updateBookmark(id: number, data: BookmarkUpdate) {
    loading.value = true
    try {
      // 调用 API 函数
      const updatedBookmark = await updateBookmarkApi(id, data)
      const index = bookmarks.value.findIndex(b => b.id === id)
      if (index > -1) {
        bookmarks.value[index] = updatedBookmark
      }
      return updatedBookmark
    } catch (error) {
      console.error('更新书签失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除书签
   * @param id - 书签ID
   */
  async function deleteBookmark(id: number) {
    loading.value = true
    try {
      // 调用 API 函数
      await deleteBookmarkApi(id)
      const index = bookmarks.value.findIndex(b => b.id === id)
      if (index > -1) {
        bookmarks.value.splice(index, 1)
        total.value--
      }
    } catch (error) {
      console.error('删除书签失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // ==================== 分类操作方法 ====================

  /**
   * 获取分类列表
   */
  async function fetchCategories() {
    categoryLoading.value = true
    try {
      categories.value = await getCategories()
    } catch (error) {
      console.error('获取分类列表失败:', error)
      throw error
    } finally {
      categoryLoading.value = false
    }
  }

  /**
   * 创建分类
   * @param data - 分类数据
   */
  async function createCategory(data: CategoryCreate) {
    categoryLoading.value = true
    try {
      // 调用 API 函数（使用别名避免命名冲突）
      const newCategory = await createCategoryApi(data)
      categories.value.push(newCategory)
      return newCategory
    } catch (error) {
      console.error('创建分类失败:', error)
      throw error
    } finally {
      categoryLoading.value = false
    }
  }

  // ==================== 标签操作方法 ====================

  /**
   * 获取标签列表
   */
  async function fetchTags() {
    tagLoading.value = true
    try {
      tags.value = await getTags()
    } catch (error) {
      console.error('获取标签列表失败:', error)
      throw error
    } finally {
      tagLoading.value = false
    }
  }

  // ==================== 初始化 ====================

  /**
   * 初始化数据（加载分类和标签）
   */
  async function init() {
    await Promise.all([fetchCategories(), fetchTags()])
  }

  return {
    // 书签状态
    bookmarks,
    total,
    currentPage,
    pageSize,
    loading,

    // 分类状态
    categories,
    categoryLoading,

    // 标签状态
    tags,
    tagLoading,

    // 书签操作
    fetchBookmarks,
    createBookmark,
    updateBookmark,
    deleteBookmark,

    // 分类操作
    fetchCategories,
    createCategory,

    // 标签操作
    fetchTags,

    // 初始化
    init,
  }
})
