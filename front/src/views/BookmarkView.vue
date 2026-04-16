<template>
  <div class="bookmark-page">
    <!-- 顶部操作栏 - 固定 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">我的收藏</h1>
        <span class="bookmark-count">共 {{ bookmarkStore.total }} 个书签</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书签标题或描述..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @input="handleSearchInput"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" :icon="Plus" @click="showAddDialog">
          添加书签
        </el-button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="page-content">
      <!-- 左侧侧边栏 - 独立滚动 -->
      <aside class="sidebar">
        <div class="sidebar-scroll-wrapper">
          <!-- 分类列表 -->
          <div class="sidebar-section">
            <div class="section-header">
              <span class="section-title">分类</span>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                class="new-category-btn"
                @click="showAddCategoryDialog"
              >
                新建
              </el-button>
            </div>
            <ul class="category-list">
              <li
                class="category-item category-parent"
                :class="{ active: !selectedCategoryId, expanded: showAllCategories }"
                @click="toggleCategoryExpand"
              >
                <el-icon class="expand-icon"><ArrowRight /></el-icon>
                <el-icon><Collection /></el-icon>
                <span>全部</span>
                <span class="category-count">{{ bookmarkStore.total }}</span>
              </li>
              <li v-show="showAllCategories" v-for="cat in bookmarkStore.categories"
                :key="cat.id"
                class="category-item category-child"
                :class="{ active: selectedCategoryId === cat.id }"
                @click="handleCategoryClick(cat.id)"
              >
                <el-icon><Folder /></el-icon>
                <span class="category-name">{{ cat.name }}</span>
                <div class="category-actions" @click.stop>
                  <el-dropdown trigger="click" @command="(cmd) => handleCategoryAction(cmd, cat)">
                    <el-button text :icon="More" size="small" class="category-more-btn" />
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit" :icon="Edit">重命名</el-dropdown-item>
                        <el-dropdown-item command="delete" :icon="Delete" class="delete-item">删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
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
                v-for="tag in displayTags"
                :key="tag.id"
                :type="selectedTagIds.includes(tag.id) ? 'primary' : 'info'"
                class="tag-item"
                :class="{ 'tag-selected': selectedTagIds.includes(tag.id) }"
                @click="handleTagClick(tag.id)"
              >
                {{ tag.name }}
              </el-tag>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧书签列表 - 独立滚动 -->
      <main class="bookmark-main">
        <div class="bookmark-scroll-wrapper">
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
                  size="small"
                  plain
                  class="action-btn"
                  @click="handleCopyUrl(bookmark)"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  plain
                  class="action-btn"
                  @click="handleBookmarkClick(bookmark)"
                >
                  <el-icon><Link /></el-icon>
                  打开
                </el-button>
                <el-dropdown trigger="click">
                  <el-button type="default" size="small" :icon="More" circle class="more-btn" />
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
        </div>
      </main>
    </div>

    <!-- 添加/编辑书签弹窗 -->
    <el-dialog
      v-model="bookmarkDialogVisible"
      :title="editingBookmark ? '编辑书签' : '添加书签'"
      width="500px"
      class="bookmark-dialog"
      @close="handleDialogClose"
      @keydown.enter.prevent
    >
      <el-form
        ref="bookmarkFormRef"
        :model="bookmarkForm"
        :rules="bookmarkRules"
        label-position="top"
        @submit.prevent="handleSaveBookmark"
      >
        <el-form-item label="网址" prop="url">
          <el-input
            v-model="bookmarkForm.url"
            placeholder="https://example.com"
            @keyup.enter="handleSaveBookmark"
          />
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="bookmarkForm.title"
            placeholder="书签标题"
            @keyup.enter="handleSaveBookmark"
          />
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
          <el-select v-model="bookmarkForm.category_id" placeholder="选择分类" clearable style="width: 100%">
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
      @close="handleCategoryDialogClose"
      @keydown.enter.prevent
    >
      <el-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-position="top"
        @submit.prevent="handleSaveCategory"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="categoryForm.name"
            placeholder="请输入分类名称"
            @keyup.enter="handleSaveCategory"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookmarkStore.categoryLoading" @click="handleSaveCategory">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑分类弹窗 -->
    <el-dialog
      v-model="editCategoryDialogVisible"
      title="重命名分类"
      width="400px"
      @close="handleEditCategoryDialogClose"
      @keydown.enter.prevent
    >
      <el-form
        ref="editCategoryFormRef"
        :model="editCategoryForm"
        :rules="categoryRules"
        label-position="top"
        @submit.prevent="handleUpdateCategory"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="editCategoryForm.name"
            placeholder="请输入新分类名称"
            @keyup.enter="handleUpdateCategory"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editCategoryDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="bookmarkStore.categoryLoading" @click="handleUpdateCategory">
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
  Search, Plus, Collection, Folder, More, Edit, Delete, View, Loading, CopyDocument, Link, ArrowRight,
  type FormInstance, type FormRules
} from '@element-plus/icons-vue'
import { useBookmarkStore } from '@/stores/bookmark'
import { getTagCategories } from '@/api/category'
import { updateCategory as updateCategoryApi, deleteCategory as deleteCategoryApi } from '@/api/category'
import { getFaviconWithCache, getDomain, getCachedFavicon } from '@/utils/favicon'
import type { Bookmark, BookmarkCreate, CategoryCreate, Tag, TagCategory } from '@/types'

