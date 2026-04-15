<template>
  <div class="bookmark-page">
    <!-- 顶部操作栏 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">我的收藏</h1>
        <span class="bookmark-count">共 {{ bookmarkStore.total }} 个书签</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书签..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" :icon="Plus" @click="showAddDialog">
          添加书签
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="page-content">
      <!-- 左侧侧边栏 -->
      <aside class="sidebar">
        <!-- 分类列表 -->
        <div class="sidebar-section">
          <div class="section-header">
            <span class="section-title">分类</span>
            <el-button text :icon="Plus" size="small" @click="showAddCategoryDialog">
              新建
            </el-button>
          </div>
          <ul class="category-list">
            <li
              class="category-item"
              :class="{ active: !selectedCategoryId }"
              @click="handleCategoryClick(null)"
            >
              <el-icon><Collection /></el-icon>
              <span>全部</span>
              <span class="category-count">{{ bookmarkStore.total }}</span>
            </li>
            <li
              v-for="cat in bookmarkStore.categories"
              :key="cat.id"
              class="category-item"
              :class="{ active: selectedCategoryId === cat.id }"
              @click="handleCategoryClick(cat.id)"
            >
              <el-icon><Folder /></el-icon>
              <span>{{ cat.name }}</span>
            </li>
          </ul>
        </div>

        <!-- 标签云 -->
        <div class="sidebar-section">
          <div class="section-header">
            <span class="section-title">标签</span>
          </div>
          <div class="tag-cloud">
            <el-tag
              v-for="tag in usedTags"
              :key="tag.id"
              :type="selectedTagIds.includes(tag.id) ? 'primary' : 'info'"
              class="tag-item"
              @click="handleTagClick(tag.id)"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </aside>

      <!-- 右侧书签列表 -->
      <main class="bookmark-main">
        <!-- 加载状态 -->
        <div v-if="bookmarkStore.loading && bookmarkStore.bookmarks.length === 0" class="loading-wrapper">
          <el-icon class="loading-icon" :size="40"><Loading /></el-icon>
          <p>加载中...</p>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-else-if="bookmarkStore.bookmarks.length === 0"
          description="暂无书签，点击上方按钮添加"
        >
          <el-button type="primary" @click="showAddDialog">添加书签</el-button>
        </el-empty>

        <!-- 书签列表容器 -->
        <div v-else class="bookmark-list">
          <div
            v-for="bookmark in bookmarkStore.bookmarks"
            :key="bookmark.id"
            class="bookmark-item"
          >
            <!-- 主信息区域 -->
            <div class="item-main" @click="handleBookmarkClick(bookmark)">
              <div class="favicon-wrapper">
                <img
                  v-if="getFaviconUrl(bookmark)"
                  :src="getFaviconUrl(bookmark)"
                  :alt="bookmark.title"
                  class="favicon-img"
                />
                <div v-else class="favicon-default">
                  <span class="favicon-letter">{{ getFirstLetter(bookmark.title) }}</span>
                </div>
              </div>
              <div class="item-info">
                <h3 class="item-title" :title="bookmark.title">{{ bookmark.title }}</h3>
                <p class="item-description" :title="bookmark.description || '暂无描述'">
                  {{ bookmark.description || '暂无描述' }}
                </p>
                <div class="item-meta">
                  <span class="item-category" v-if="bookmark.category">
                    <el-icon><Folder /></el-icon>
                    {{ bookmark.category.name }}
                  </span>
                  <span class="item-clicks">
                    <el-icon><View /></el-icon>
                    {{ bookmark.click_count }} 次访问
                  </span>
                  <!-- 标签 - 在访问次数后面 -->
                  <div class="item-tags">
                    <el-tag
                      v-for="tag in bookmark.tags"
                      :key="tag.id"
                      size="small"
                      type="info"
                      class="item-tag"
                    >
                      {{ tag.name }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作按钮区域 -->
            <div class="item-actions" @click.stop>
              <el-button
                type="success"
                size="default"
                plain
                class="action-btn"
                @click="handleCopyUrl(bookmark)"
              >
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button
                type="primary"
                size="default"
                plain
                class="action-btn"
                @click="handleBookmarkClick(bookmark)"
              >
                <el-icon><Link /></el-icon>
                打开
              </el-button>
              <el-dropdown trigger="click">
                <el-button type="default" size="default" :icon="More" circle class="more-btn" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Edit" @click="handleEdit(bookmark)">编辑</el-dropdown-item>
                    <el-dropdown-item :icon="Delete" @click="handleDelete(bookmark)" class="delete-item">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="bookmarkStore.total > bookmarkStore.pageSize">
          <el-pagination
            v-model:current-page="bookmarkStore.currentPage"
            v-model:page-size="bookmarkStore.pageSize"
            :total="bookmarkStore.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @current-change="fetchBookmarks"
            @size-change="fetchBookmarks"
          />
        </div>
      </main>
    </div>

    <!-- 添加/编辑书签弹窗 -->
    <el-dialog
      v-model="bookmarkDialogVisible"
      :title="editingBookmark ? '编辑书签' : '添加书签'"
      width="500px"
      class="bookmark-dialog"
    >
      <el-form
        ref="bookmarkFormRef"
        :model="bookmarkForm"
        :rules="bookmarkRules"
        label-position="top"
      >
        <el-form-item label="网址" prop="url">
          <el-input v-model="bookmarkForm.url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="bookmarkForm.title" placeholder="书签标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="bookmarkForm.description"
            type="textarea"
            :rows="3"
            placeholder="可选描述"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="bookmarkForm.category_id" placeholder="选择分类" clearable style="width: 100%" @change="handleCategoryChange">
            <el-option
              v-for="cat in bookmarkStore.categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-cascader
            v-model="bookmarkForm.tag_ids"
            :options="tagCategoryOptions"
            :props="cascaderProps"
            placeholder="选择标签"
            clearable
            multiple
            filterable
            style="width: 100%"
          />
        </el-form-item>

      </el-form>
      <template #footer>
        <el-button @click="bookmarkDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookmarkStore.loading" @click="handleSaveBookmark">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加分类弹窗 -->
    <el-dialog
      v-model="categoryDialogVisible"
      title="新建分类"
      width="400px"
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-position="top"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookmarkStore.categoryLoading" @click="handleSaveCategory">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Collection, Folder, More, Edit, Delete, View, Loading, CopyDocument, Link,
  type FormInstance, type FormRules
} from '@element-plus/icons-vue'
import { useBookmarkStore } from '@/stores/bookmark'
import { getAdminTagCategories } from '@/api/admin'
import { getFaviconWithCache, getDomain, getCachedFavicon } from '@/utils/favicon'
import type { Bookmark, BookmarkCreate, CategoryCreate, Tag, TagCategory } from '@/types'

