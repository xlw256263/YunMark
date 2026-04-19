<!-- front/src/views/MySharesView.vue -->
<template>
  <div class="my-shares-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><Share /></el-icon>
          我的分享
        </h1>
        <p class="page-subtitle">管理您分享的书签，查看审核状态</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-total">
        <div class="stat-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总分享数</div>
        </div>
      </div>

      <div class="stat-card stat-pending">
        <div class="stat-icon">
          <el-icon :size="24"><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>

      <div class="stat-card stat-approved">
        <div class="stat-icon">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>

      <div class="stat-card stat-rejected">
        <div class="stat-icon">
          <el-icon :size="24"><CircleClose /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
      </div>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-radio-group v-model="statusFilter" @change="handleFilterChange" size="default">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="draft">草稿</el-radio-button>
          <el-radio-button label="pending">待审核</el-radio-button>
          <el-radio-button label="reviewing">审核中</el-radio-button>
          <el-radio-button label="approved">已通过</el-radio-button>
          <el-radio-button label="rejected">已驳回</el-radio-button>
          <el-radio-button label="cancelled">已取消</el-radio-button>
        </el-radio-group>
      </div>
      <el-button @click="loadShares" :icon="Refresh">刷新</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && shares.length === 0" class="loading-wrapper">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="shares.length === 0"
      description="暂无分享记录"
    >
      <template #image>
        <el-icon :size="80" color="#909399"><Document /></el-icon>
      </template>
      <el-button type="primary" @click="$router.push('/my/bookmarks')">
        去添加书签
      </el-button>
    </el-empty>

    <!-- 分享卡片列表 -->
    <div v-else class="share-cards">
      <div
        v-for="share in shares"
        :key="share.id"
        class="share-card"
      >
        <!-- 书签信息区域 -->
        <div class="card-header">
          <div class="favicon-wrapper">
            <img
              v-if="share.bookmark_favicon"
              :src="share.bookmark_favicon"
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
            <el-link
              :href="share.bookmark_url"
              target="_blank"
              type="primary"
              :underline="false"
              class="bookmark-url"
            >
              {{ share.bookmark_url }}
            </el-link>
          </div>
          <el-tag :type="getStatusType(share.status)" effect="dark" size="large">
            {{ getStatusText(share.status) }}
          </el-tag>
        </div>

        <!-- 时间信息 -->
        <div class="card-meta">
          <span class="meta-item">
            <el-icon><Clock /></el-icon>
            提交：{{ formatTime(share.submitted_at) }}
          </span>
          <span v-if="share.reviewed_at" class="meta-item">
            <el-icon><Check /></el-icon>
            审核：{{ formatTime(share.reviewed_at) }}
          </span>
        </div>

        <!-- 驳回原因 -->
        <div v-if="share.reject_reason" class="reject-reason-box">
          <el-icon class="reject-icon"><Warning /></el-icon>
          <span>{{ share.reject_reason }}</span>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <el-button
            v-if="share.status === 'draft'"
            type="primary"
            size="default"
            @click="handleSubmit(share)"
          >
            <el-icon><Upload /></el-icon>
            提交审核
          </el-button>

          <el-button
            v-if="['draft', 'pending', 'reviewing'].includes(share.status)"
            type="danger"
            plain
            size="default"
            @click="handleCancel(share)"
          >
            <el-icon><Close /></el-icon>
            取消分享
          </el-button>

          <el-button
            v-if="share.status === 'rejected'"
            type="primary"
            plain
            size="default"
            @click="handleResubmit(share)"
          >
            <el-icon><RefreshRight /></el-icon>
            重新提交
          </el-button>

          <el-button
            v-if="share.bookmark_url"
            text
            type="primary"
            @click="handleOpenLink(share)"
          >
            <el-icon><Link /></el-icon>
            访问链接
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
        :page-sizes="[6, 12, 24]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadShares"
        @current-change="loadShares"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Share, Document, Clock, CircleCheck, CircleClose,
  Refresh, Loading, Check, Warning, Upload, Close,
  RefreshRight, Link
} from '@element-plus/icons-vue'
import { getMyShares, submitShare, cancelShare } from '@/api/share'
import type { ShareRecord } from '@/types'

const loading = ref(false)
const shares = ref<ShareRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const statusFilter = ref<string>('')

// 统计数据
const stats = computed(() => {
  return {
    total: total.value,
    pending: shares.value.filter(s => s.status === 'pending').length,
    approved: shares.value.filter(s => s.status === 'approved').length,
    rejected: shares.value.filter(s => s.status === 'rejected').length
  }
})

// 加载分享列表
const loadShares = async () => {
  loading.value = true
  try {
    const res = await getMyShares({
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined
    })
    shares.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载分享列表失败')
  } finally {
    loading.value = false
  }
}

// 筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadShares()
}

// 提交审核
const handleSubmit = async (share: ShareRecord) => {
  try {
    await ElMessageBox.confirm('确定要提交审核吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    await submitShare(share.id)
    ElMessage.success('提交成功，等待管理员审核')
    loadShares()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

// 取消分享
const handleCancel = async (share: ShareRecord) => {
  try {
    await ElMessageBox.confirm('确定要取消分享吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await cancelShare(share.id)
    ElMessage.success('已取消分享')
    loadShares()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

// 重新提交
const handleResubmit = async (share: ShareRecord) => {
  try {
    await ElMessageBox.confirm('确定要重新提交审核吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    await submitShare(share.id)
    ElMessage.success('重新提交成功')
    loadShares()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

// 打开链接
const handleOpenLink = (share: ShareRecord) => {
  if (share.bookmark_url) {
    window.open(share.bookmark_url, '_blank')
  }
}

// 状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    draft: 'info',
    pending: 'warning',
    reviewing: '',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

// 状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    reviewing: '审核中',
    approved: '已通过',
    rejected: '已驳回',
    cancelled: '已取消',
    taken_down: '已下架'
  }
  return textMap[status] || status
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
.my-shares-view {
  padding: 24px 32px;
  background: #f5f7fa;
  min-height: calc(100vh - 73px);
}

/* 页面标题 */
.page-header {
  margin-bottom: 24px;
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
  color: #409eff;
  font-size: 32px;
}

.page-subtitle {
  margin: 0;
  color: #86909c;
  font-size: 14px;
}

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-pending .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-approved .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-rejected .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #86909c;
  margin-top: 4px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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

/* 分享卡片 */
.share-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.share-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 1px solid #e5e6eb;
}

.share-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border-color: #409eff;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.favicon-wrapper {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  overflow: hidden;
  background: #f2f3f5;
}

.favicon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
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
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.bookmark-info {
  flex: 1;
  min-width: 0;
}

.bookmark-title {
  font-size: 15px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 6px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-url {
  font-size: 12px;
  color: #86909c;
}

.card-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #86909c;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.reject-reason-box {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: #cf1322;
}

.reject-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f2f3f5;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .my-shares-view {
    padding: 16px;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }

  .share-cards {
    grid-template-columns: 1fr;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