// ==================== Store ====================
const bookmarkStore = useBookmarkStore()

// ==================== Favicon 缓存 ====================
const faviconCache = ref<Map<number, string>>(new Map())

const getFaviconUrl = (bookmark: Bookmark): string => {
  const cached = faviconCache.value.get(bookmark.id)
  if (cached) return cached

  const domain = getDomain(bookmark.url)
  const localStorageCache = getCachedFavicon(domain)
  if (localStorageCache) {
    faviconCache.value.set(bookmark.id, localStorageCache)
    return localStorageCache
  }

  getFaviconWithCache(
    bookmark.url,
    (faviconUrl) => {
      faviconCache.value.set(bookmark.id, faviconUrl)
    },
    () => {
      faviconCache.value.set(bookmark.id, '')
    }
  )

  return ''
}

const getFirstLetter = (title: string): string => {
  if (!title) return '?'
  const firstChar = title.trim().charAt(0)
  if (/[\u4e00-\u9fa5]/.test(firstChar)) {
    return firstChar
  }
  return firstChar.toUpperCase()
}

// ==================== 搜索 ====================
const searchQuery = ref('')
const searchTimer = ref<number | null>(null)

const handleSearchInput = () => {
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }

  searchTimer.value = window.setTimeout(() => {
    bookmarkStore.currentPage = 1
    fetchBookmarks()
  }, 300)
}

const handleSearch = () => {
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }
  bookmarkStore.currentPage = 1
  fetchBookmarks()
}

// ==================== 分类筛选 ====================
const selectedCategoryId = ref<number | null>(null)
const showAllCategories = ref(false)

const toggleCategoryExpand = () => {
  showAllCategories.value = !showAllCategories.value
  if (!showAllCategories.value) {
    selectedCategoryId.value = null
    searchQuery.value = ''
    bookmarkStore.currentPage = 1
    fetchBookmarks()
  }
}

const handleCategoryClick = (categoryId: number | null) => {
  selectedCategoryId.value = categoryId
  searchQuery.value = ''
  bookmarkStore.currentPage = 1
  fetchBookmarks()
}

// ==================== 标签筛选 ====================
const selectedTagIds = ref<number[]>([])

// 使用用户所有书签中使用过的标签
const displayTags = computed(() => {
  return bookmarkStore.myTags
})

const handleTagClick = (tagId: number) => {
  const index = selectedTagIds.value.indexOf(tagId)
  if (index > -1) {
    selectedTagIds.value.splice(index, 1)
  } else {
    selectedTagIds.value.push(tagId)
  }
  searchQuery.value = ''
  bookmarkStore.currentPage = 1
  fetchBookmarks()
}