// ==================== Store ====================
const bookmarkStore = useBookmarkStore()

// ==================== Favicon 缓存 ====================
const faviconCache = ref<Map<number, string>>(new Map())

/**
 * 获取书签的 Favicon URL
 * 优先使用缓存，未缓存时异步加载
 */
const getFaviconUrl = (bookmark: Bookmark): string => {
  // 1. 检查内存缓存
  const cached = faviconCache.value.get(bookmark.id)
  if (cached) return cached

  // 2. 检查 localStorage 缓存
  const domain = getDomain(bookmark.url)
  const localStorageCache = getCachedFavicon(domain)
  if (localStorageCache) {
    faviconCache.value.set(bookmark.id, localStorageCache)
    return localStorageCache
  }

  // 3. 异步加载并缓存
  getFaviconWithCache(
    bookmark.url,
    (faviconUrl) => {
      faviconCache.value.set(bookmark.id, faviconUrl)
    },
    () => {
      // 加载失败，设置空字符串
      faviconCache.value.set(bookmark.id, '')
    }
  )

  return ''
}

/**
 * 获取标题首字母（用于默认图标）
 */
const getFirstLetter = (title: string): string => {
  if (!title) return '?'
  // 如果是中文，返回第一个字符
  const firstChar = title.trim().charAt(0)
  if (/[\u4e00-\u9fa5]/.test(firstChar)) {
    return firstChar
  }
  // 英文返回大写首字母
  return firstChar.toUpperCase()
}

