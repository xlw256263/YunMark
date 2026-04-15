<template>
  <div class="favorites-page">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <router-link to="/dashboard" class="back-btn">
          <span class="icon-back">←</span>
          返回
        </router-link>
        <h2>我的收藏夹</h2>
      </div>
      <div class="nav-right">
        <span class="welcome">欢迎, {{ username }}</span>
        <button class="btn btn-outline" @click="logout">退出登录</button>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="menu-item" :class="{ active: $route.name === 'Dashboard' }">
          <router-link to="/dashboard">
            <span class="icon-home">🏠</span>
            <span>首页</span>
          </router-link>
        </div>
        <div
          v-for="category in categories"
          :key="category.id"
          class="menu-item"
          :class="{ active: currentFilter.category_id === category.id }"
          @click="filterByCategory(category.id)"
        >
          <span class="icon-category">📁</span>
          <span>{{ category.name }}</span>
        </div>
        <div class="menu-item" :class="{ active: $route.name === 'Favorites' }">
          <router-link to="/favorites">
            <span class="icon-favorite">❤️</span>
            <span>全部收藏</span>
          </router-link>
        </div>
        <div class="menu-item" :class="{ active: $route.name === 'Profile' }">
          <router-link to="/profile">
            <span class="icon-user">👤</span>
            <span>个人中心</span>
          </router-link>
        </div>
      </aside>

      <!-- 内容区 -->
      <main class="content">
        <!-- 操作栏 -->
        <div class="favorites-header">
          <div class="header-left">
            <h3>
              {{ currentFilter.category_id ? getCategoryName(currentFilter.category_id) : '全部收藏' }}
              ({{ totalBookmarks }})
            </h3>
          </div>
          <div class="header-right">
            <button class="btn btn-primary" @click="showAddModal = true">
              <span>+</span> 添加书签
            </button>
          </div>
        </div>

        <!-- 筛选和排序 -->
        <div class="filters-bar">
          <div class="filter-group">
            <label>排序：</label>
            <select v-model="sortBy" class="filter-select" @change="handleSortChange">
              <option value="recent">最近收藏</option>
              <option value="popular">最受欢迎</option>
              <option value="alphabetical">按名称排序</option>
            </select>
          </div>
          <div class="filter-group" v-if="tags.length > 0">
            <label>标签：</label>
            <div class="tag-filters">
              <span
                v-for="tag in tags"
                :key="tag.id"
                class="tag-filter"
                :class="{ active: currentFilter.tag_ids.includes(tag.id) }"
                @click="toggleTagFilter(tag.id)"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 书签列表 -->
        <div v-else-if="bookmarks.length > 0" class="bookmarks-grid">
          <div
            v-for="bookmark in sortedBookmarks"
            :key="bookmark.id"
            class="bookmark-card"
            @click="visitBookmark(bookmark)"
          >
            <div class="card-image">
              <img
                :src="bookmark.favicon || `https://via.placeholder.com/300x200/4a90e2/ffffff?text=${encodeURIComponent(bookmark.title)}`"
                :alt="bookmark.title"
                @error="handleImageError"
              />
            </div>
            <div class="card-content">
              <div class="card-header">
                <h4>{{ bookmark.title }}</h4>
                <button
                  class="remove-btn"
                  @click.stop="confirmDelete(bookmark)"
                  title="删除书签"
                >
                  ×
                </button>
              </div>
              <p class="description">{{ bookmark.description || '暂无描述' }}</p>
              <div class="card-meta">
                <span v-if="bookmark.category" class="category-badge">
                  📁 {{ bookmark.category.name }}
                </span>
                <span class="click-count">
                  👁️ {{ bookmark.click_count }} 次访问
                </span>
              </div>
              <div class="tags" v-if="bookmark.tags && bookmark.tags.length > 0">
                <span v-for="tag in bookmark.tags" :key="tag.id" class="tag">
                  #{{ tag.name }}
                </span>
              </div>
              <div class="card-footer">
                <span class="created-at">{{ formatDate(bookmark.created_at) }}</span>
                <button class="btn btn-small btn-outline" @click.stop="editBookmark(bookmark)">
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <div class="empty-icon">❤️</div>
          <h3>暂无收藏</h3>
          <p>您还没有收藏任何网站，点击右上角添加您的第一个书签吧！</p>
          <button class="btn btn-primary" @click="showAddModal = true">
            添加书签
          </button>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            下一页
          </button>
        </div>
      </main>
    </div>

    <!-- 添加/编辑书签弹窗 -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showEditModal ? '编辑书签' : '添加书签' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>标题 *</label>
              <input
                v-model="formData.title"
                type="text"
                required
                placeholder="输入网站标题"
              />
            </div>
            <div class="form-group">
              <label>URL *</label>
              <input
                v-model="formData.url"
                type="url"
                required
                placeholder="https://example.com"
              />
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea
                v-model="formData.description"
                rows="3"
                placeholder="输入网站描述（可选）"
              ></textarea>
            </div>
            <div class="form-group">
              <label>图标 URL</label>
              <input
                v-model="formData.favicon"
                type="url"
                placeholder="https://example.com/favicon.ico（可选）"
              />
            </div>
            <div class="form-group">
              <label>分类</label>
              <select v-model="formData.category_id">
                <option :value="null">无分类</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>标签</label>
              <div class="tag-selector">
                <div class="selected-tags" v-if="formData.tag_ids.length > 0">
                  <span
                    v-for="tagId in formData.tag_ids"
                    :key="tagId"
                    class="selected-tag"
                  >
                    {{ getTagName(tagId) }}
                    <button type="button" @click="removeTag(tagId)">×</button>
                  </span>
                </div>
                <select @change="addTag($event)" :value="''">
                  <option :value="''" disabled>选择标签...</option>
                  <option v-for="tag in availableTags" :key="tag.id" :value="tag.id">
                    {{ tag.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? '提交中...' : (showEditModal ? '保存' : '添加') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 添加分类弹窗 -->
    <div v-if="showCategoryModal" class="modal-overlay" @click="showCategoryModal = false">
      <div class="modal modal-small" @click.stop>
        <div class="modal-header">
          <h3>新建分类</h3>
          <button class="close-btn" @click="showCategoryModal = false">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleCreateCategory">
            <div class="form-group">
              <label>分类名称 *</label>
              <input
                v-model="newCategoryName"
                type="text"
                required
                placeholder="输入分类名称"
              />
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="showCategoryModal = false">取消</button>
              <button type="submit" class="btn btn-primary">创建</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useBookmarkStore } from '@/stores/bookmark.js'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const bookmarkStore = useBookmarkStore()

// 用户信息
const username = computed(() => userStore.username)

// Store 数据
const bookmarks = computed(() => bookmarkStore.bookmarks)
const categories = computed(() => bookmarkStore.categories)
const tags = computed(() => bookmarkStore.tags)
const totalBookmarks = computed(() => bookmarkStore.totalBookmarks)
const currentPage = computed(() => bookmarkStore.currentPage)
const totalPages = computed(() => bookmarkStore.totalPages)
const loading = computed(() => bookmarkStore.loading)
const currentFilter = computed(() => bookmarkStore.currentFilter)

// 本地状态
const sortBy = ref('recent')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showCategoryModal = ref(false)
const submitting = ref(false)
const newCategoryName = ref('')
const editingBookmark = ref(null)

// 表单数据
const formData = ref({
  title: '',
  url: '',
  description: '',
  favicon: '',
  category_id: null,
  tag_ids: []
})

// 排序后的书签
const sortedBookmarks = computed(() => {
  const sorted = [...bookmarks.value]

  switch(sortBy.value) {
    case 'recent':
      return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    case 'popular':
      return sorted.sort((a, b) => b.click_count - a.click_count)
    case 'alphabetical':
      return sorted.sort((a, b) => a.title.localeCompare(b.title))
    default:
      return sorted
  }
})

// 可用的标签（未选择的）
const availableTags = computed(() => {
  return tags.value.filter(tag => !formData.value.tag_ids.includes(tag.id))
})

// 生命周期
onMounted(async () => {
  try {
    console.log('Favorites mounted, loading data...')
    await Promise.all([
      bookmarkStore.fetchCategories(),
      bookmarkStore.fetchTags()
    ])
    console.log('Categories:', bookmarkStore.categories)
    console.log('Tags:', bookmarkStore.tags)

    // 检查 URL 参数中是否有分类 ID
    const categoryId = route.query.category
    if (categoryId) {
      console.log('Loading bookmarks for category:', categoryId)
      await bookmarkStore.fetchBookmarks(1, { category_id: parseInt(categoryId) })
    } else {
      await bookmarkStore.fetchBookmarks(1)
    }
    console.log('Bookmarks loaded:', bookmarkStore.bookmarks)
  } catch (error) {
    console.error('Failed to load data:', error)
    alert('加载数据失败，请刷新页面重试')
  }
})

// 监听路由变化
watch(() => route.query.category, async (newCategoryId) => {
  if (newCategoryId) {
    await bookmarkStore.fetchBookmarks(1, { category_id: parseInt(newCategoryId) })
  } else {
    await bookmarkStore.fetchBookmarks(1)
  }
})

// 方法
const logout = () => {
  userStore.logout()
  bookmarkStore.resetState()
  router.push('/')
}

const visitBookmark = async (bookmark) => {
  // 增加点击次数
  await bookmarkStore.addClickCount(bookmark.id)
  // 打开链接
  window.open(bookmark.url, '_blank')
}

const confirmDelete = async (bookmark) => {
  if (confirm(`确定要删除 "${bookmark.title}" 吗？`)) {
    try {
      await bookmarkStore.removeBookmark(bookmark.id)
      alert('删除成功')
    } catch (error) {
      alert('删除失败')
    }
  }
}

const editBookmark = (bookmark) => {
  editingBookmark.value = bookmark
  formData.value = {
    title: bookmark.title,
    url: bookmark.url,
    description: bookmark.description || '',
    favicon: bookmark.favicon || '',
    category_id: bookmark.category_id,
    tag_ids: bookmark.tags ? bookmark.tags.map(t => t.id) : []
  }
  showEditModal.value = true
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    if (showEditModal.value) {
      await bookmarkStore.editBookmark(editingBookmark.value.id, formData.value)
      alert('更新成功')
    } else {
      await bookmarkStore.addBookmark(formData.value)
      alert('添加成功')
    }
    closeModal()
  } catch (error) {
    alert(showEditModal.value ? '更新失败' : '添加失败')
  } finally {
    submitting.value = false
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  showCategoryModal.value = false
  editingBookmark.value = null
  resetForm()
}

const resetForm = () => {
  formData.value = {
    title: '',
    url: '',
    description: '',
    favicon: '',
    category_id: null,
    tag_ids: []
  }
}

const addTag = (event) => {
  const tagId = parseInt(event.target.value)
  if (tagId && !formData.value.tag_ids.includes(tagId)) {
    formData.value.tag_ids.push(tagId)
  }
  event.target.value = ''
}

const removeTag = (tagId) => {
  const index = formData.value.tag_ids.indexOf(tagId)
  if (index !== -1) {
    formData.value.tag_ids.splice(index, 1)
  }
}

const getTagName = (tagId) => {
  const tag = tags.value.find(t => t.id === tagId)
  return tag ? tag.name : ''
}

const getCategoryName = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  return category ? category.name : '未知分类'
}