// ==================== 获取书签列表 ====================
const fetchBookmarks = async () => {
  try {
    const params: any = {
      page: bookmarkStore.currentPage,
      page_size: bookmarkStore.pageSize,
      category_id: selectedCategoryId.value || undefined,
      tag_ids: selectedTagIds.value.length > 0 ? selectedTagIds.value : undefined,
    }

    if (searchQuery.value.trim()) {
      params.title = searchQuery.value.trim()
    }

    await bookmarkStore.fetchBookmarks(params)
  } catch (error) {
    console.error('获取书签列表失败:', error)
  }
}

// ==================== 点击书签跳转 ====================
const handleBookmarkClick = (bookmark: Bookmark) => {
  window.open(bookmark.url, '_blank')
  bookmarkStore.incrementClickCount(bookmark.id)
}

// ==================== 复制书签链接 ====================
const handleCopyUrl = async (bookmark: Bookmark) => {
  try {
    await navigator.clipboard.writeText(bookmark.url)
    ElMessage.success('链接已复制到剪贴板')
  } catch {
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

const bookmarkRules: FormRules = {
  url: [
    { required: true, message: '请输入网址', trigger: 'blur' },
    { type: 'url', message: '请输入正确的网址格式', trigger: 'blur' },
  ],
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
  ],
}

const tagCategories = ref<TagCategory[]>([])

const cascaderProps = {
  multiple: true,
  checkStrictly: true,
  emitPath: false,
  expandTrigger: 'hover' as const,
}

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

const loadTagCategories = async () => {
  try {
    tagCategories.value = await getTagCategories()
    console.log('[调试] 标签分类数据:', tagCategories.value)
    console.log('[调试] Store中的标签数据:', bookmarkStore.tags)
  } catch (error) {
    console.error('加载标签分类失败', error)
  }
}

const handleSaveBookmark = async () => {
  if (!bookmarkFormRef.value) return

  await bookmarkFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      const tagOnlyIds = bookmarkForm.value.tag_ids?.filter(id =>
        !String(id).startsWith('cat_')
      ) || []

      const submitData = {
        ...bookmarkForm.value,
        tag_ids: tagOnlyIds
      }

      if (editingBookmark.value) {
        await bookmarkStore.updateBookmark(editingBookmark.value.id, submitData)
        ElMessage.success('更新成功')
      } else {
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

const handleDialogClose = () => {
  bookmarkFormRef.value?.clearValidate()
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
    .catch(() => {})
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

const handleCategoryDialogClose = () => {
  categoryFormRef.value?.clearValidate()
}

// ==================== 编辑分类 ====================
const editCategoryDialogVisible = ref(false)
const editCategoryFormRef = ref<FormInstance>()
const editCategoryForm = ref<CategoryCreate>({
  name: '',
})
const editingCategoryId = ref<number | null>(null)

const handleCategoryAction = (command: string, category: any) => {
  if (command === 'edit') {
    handleEditCategory(category)
  } else if (command === 'delete') {
    handleDeleteCategory(category)
  }
}

const handleEditCategory = (category: any) => {
  editingCategoryId.value = category.id
  editCategoryForm.value = { name: category.name }
  editCategoryDialogVisible.value = true
}

const handleUpdateCategory = async () => {
  if (!editCategoryFormRef.value || !editingCategoryId.value) return

  await editCategoryFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      await updateCategoryApi(editingCategoryId.value, editCategoryForm.value)
      ElMessage.success('分类更新成功')
      editCategoryDialogVisible.value = false
      await bookmarkStore.fetchCategories()
    } catch (error: any) {
      console.error('更新分类失败:', error)
    }
  })
}

const handleEditCategoryDialogClose = () => {
  editCategoryFormRef.value?.clearValidate()
}

// ==================== 删除分类 ====================
const handleDeleteCategory = (category: any) => {
  ElMessageBox.confirm(
    `确定要删除分类「${category.name}」吗？删除后该分类下的书签将变为未分类。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await deleteCategoryApi(category.id)
        ElMessage.success('分类删除成功')
        if (selectedCategoryId.value === category.id) {
          selectedCategoryId.value = null
        }
        await bookmarkStore.fetchCategories()
        fetchBookmarks()
      } catch (error: any) {
        console.error('删除分类失败:', error)
      }
    })
    .catch(() => {})
}

// ==================== 生命周期 ====================
onMounted(async () => {
  await bookmarkStore.init()
  console.log('[调试] Store初始化完成, tags:', bookmarkStore.tags.length)
  await loadTagCategories()
  fetchBookmarks()
})

</script>

<style scoped>
.bookmark-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #0f1923;
  overflow: hidden;
}

.page-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
  background: rgba(255, 255, 255, 0.06);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
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
  width: 280px;
}

.page-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

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
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.04);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-scroll-wrapper {
  padding: 24px 16px;
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

.new-category-btn {
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  border: none;
  color: #fff;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
}

.new-category-btn:hover {
  background: linear-gradient(135deg, #818cf8 0%, #a5b4fc 100%);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}

.new-category-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
}

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
  position: relative;
}

.category-parent {
  background: rgba(99, 102, 241, 0.15);
  font-weight: 500;
}

.category-parent:hover {
  background: rgba(99, 102, 241, 0.25);
}

.category-parent.active {
  background: rgba(99, 102, 241, 0.3);
  color: #818cf8;
}

.expand-icon {
  transition: transform 0.3s ease;
  font-size: 12px;
}

.category-parent.expanded .expand-icon {
  transform: rotate(90deg);
}

.category-children {
  padding-left: 20px;
  margin-top: 4px;
}

.category-child {
  padding: 6px 12px;
  font-size: 13px;
}

.category-child:hover {
  background: rgba(255, 255, 255, 0.08);
}

.category-child.active {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
}

.category-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.category-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.category-item:hover .category-actions {
  opacity: 1;
}

.category-more-btn {
  color: #94a3b8;
  padding: 0;
  min-width: auto;
}

.category-more-btn:hover {
  color: #818cf8;
}

.category-count {
  margin-left: auto;
  font-size: 12px;
  color: #64748b;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.tag-item:hover {
  transform: translateY(-2px);
}

.tag-item.tag-selected {
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
  font-weight: 500;
}

.bookmark-main {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: #0f1923;
  min-width: 0;
}

.bookmark-scroll-wrapper {
  padding: 20px 32px;
  min-height: 100%;
}

.sidebar::-webkit-scrollbar,
.bookmark-main::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track,
.bookmark-main::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb,
.bookmark-main::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  transition: background 0.3s;
}

.sidebar::-webkit-scrollbar-thumb:hover,
.bookmark-main::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.bookmark-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bookmark-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
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

.item-main {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.item-main:hover .item-title {
  color: #818cf8;
}

.favicon-wrapper {
  width: 38px;
  height: 38px;
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
  font-size: 18px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 3px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}

.item-description {
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 14px;
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
  font-size: 13px;
}

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

.item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  padding: 6px 12px;
  font-size: 13px;
}

.more-btn {
  width: 32px;
  height: 32px;
  padding: 0;
}

.delete-item {
  color: #ef4444;
}

.delete-item:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
}

/* 隐藏级联选择器中的复选框 - 使用全局样式 */
.el-cascader-panel .el-cascader-node .el-checkbox {
  display: none !important;
}

.el-cascader-panel .el-cascader-node .el-checkbox__input {
  display: none !important;
}

.el-cascader-panel .el-cascader-node .el-cascader-node__label {
  padding-left: 0 !important;
  margin-left: 0 !important;
}

</style>

<style>
/* 全局样式，用于隐藏级联选择器复选框（穿透scoped限制） */
.el-cascader-panel .el-cascader-node .el-checkbox {
  display: none !important;
}

.el-cascader-panel .el-cascader-node .el-checkbox__input {
  display: none !important;
}

.el-cascader-panel .el-cascader-node .el-cascader-node__label {
  padding-left: 0 !important;
  margin-left: 0 !important;
}
</style>