// ==================== 搜索 ====================
const searchQuery = ref('')

const handleSearch = () => {
  // TODO: 实现搜索功能
  console.log('搜索:', searchQuery.value)
}

// ==================== 分类筛选 ====================
const selectedCategoryId = ref<number | null>(null)

const handleCategoryClick = (categoryId: number | null) => {
  selectedCategoryId.value = categoryId
  bookmarkStore.currentPage = 1
  fetchBookmarks()
}

// ==================== 标签筛选 ====================
const selectedTagIds = ref<number[]>([])

// 计算用户实际用到的标签
const usedTags = computed(() => {
  const tagMap = new Map<number, Tag>()
  bookmarkStore.bookmarks.forEach(bookmark => {
    bookmark.tags.forEach(tag => {
      if (!tagMap.has(tag.id)) {
        tagMap.set(tag.id, tag)
      }
    })
  })
  return Array.from(tagMap.values())
})

const handleTagClick = (tagId: number) => {
  const index = selectedTagIds.value.indexOf(tagId)
  if (index > -1) {
    selectedTagIds.value.splice(index, 1)
  } else {
    selectedTagIds.value.push(tagId)
  }
  bookmarkStore.currentPage = 1
  fetchBookmarks()
}

// ==================== 获取书签列表 ====================
const fetchBookmarks = () => {
  bookmarkStore.fetchBookmarks({
    page: bookmarkStore.currentPage,
    page_size: bookmarkStore.pageSize,
    category_id: selectedCategoryId.value || undefined,
    tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
  })
}

// ==================== 点击书签跳转 ====================
const handleBookmarkClick = (bookmark: Bookmark) => {
  // 新标签页打开
  window.open(bookmark.url, '_blank')
  // 增加点击次数
  bookmarkStore.incrementClickCount(bookmark.id)
}

// ==================== 复制书签链接 ====================
const handleCopyUrl = async (bookmark: Bookmark) => {
  try {
    await navigator.clipboard.writeText(bookmark.url)
    ElMessage.success('链接已复制到剪贴板')
  } catch {
    // 降级方案
    const input = document.createElement('input')
    input.value = bookmark.url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    ElMessage.success('链接已复制到剪贴板')
  }
}

// ==================== 添加/编辑书签 ====================
const bookmarkDialogVisible = ref(false)
const editingBookmark = ref<Bookmark | null>(null)
const bookmarkFormRef = ref<FormInstance>()
const bookmarkForm = ref<BookmarkCreate>({
  url: '',
  title: '',
  description: '',
  category_id: undefined,
  tag_ids: [],
})

// 表单验证规则
const bookmarkRules: FormRules = {
  url: [
    { required: true, message: '请输入网址', trigger: 'blur' },
    { type: 'url', message: '请输入正确的网址格式', trigger: 'blur' },
  ],
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
  ],
}

// 标签分类数据
const tagCategories = ref<TagCategory[]>([])

// 级联选择器配置
const cascaderProps = {
  multiple: true,
  checkStrictly: true,
  emitPath: false,
  expandTrigger: 'hover' as const,
}

// 构建级联选择器选项
const tagCategoryOptions = computed(() => {
  if (!tagCategories.value.length) return []

  return tagCategories.value.map(cat => ({
    value: `cat_${cat.id}`,
    label: cat.name,
    disabled: true,
    children: bookmarkStore.tags
      .filter(tag => tag.category_id === cat.id)
      .map(tag => ({
        value: tag.id,
        label: tag.name
      }))
  }))
})