const handleCreateCategory = async () => {
  try {
    await bookmarkStore.addCategory({ name: newCategoryName.value })
    alert('分类创建成功')
    showCategoryModal.value = false
    newCategoryName.value = ''
  } catch (error) {
    alert('创建分类失败')
  }
}

const filterByCategory = (categoryId) => {
  bookmarkStore.fetchBookmarks(1, { category_id: categoryId })
}

const toggleTagFilter = (tagId) => {
  const tagIds = currentFilter.value.tag_ids || []
  const newTagIds = tagIds.includes(tagId)
    ? tagIds.filter(id => id !== tagId)
    : [...tagIds, tagId]

  bookmarkStore.fetchBookmarks(1, {
    category_id: currentFilter.value.category_id,
    tag_ids: newTagIds
  })
}

const handleSortChange = () => {
  // 排序在计算属性中处理，这里只需触发重新渲染
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    bookmarkStore.fetchBookmarks(page, currentFilter.value)
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const handleImageError = (e) => {
  e.target.src = 'https://via.placeholder.com/300x200/cccccc/666666?text=No+Image'
}
</script>

<style scoped>
.favorites-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-left h2 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.back-btn {
  text-decoration: none;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 5px;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #f5f7fa;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome {
  color: #666;
  font-size: 14px;
}

.main-content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #eee;
  height: calc(100vh - 60px);
  position: fixed;
  top: 60px;
  left: 0;
  overflow-y: auto;
}

