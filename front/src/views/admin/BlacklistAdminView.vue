<template>
  <div class="blacklist-admin-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon class="title-icon"><CircleClose /></el-icon>
          黑名单管理
        </h1>
        <p class="page-subtitle">管理禁止分享的域名或关键字规则</p>
      </div>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加规则
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ blacklist.length }}</div>
          <div class="stat-label">规则总数</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && blacklist.length === 0" class="loading-wrapper">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="blacklist.length === 0"
      description="暂无黑名单规则"
    >
      <template #image>
        <el-icon :size="80" color="#909399"><CircleClose /></el-icon>
      </template>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加第一条规则
      </el-button>
    </el-empty>

    <!-- 黑名单列表 -->
    <el-card v-else class="list-card" shadow="never">
      <el-table
        :data="blacklist"
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#fafafa', color: '#606266', fontWeight: '600' }"
      >
        <el-table-column label="ID" width="80">
          <template #default="{ row }">
            <span class="id-text">#{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column label="匹配规则" min-width="250">
          <template #default="{ row }">
            <div class="pattern-cell">
              <el-tag type="danger" effect="light">
                {{ row.pattern }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="描述" min-width="200">
          <template #default="{ row }">
            <span class="description-text">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              {{ formatTime(row.created_at) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="danger"
              plain
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加黑名单规则"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="addForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="confirmAdd"
      >
        <el-form-item label="匹配规则" prop="pattern">
          <el-input
            v-model="addForm.pattern"
            placeholder="输入域名或关键字，如：example.com 或 违规词"
            maxlength="255"
            show-word-limit
            @keyup.enter="confirmAdd"
          />
          <div class="form-tip">
            支持域名（如 example.com）或关键字（如 广告、赌博）
          </div>
        </el-form-item>
        <el-form-item label="描述（可选）" prop="description">
          <el-input
            v-model="addForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入规则说明（选填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="confirmAdd">
          确认添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { CircleClose, Plus, Loading, Clock, Delete, Document } from '@element-plus/icons-vue'
import { getBlacklist, createBlacklist, deleteBlacklist, type BlacklistItem } from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const blacklist = ref<BlacklistItem[]>([])
const addDialogVisible = ref(false)
const formRef = ref<FormInstance>()

const addForm = ref({
  pattern: '',
  description: ''
})

const rules: FormRules = {
  pattern: [
    { required: true, message: '请输入匹配规则', trigger: 'blur' },
    { min: 1, max: 255, message: '规则长度在 1 到 255 个字符', trigger: 'blur' }
  ]
}

// 加载黑名单列表
const loadBlacklist = async () => {
  loading.value = true
  try {
    const res = await getBlacklist()
    blacklist.value = res
  } catch (error: any) {
    console.error('加载黑名单失败:', error)
    // 错误提示已由响应拦截器统一处理
  } finally {
    loading.value = false
  }
}

// 打开添加对话框
const handleAdd = () => {
  addForm.value = {
    pattern: '',
    description: ''
  }
  addDialogVisible.value = true
}

// 确认添加
const confirmAdd = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      submitting.value = true
      await createBlacklist(addForm.value)
      ElMessage.success('添加成功')
      addDialogVisible.value = false
      loadBlacklist()
    } catch (error: any) {
      if (error.response?.status === 400) {
        ElMessage.warning('该规则已存在')
      } else {
        console.error('添加失败:', error)
        // 错误提示已由响应拦截器统一处理
      }
    } finally {
      submitting.value = false
    }
  })
}

// 删除规则
const handleDelete = async (item: BlacklistItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则「${item.pattern}」吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteBlacklist(item.id)
    ElMessage.success('删除成功')
    loadBlacklist()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 错误提示已由响应拦截器统一处理
    }
  }
}

// 格式化时间
const formatTime = (time: string) => {
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
  loadBlacklist()
})
</script>

<style scoped>
.blacklist-admin-view {
  padding: 24px 32px;
  background: #f5f7fa;
  min-height: calc(100vh - 73px);
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
  color: #f56c6c;
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

.id-text {
  font-family: monospace;
  color: #86909c;
  font-size: 13px;
}

.pattern-cell {
  display: flex;
  align-items: center;
}

.description-text {
  color: #606266;
  font-size: 14px;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

/* 表单提示 */
.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .blacklist-admin-view {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
