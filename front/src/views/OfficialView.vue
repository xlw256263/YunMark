<template>
  <div class="official-view">
    <!-- 顶部标题区 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><Star /></el-icon>
          官方分享
        </h1>
        <p class="page-subtitle">发现优质书签，与社区共享知识</p>
      </div>
      <div class="header-right">
        <el-radio-group v-model="sortType" @change="handleSortChange" size="large">
          <el-radio-button label="latest">
            <el-icon><Sort /></el-icon>
            最新发布
          </el-radio-button>
          <el-radio-button label="popular">
            <el-icon><Histogram /></el-icon>
            最热门
          </el-radio-button>
        </el-radio-group>
      </div>
    </header>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stats-info">
        <el-icon><Document /></el-icon>
        <span>共 <strong>{{ total }}</strong> 个优质分享</span>
      </div>
      <el-button @click="loadShares" :icon="Refresh" circle />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && shares.length === 0" class="loading-wrapper">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="shares.length === 0"
      description="暂无公开分享"
      class="empty-state"
    >
      <template #image>
        <el-icon :size="80" color="#909399"><Document /></el-icon>
      </template>
    </el-empty>

    <!-- 分享卡片列表 -->
    <div v-else class="share-list">
      <div
        v-for="share in shares"
        :key="share.id"
        class="share-card"
      >
        <!-- 书签信息区域 -->
        <div class="card-content" @click="handleBookmarkClick(share)">
          <div class="favicon-wrapper">
            <img
              v-if="getFaviconUrl(share)"
              :src="getFaviconUrl(share)"
              :alt="share.bookmark_title"
              class="favicon-img"
            />
            <div v-else class="favicon-default">
              <span class="favicon-letter">{{ getFirstLetter(share.bookmark_title) }}</span>
            </div>
          </div>

          <div class="bookmark-info">
            <h3 class="bookmark-title" :title="share.bookmark_title">
              {{ share.bookmark_title }}
            </h3>
            <p class="bookmark-description" :title="share.bookmark_description">
              {{ share.bookmark_description || '暂无描述' }}
            </p>

            <div class="bookmark-meta">
              <span class="meta-item user-info">
                <el-icon><User /></el-icon>
                {{ share.username }}
              </span>
              <span class="meta-item time-info">
                <el-icon><Clock /></el-icon>
                {{ formatTime(share.reviewed_at) }}
              </span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions" @click.stop>
          <el-button
            type="primary"
            size="default"
            plain
            @click="handleOpenLink(share)"
          >
            <el-icon><Link /></el-icon>
            访问
          </el-button>
          <el-button
            type="success"
            size="default"
            plain
            @click="handleCopyUrl(share)"
          >
            <el-icon><CopyDocument /></el-icon>
            复制链接
          </el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="total > 0" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadShares"
        @current-change="loadShares"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Star, Sort, Histogram, Refresh, Loading,
  Document, User, Clock, Link, CopyDocument
} from '@element-plus/icons-vue'
import { getPublicShares } from '@/api/share'
import { getFaviconWithCache, getDomain, getCachedFavicon } from '@/utils/favicon'
import type { ShareRecord } from '@/types'

const loading = ref(false)
const shares = ref<ShareRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const sortType = ref<'latest' | 'popular'>('latest')

// Favicon 缓存
const faviconCache = ref<Map<number, string>>(new Map())

// 获取 Favicon URL
const getFaviconUrl = (share: ShareRecord): string => {
  // 优先使用书签自带的 favicon
  if (share.bookmark_favicon) return share.bookmark_favicon

  // 检查内存缓存
  const cached = faviconCache.value.get(share.bookmark_id)
  if (cached) return cached

  // 检查 localStorage 缓存
  if (share.bookmark_url) {
    const domain = getDomain(share.bookmark_url)
    const localStorageCache = getCachedFavicon(domain)
    if (localStorageCache) {
      faviconCache.value.set(share.bookmark_id, localStorageCache)
      return localStorageCache
    }

    // 异步获取并缓存
    getFaviconWithCache(
      share.bookmark_url,
      (faviconUrl) => {
        faviconCache.value.set(share.bookmark_id, faviconUrl)
      },
      () => {
        faviconCache.value.set(share.bookmark_id, '')
      }
    )
  }

  return ''
}

// 加载分享列表
const loadShares = async () => {
  loading.value = true
  try {
    const res = await getPublicShares({
      page: currentPage.value,
      page_size: pageSize.value,
      sort: sortType.value
    })
    shares.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载分享列表失败')
  } finally {
    loading.value = false
  }
}

// 排序变化
const handleSortChange = () => {
  currentPage.value = 1
  loadShares()
}

// 点击书签卡片
const handleBookmarkClick = (share: ShareRecord) => {
  console.log('查看书签:', share.bookmark_title)
}

// 打开链接
const handleOpenLink = (share: ShareRecord) => {
  if (share.bookmark_url) {
    window.open(share.bookmark_url, '_blank')
  }
}

// 复制链接
const handleCopyUrl = (share: ShareRecord) => {
  if (share.bookmark_url) {
    navigator.clipboard.writeText(share.bookmark_url).then(() => {
      ElMessage.success('链接已复制')
    }).catch(() => {
      const input = document.createElement('input')
      input.value = share.bookmark_url!
      document.body.appendChild(input)
      input.select()
      document.execCommand('copy')
      document.body.removeChild(input)
      ElMessage.success('链接已复制到剪贴板')
    })
  }
}

// 获取首字母
const getFirstLetter = (title?: string | null): string => {
  if (!title) return '?'
  const firstChar = title.trim().charAt(0)
  if (/[\u4e00-\u9fa5]/.test(firstChar)) return firstChar
  return firstChar.toUpperCase()
}

// 格式化时间
const formatTime = (time?: string | null) => {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadShares()
})
</script>

<style scoped>
.official-view {
  min-height: calc(100vh - 73px);
  padding: 32px;
  background: #f5f7fa;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1d2129;
}

.title-icon {
  color: #f59e0b;
  font-size: 32px;
}

.page-subtitle {
  margin: 0;
  color: #86909c;
  font-size: 14px;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stats-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.stats-info .el-icon {
  color: #409eff;
}

.stats-info strong {
  color: #1d2129;
  font-weight: 700;
}

/* 加载状态 */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #86909c;
}

.loading-wrapper p {
  margin-top: 16px;
}

.empty-state {
  padding: 60px 0;
}

/* 分享卡片列表 */
.share-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.share-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 1px solid #e5e6eb;
}

.share-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #409eff;
}

.card-content {
  display: flex;
  gap: 16px;
  padding: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.card-content:hover {
  background: #fafafa;
}

.favicon-wrapper {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  overflow: hidden;
  background: #f2f3f5;
}

.favicon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 6px;
}

.favicon-default {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.favicon-letter {
  font-size: 22px;
  font-weight: 700;
  color: white;
}

.bookmark-info {
  flex: 1;
  min-width: 0;
}

.bookmark-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-description {
  font-size: 13px;
  color: #86909c;
  margin: 0 0 12px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
  min-height: 39px;
}

.bookmark-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-info .el-icon {
  color: #67c23a;
}

.time-info .el-icon {
  color: #e6a23c;
}

.card-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: #fafafa;
  border-top: 1px solid #f2f3f5;
}

.card-actions .el-button {
  flex: 1;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .share-list {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .official-view {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .share-list {
    grid-template-columns: 1fr;
  }

  .stats-bar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