const showAddDialog = () => {
  editingBookmark.value = null
  bookmarkForm.value = {
    url: '',
    title: '',
    description: '',
    category_id: undefined,
    tag_ids: [],
  }
  loadTagCategories()
  bookmarkDialogVisible.value = true
}

const handleEdit = (bookmark: Bookmark) => {
  editingBookmark.value = bookmark
  bookmarkForm.value = {
    url: bookmark.url,
    title: bookmark.title,
    description: bookmark.description || '',
    category_id: bookmark.category?.id,
    tag_ids: bookmark.tags.map(t => t.id),
  }
  loadTagCategories()
  bookmarkDialogVisible.value = true
}

// 加载标签分类
const loadTagCategories = async () => {
  try {
    tagCategories.value = await getAdminTagCategories()
  } catch (error) {
    console.error('加载标签分类失败', error)
  }
}

const handleSaveBookmark = async () => {
  if (!bookmarkFormRef.value) return

  await bookmarkFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      // 过滤掉分类 ID（只保留标签 ID）
      const tagOnlyIds = bookmarkForm.value.tag_ids?.filter(id =>
        !String(id).startsWith('cat_')
      ) || []

      const submitData = {
        ...bookmarkForm.value,
        tag_ids: tagOnlyIds
      }

      if (editingBookmark.value) {
        // 编辑模式
        await bookmarkStore.updateBookmark(editingBookmark.value.id, submitData)
        ElMessage.success('更新成功')
      } else {
        // 新增模式
        await bookmarkStore.createBookmark(submitData)
        ElMessage.success('添加成功')
      }
      bookmarkDialogVisible.value = false
      fetchBookmarks()
    } catch (error: any) {
      console.error('保存失败:', error)
    }
  })
}

