<!-- front/src/views/admin/ShareAdminView.vue -->
<template>
  <div class="share-admin-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><DocumentChecked /></el-icon>
          分享审核管理
        </h1>
        <p class="page-subtitle">审核用户提交的书签分享申请，维护社区内容质量</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card stat-pending">
        <div class="stat-icon">
          <el-icon :size="24"><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
        <el-tag v-if="stats.pending > 0" class="stat-badge" type="warning" effect="dark">
          需处理
        </el-tag>
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

      <div class="stat-card stat-takendown">
        <div class="stat-icon">
          <el-icon :size="24"><Delete /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.takenDown }}</div>
          <div class="stat-label">已下架</div>
        </div>
      </div>
    </div>

    <!-- Tab切换和工具栏 -->
    <div class="toolbar">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="admin-tabs">
        <el-tab-pane name="pending">
          <template #label>
            <span class="tab-label">
              <el-icon><Clock /></el-icon>
              待审核
              <el-badge v-if="stats.pending > 0" :value="stats.pending" :max="99" class="tab-badge" />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="approved">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleCheck /></el-icon>
              已通过
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="rejected">
          <template #label>
            <span class="tab-label">
              <el-icon><CircleClose /></el-icon>
              已驳回
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="taken_down">
          <template #label>
            <span class="tab-label">
              <el-icon><Delete /></el-icon>
              已下架
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>

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
      :description="getEmptyDescription()"
    >
      <template #image>
        <el-icon :size="80" color="#909399"><Document /></el-icon>
      </template>
    </el-empty>

    <!-- 分享列表 -->
    <el-card v-else class="list-card" shadow="never">
      <el-table
        :data="shares"
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#fafafa', color: '#606266', fontWeight: '600' }"
      >
        <el-table-column label="书签信息" min-width="280">
          <template #default="{ row }">
            <div class="bookmark-info">
              <div class="favicon-wrapper">
                <img
                  v-if="row.bookmark_favicon"
                  :src="row.bookmark_favicon"
                  :alt="row.bookmark_title"
                  class="favicon-img"
                />
                <div v-else class="favicon-default">
                  <span class="favicon-letter">{{ getFirstLetter(row.bookmark_title) }}</span>
                </div>
              </div>
              <div class="info-content">
                <div class="bookmark-title" :title="row.bookmark_title">
                  {{ row.bookmark_title }}
                </div>
                <el-link
                  :href="row.bookmark_url"
                  target="_blank"
                  type="primary"
                  :underline="false"
                  class="bookmark-url"
                >
                  {{ row.bookmark_url }}
                </el-link>
                <div v-if="row.bookmark_description" class="bookmark-desc">
                  {{ row.bookmark_description }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="分享用户" width="120">
          <template #default="{ row }">
            <div class="user-info">
              <el-avatar :size="28" class="user-avatar">
                {{ row.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span>{{ row.username }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              {{ formatTime(row.submitted_at) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="审核时间" width="160">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon v-if="row.reviewed_at"><Check /></el-icon>
              {{ formatTime(row.reviewed_at) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="审核人" width="100">
          <template #default="{ row }">
            {{ row.reviewer_username || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <template v-if="['pending', 'reviewing'].includes(row.status)">
                <el-button
                  size="small"
                  type="success"
                  @click="handleApprove(row)"
                >
                  <el-icon><Select /></el-icon>
                  通过
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  @click="handleReject(row)"
                >
                  <el-icon><CloseBold /></el-icon>
                  驳回
                </el-button>
              </template>

              <el-button
                v-if="row.status === 'approved'"
                size="small"
                type="warning"
                plain
                @click="handleTakeDown(row)"
              >
                <el-icon><Delete /></el-icon>
                下架
              </el-button>

              <el-button
                v-if="row.reject_reason"
                size="small"
                text
                type="primary"
                @click="showRejectReason(row)"
              >
                查看原因
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadShares"
          @current-change="loadShares"
        />
      </div>
    </el-card>

    <!-- 驳回对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="驳回分享申请"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <div class="bookmark-preview">
          <h4>书签信息</h4>
          <div class="preview-item">
            <span class="label">标题：</span>
            <span class="value">{{ currentShare?.bookmark_title }}</span>
          </div>
          <div class="preview-item">
            <span class="label">网址：</span>
            <el-link :href="currentShare?.bookmark_url" target="_blank" type="primary">
              {{ currentShare?.bookmark_url }}
            </el-link>
          </div>
          <div class="preview-item">
            <span class="label">用户：</span>
            <span class="value">{{ currentShare?.username }}</span>
          </div>
        </div>

        <el-form :model="rejectForm" label-position="top" class="reject-form">
          <el-form-item label="驳回原因" required>
            <el-input
              v-model="rejectForm.reject_reason"
              type="textarea"
              :rows="4"
              placeholder="请输入驳回原因，将展示给用户（必填）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          <el-form-item label="审核备注（可选）">
            <el-input
              v-model="rejectForm.review_note"
              type="textarea"
              :rows="2"
              placeholder="内部备注，仅管理员可见"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="confirmReject">
          确认驳回
        </el-button>
      </template>
    </el-dialog>

    <!-- 下架对话框 -->
    <el-dialog
      v-model="takeDownDialogVisible"
      title="下架已通过的分享"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-alert
          title="下架后该分享将不再展示在官方分享页面"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <el-form :model="takeDownForm" label-position="top">
          <el-form-item label="下架原因" required>
            <el-input
              v-model="takeDownForm.reason"
              type="textarea"
              :rows="4"
              placeholder="请输入下架原因（违规内容、质量问题等）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="takeDownDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="submitting" @click="confirmTakeDown">
          确认下架
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DocumentChecked, Clock, CircleCheck, CircleClose, Delete,
  Refresh, Loading, Check, Select, CloseBold
} from '@element-plus/icons-vue'
import { getPendingShares, reviewShare, takeDownShare } from '@/api/share'
import type { ShareRecord } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const shares = ref<ShareRecord[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const activeTab = ref('pending')

// 统计数据
const stats = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
  takenDown: 0
})

// 当前操作的分享
const currentShare = ref<ShareRecord | null>(null)

// 驳回对话框
const rejectDialogVisible = ref(false)
const rejectForm = ref({
  share_id: 0,
  reject_reason: '',
  review_note: ''
})

// 下架对话框
const takeDownDialogVisible = ref(false)
const takeDownForm = ref({
  share_id: 0,
  reason: ''
})

// Tab切换
const handleTabChange = (tab: string) => {
  currentPage.value = 1
  loadShares()
}

// 加载分享列表
const loadShares = async () => {
  loading.value = true
  try {
    const res = await getPendingShares({
      page: currentPage.value,
      page_size: pageSize.value,
      status: activeTab.value
    })
    shares.value = res.items
    total.value = res.total

    // 更新统计数据（简化版，实际应该从后端获取）
    if (activeTab.value === 'pending') {
      stats.value.pending = res.total
    } else if (activeTab.value === 'approved') {
      stats.value.approved = res.total
    } else if (activeTab.value === 'rejected') {
      stats.value.rejected = res.total
    } else if (activeTab.value === 'taken_down') {
      stats.value.takenDown = res.total
    }
  } catch (error) {
    ElMessage.error('加载分享列表失败')
  } finally {
    loading.value = false
  }
}

// 通过审核
const handleApprove = async (share: ShareRecord) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过「${share.bookmark_title}」的分享申请吗？`,
      '通过审核',
      {
        confirmButtonText: '确定通过',
        cancelButtonText: '取消',
        type: 'success'
      }
    )

    submitting.value = true
    await reviewShare({
      share_id: share.id,
      status: 'approved',
      review_note: '审核通过'
    })
    ElMessage.success('审核通过，该分享已展示在官方页面')
    loadShares()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

// 打开驳回对话框
const handleReject = (share: ShareRecord) => {
  currentShare.value = share
  rejectForm.value = {
    share_id: share.id,
    reject_reason: '',
    review_note: ''
  }
  rejectDialogVisible.value = true
}

// 确认驳回
const confirmReject = async () => {
  if (!rejectForm.value.reject_reason.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }

  try {
    submitting.value = true
    await reviewShare({
      ...rejectForm.value,
      status: 'rejected'
    })
    ElMessage.success('已驳回')
    rejectDialogVisible.value = false
    loadShares()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 打开下架对话框
const handleTakeDown = (share: ShareRecord) => {
  currentShare.value = share
  takeDownForm.value = {
    share_id: share.id,
    reason: ''
  }
  takeDownDialogVisible.value = true
}

// 确认下架
const confirmTakeDown = async () => {
  if (!takeDownForm.value.reason.trim()) {
    ElMessage.warning('请填写下架原因')
    return
  }

  try {
    submitting.value = true
    await takeDownShare(takeDownForm.value.share_id, takeDownForm.value.reason)
    ElMessage.success('已下架')
    takeDownDialogVisible.value = false
    loadShares()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

// 查看驳回原因
const showRejectReason = (share: ShareRecord) => {
  ElMessageBox.alert(share.reject_reason, '驳回原因', {
    confirmButtonText: '知道了',
    type: 'warning'
  })
}

// 状态标签类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'warning',
    reviewing: '',
    approved: 'success',
    rejected: 'danger',
    taken_down: 'info'
  }
  return typeMap[status] || 'info'
}

// 状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    reviewing: '审核中',
    approved: '已通过',
    rejected: '已驳回',
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

// 空状态描述
const getEmptyDescription = () => {
  const descMap: Record<string, string> = {
    pending: '暂无待审核的分享',
    approved: '暂无已通过的分享',
    rejected: '暂无已驳回的分享',
    taken_down: '暂无已下架的分享'
  }
  return descMap[activeTab.value] || '暂无数据'
}

onMounted(() => {
  loadShares()
})
</script>

<style scoped>
.share-admin-view {
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
  position: relative;
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

.stat-takendown .stat-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #606266;
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

.stat-badge {
  position: absolute;
  top: 12px;
  right: 12px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 0 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.admin-tabs {
  flex: 1;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-badge {
  margin-left: 4px;
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

/* 列表卡片 */
.list-card {
  border-radius: 12px;
}

.bookmark-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.favicon-wrapper {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 8px;
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
  font-size: 16px;
  font-weight: 700;
  color: white;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.bookmark-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-url {
  font-size: 12px;
  color: #86909c;
  display: block;
  margin-bottom: 4px;
}

.bookmark-desc {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 12px;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

/* 分页 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 对话框样式 */
.dialog-content {
  padding: 10px 0;
}

.bookmark-preview {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.bookmark-preview h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #1d2129;
}

.preview-item {
  margin-bottom: 8px;
  font-size: 13px;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item .label {
  color: #86909c;
  margin-right: 8px;
}

.preview-item .value {
  color: #1d2129;
}

.reject-form {
  margin-top: 16px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .share-admin-view {
    padding: 16px;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
