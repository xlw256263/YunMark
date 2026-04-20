<template>
  <div class="tag-admin">
    <el-card class="header-card">
      <div class="card-header">
        <span class="title">标签管理</span>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新增标签
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <!-- 筛选器 -->
      <div class="filter-bar">
        <el-select
          v-model="filterCategoryId"
          placeholder="按分类筛选"
          clearable
          @change="handleFilterChange"
          style="width: 200px"
        >
          <el-option label="全部分类" :value="null" />
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
      </div>

      <el-table
        :data="tagList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="标签名称" min-width="150">
          <template #default="{ row }">
            <el-tag>{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="所属分类" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="row.category" type="success">{{ row.category.name }}</el-tag>
            <el-tag v-else type="info">未分类</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="120" sortable>
          <template #default="{ row }">
            <el-tag :type="row.usage_count > 0 ? 'success' : 'info'">
              {{ row.usage_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              link
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              link
              :disabled="row.usage_count > 0"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadTags"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑标签' : '新增标签'"
      width="500px"
      @keydown.enter.prevent
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="标签分类" prop="category_id">
          <el-select
            v-model="formData.category_id"
            placeholder="请选择分类（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入标签名称"
            clearable
            @keyup.enter="handleSubmit"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAdminTags,
  createAdminTag,
  updateAdminTag,
  deleteAdminTag,
  getAdminTagCategories
} from '@/api/admin'
import type { Tag, TagCategory } from '@/types'

// 状态
const loading = ref(false)
const submitting = ref(false)
const tagList = ref<Tag[]>([])
const categories = ref<TagCategory[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentTagId = ref<number | null>(null)
const filterCategoryId = ref<number | null>(null)
const formRef = ref<FormInstance>()

// 分页状态
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formData = ref({
  name: '',
  category_id: null as number | null
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 方法
const loadTags = async () => {
  loading.value = true
  try {
    const res = await getAdminTags({
      page: currentPage.value,
      page_size: pageSize.value,
      category_id: filterCategoryId.value
    })
    tagList.value = res.items
    total.value = res.total
    currentPage.value = res.page
    pageSize.value = res.page_size
  } catch (error) {
    ElMessage.error('加载标签列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadTags()
}

const loadCategories = async () => {
  try {
    const res = await getAdminTagCategories()
    categories.value = res
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  loadTags()
}

const showCreateDialog = () => {
  isEdit.value = false
  currentTagId.value = null
  formData.value = { name: '', category_id: null }
  dialogVisible.value = true
}

const showEditDialog = (tag: Tag) => {
  isEdit.value = true
  currentTagId.value = tag.id
  formData.value = {
    name: tag.name,
    category_id: tag.category_id || null
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value && currentTagId.value) {
        await updateAdminTag(currentTagId.value, formData.value.name, formData.value.category_id)
        ElMessage.success('更新成功')
      } else {
        await createAdminTag({
          name: formData.value.name,
          category_id: formData.value.category_id
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await loadTags()
    } catch (error: any) {
      console.error('操作失败:', error)
      // 错误提示已由响应拦截器统一处理
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (tag: Tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAdminTag(tag.id)
    ElMessage.success('删除成功')
    await loadTags()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 错误提示已由响应拦截器统一处理
    }
  }
}

// 生命周期
onMounted(() => {
  loadTags()
  loadCategories()
})
</script>

<style scoped>
.tag-admin {
  height: 100%;
}

.header-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.table-card {
  min-height: calc(100vh - 240px);
}

.filter-bar {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
