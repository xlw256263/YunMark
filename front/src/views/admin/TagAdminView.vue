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
        :data="filteredTags"
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
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑标签' : '新增标签'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
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

// 计算属性
const filteredTags = computed(() => {
  if (!filterCategoryId.value) return tagList.value
  return tagList.value.filter(tag => tag.category_id === filterCategoryId.value)
})

// 方法
const loadTags = async () => {
  loading.value = true
  try {
    const res = await getAdminTags()
    tagList.value = res
  } catch (error) {
    ElMessage.error('加载标签列表失败')
  } finally {
    loading.value = false
  }
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
  // 筛选逻辑在 computed 中处理
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
      ElMessage.error(error.response?.data?.detail || '操作失败')
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
      ElMessage.error(error.response?.data?.detail || '删除失败')
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
</style>