.menu-item {
  padding: 12px 20px;
  cursor: pointer;
}

.menu-item a,
.menu-item {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #666;
  transition: all 0.3s;
  padding: 8px 12px;
  border-radius: 5px;
}

.menu-item:hover {
  background: #f5f7fa;
  color: #4a90e2;
}

.menu-item.active {
  background: #4a90e2;
  color: white;
}

.content {
  flex: 1;
  margin-left: 220px;
  padding: 20px;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.favorites-header h3 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.filters-bar {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-group label {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
  color: #333;
  font-size: 14px;
}

.tag-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-filter {
  padding: 4px 12px;
  background: #f0f2f5;
  color: #666;
  border-radius: 15px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.tag-filter:hover {
  background: #e0e2e5;
}

.tag-filter.active {
  background: #4a90e2;
  color: white;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4a90e2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.bookmarks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.bookmark-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.bookmark-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-image img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.card-content {
  padding: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.card-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  flex: 1;
  margin-right: 10px;
}

.remove-btn {
  background: #ff4757;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 0.3s;
}

.remove-btn:hover {
  opacity: 0.8;
}

.description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.category-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.click-count {
  color: #999;
}

.tags {
  margin-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  display: inline-block;
  background: #f0f2f5;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.created-at {
  color: #999;
  font-size: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
}

.empty-state p {
  margin: 0 0 20px 0;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
  padding: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.page-btn:hover:not(:disabled) {
  background: #4a90e2;
  color: white;
  border-color: #4a90e2;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-small {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #f5f7fa;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #4a90e2;
}

.tag-selector {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #4a90e2;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.selected-tag button {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background: #4a90e2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #357abd;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 1px solid #ddd;
  color: #666;
}

.btn-outline:hover {
  background: #f5f7fa;
  border-color: #4a90e2;
  color: #4a90e2;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .menu-item span:last-child {
    display: none;
  }

  .content {
    margin-left: 60px;
  }

  .bookmarks-grid {
    grid-template-columns: 1fr;
  }

  .favorites-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>