// ==================== 删除书签 ====================
const handleDelete = (bookmark: Bookmark) => {
  ElMessageBox.confirm(
    `确定要删除书签「${bookmark.title}」吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await bookmarkStore.deleteBookmark(bookmark.id)
        ElMessage.success('删除成功')
        fetchBookmarks()
      } catch (error: any) {
        console.error('删除失败:', error)
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// ==================== 添加分类 ====================
const categoryDialogVisible = ref(false)
const categoryFormRef = ref<FormInstance>()
const categoryForm = ref<CategoryCreate>({
  name: '',
})

const categoryRules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 20, message: '分类名称长度为1-20个字符', trigger: 'blur' },
  ],
}

const showAddCategoryDialog = () => {
  categoryForm.value = { name: '' }
  categoryDialogVisible.value = true
}

const handleSaveCategory = async () => {
  if (!categoryFormRef.value) return

  await categoryFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await bookmarkStore.createCategory(categoryForm.value)
      ElMessage.success('分类创建成功')
      categoryDialogVisible.value = false
    } catch (error: any) {
      console.error('创建分类失败:', error)
    }
  })
}

// ==================== 生命周期 ====================
onMounted(async () => {
  // 初始化分类和标签
  await bookmarkStore.init()
  // 加载标签分类
  await loadTagCategories()
  // 加载书签列表
  fetchBookmarks()
})

</script>

<style scoped>
.bookmark-page {
  min-height: calc(100vh - 73px);
  background: #0f1923;
}

/* ========== 顶部操作栏 ========== */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  background: rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
}

.bookmark-count {
  font-size: 14px;
  color: #94a3b8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

/* ========== 主内容区 ========== */
.page-content {
  display: flex;
  min-height: calc(100vh - 80px);
}

/* ========== 加载状态 ========== */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #94a3b8;
}

.loading-icon {
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
  color: #818cf8;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ========== 左侧侧边栏 ========== */
.sidebar {
  width: 240px;
  padding: 24px 16px;
  background: rgba(255, 255, 255, 0.04);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 分类列表 */
.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #cbd5e1;
  font-size: 14px;
  transition: all 0.2s;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.category-item.active {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.category-count {
  margin-left: auto;
  font-size: 12px;
  color: #64748b;
}

/* 标签云 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.2s;
}

.tag-item:hover {
  transform: translateY(-2px);
}

/* ========== 右侧书签列表 ========== */
.bookmark-main {
  flex: 1;
  padding: 20px 32px;
  overflow-y: auto;
}

/* 书签列表容器 */
.bookmark-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 书签列表项 */
.bookmark-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  transition: all 0.25s ease;
}

.bookmark-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(129, 140, 248, 0.3);
  transform: translateX(4px);
}

/* 主信息区域 */
.item-main {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.item-main:hover .item-title {
  color: #818cf8;
}

.favicon-wrapper {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.favicon-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.favicon-default {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.favicon-letter {
  font-size: 20px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* 信息区域 */
.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}

.item-description {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

/* 元信息区域 */
.item-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
  flex-wrap: wrap;
}

.item-category,
.item-clicks {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.item-category .el-icon,
.item-clicks .el-icon {
  font-size: 14px;
}

/* 标签区域 - 在元信息内 */
.item-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.item-tag {
  font-size: 11px;
  padding: 2px 8px;
}

/* 操作按钮区域 */
.item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  font-size: 13px;
  font-weight: 500;
  padding: 6px 16px;
  height: 32px;
  border-radius: 6px;
}

.action-btn .el-icon {
  margin-right: 4px;
}

.action-btn[type="success"] {
  border-color: #67c23a;
  color: #67c23a;
}

.action-btn[type="success"]:hover {
  background: #67c23a;
  color: white;
}

.action-btn[type="primary"] {
  border-color: #409eff;
  color: #409eff;
}

.action-btn[type="primary"]:hover {
  background: #409eff;
  color: white;
}

.more-btn {
  padding: 0;
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.delete-item {
  color: #f56c6c;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .page-content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .bookmark-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
/* 级联选择器输入框样式 */
.el-cascader .el-input__wrapper {
  box-shadow: none !important;
  border: 1px solid #dcdfe6;
}

.el-cascader .el-input__wrapper:hover {
  border-color: #c0c4cc;
}

.el-cascader.is-focus .el-input__wrapper {
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff inset !important;
}

/* 隐藏级联选择器面板中的复选框 */
.el-cascader-panel .el-checkbox {
  display: none !important;
}

/* 选中的子标签高亮显示 */
.el-cascader-panel .el-cascader-node.is-active {
  color: #409eff;
  font-weight: 600;
}

/* 确保选中节点有背景色 */
.el-cascader-panel .el-cascader-node.is-active {
  background-color: #ecf5ff;
}

/* 鼠标悬停效果 */
.el-cascader-panel .el-cascader-node:hover {
  background-color: #f5f7fa;
}

/* 禁用一级分类节点的高亮 */
.el-cascader-panel .el-cascader-node[aria-level="1"].is-active {
  color: inherit;
  font-weight: normal;
  background-color: transparent;
}

.el-cascader-panel .el-cascader-node__postfix {
  margin-right: 10px;
}

/* 弹窗内的表单样式 */
.bookmark-dialog .el-form-item__label {
  font-weight: 500;
}

.bookmark-dialog .el-input__wrapper,
.bookmark-dialog .el-textarea__inner,
.bookmark-dialog .el-select .el-input__wrapper {
  box-shadow: none !important;
  border: 1px solid #dcdfe6;
}

.bookmark-dialog .el-input__wrapper:hover,
.bookmark-dialog .el-textarea__inner:hover,
.bookmark-dialog .el-select .el-input__wrapper:hover {
  border-color: #c0c4cc;
}
</style>
