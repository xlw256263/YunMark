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
              v-for="tag in bookmarkStore.tags"
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

        <!-- 书签卡片网格 -->
        <div v-else class="bookmark-grid">
          <el-card
            v-for="bookmark in bookmarkStore.bookmarks"
            :key="bookmark.id"
            class="bookmark-card"
            shadow="hover"
          >
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="card-title-row">
                <el-avatar
                  :size="24"
                  :src="bookmark.favicon || `https://www.google.com/s2/favicons?domain=${getDomain(bookmark.url)}&sz=64`"
                  class="favicon"
                />
                <h3 class="card-title" :title="bookmark.title">{{ bookmark.title }}</h3>
              </div>
              <el-dropdown trigger="click" class="card-actions">
                <el-icon><More /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Edit" @click="handleEdit(bookmark)">编辑</el-dropdown-item>
                    <el-dropdown-item :icon="Delete" @click="handleDelete(bookmark)">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <!-- 卡片内容 -->
            <div class="card-body">
              <p class="card-description" :title="bookmark.description || '暂无描述'">
                {{ bookmark.description || '暂无描述' }}
              </p>
            </div>

            <!-- 卡片底部 -->
            <div class="card-footer">
              <div class="card-tags">
                <el-tag
                  v-for="tag in bookmark.tags"
                  :key="tag.id"
                  size="small"
                  type="info"
                  class="card-tag"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              <div class="card-meta">
                <span class="click-count">
                  <el-icon><View /></el-icon>
                  {{ bookmark.click_count }}
                </span>
                <span class="card-category" v-if="bookmark.category">
                  {{ bookmark.category.name }}
                </span>
              </div>
            </div>
          </el-card>
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
          <el-select
            v-model="bookmarkForm.tag_ids"
            multiple
            placeholder="选择标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in bookmarkStore.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Plus, Collection, Folder, More, Edit, Delete, View, Loading,
  type FormInstance, type FormRules
} from '@element-plus/icons-vue'
import { useBookmarkStore } from '@/stores/bookmark'
import type { Bookmark, BookmarkCreate, CategoryCreate } from '@/types'

// ==================== Store ====================
const bookmarkStore = useBookmarkStore()

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

const showAddDialog = () => {
  editingBookmark.value = null
  bookmarkForm.value = {
    url: '',
    title: '',
    description: '',
    category_id: undefined,
    tag_ids: [],
  }
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
  bookmarkDialogVisible.value = true
}

const handleSaveBookmark = async () => {
  if (!bookmarkFormRef.value) return

  await bookmarkFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      if (editingBookmark.value) {
        // 编辑模式
        await bookmarkStore.updateBookmark(editingBookmark.value.id, bookmarkForm.value)
        ElMessage.success('更新成功')
      } else {
        // 新增模式
        await bookmarkStore.createBookmark(bookmarkForm.value)
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

// ==================== 获取域名（用于 favicon）====================
const getDomain = (url: string) => {
  try {
    return new URL(url).hostname
  } catch {
    return ''
  }
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
  padding: 24px 32px;
  overflow-y: auto;
}

/* 书签卡片网格 */
.bookmark-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.bookmark-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
  cursor: pointer;
}

.bookmark-card:hover {
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.favicon {
  flex-shrink: 0;
}

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: #e2e8f0;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-actions {
  color: #94a3b8;
  cursor: pointer;
}

/* 卡片内容 */
.card-body {
  margin-bottom: 12px;
}

.card-description {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.card-tag {
  font-size: 11px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
}

.click-count {
  display: flex;
  align-items: center;
  gap: 4px;
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
