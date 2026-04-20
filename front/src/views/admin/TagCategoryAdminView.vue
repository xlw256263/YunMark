<template>
  <div class="tag-category-admin">
    <el-card class="header-card">
      <div class="card-header">
        <span class="title">标签分类管理</span>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新增分类
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="categoryList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分类名称" min-width="150">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="100" sortable />
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
      :title="isEdit ? '编辑分类' : '新增分类'"
      width="500px"
      @keydown.enter.prevent
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入分类名称"
            clearable
            @keyup.enter="handleSubmit"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述（可选）"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="0"
            :max="999"
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAdminTagCategories,
  createAdminTagCategory,
  updateAdminTagCategory,
  deleteAdminTagCategory
} from '@/api/admin'
import type { TagCategory } from '@/types'

// 状态
const loading = ref(false)
const submitting = ref(false)
const categoryList = ref<TagCategory[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentCategoryId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const formData = ref({
  name: '',
  description: '',
  sort_order: 0
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

// 方法
const loadCategories = async () => {
  loading.value = true
  try {
    const res = await getAdminTagCategories()
    categoryList.value = res
  } catch (error) {
    ElMessage.error('加载分类列表失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  currentCategoryId.value = null
  formData.value = { name: '', description: '', sort_order: 0 }
  dialogVisible.value = true
}

const showEditDialog = (category: TagCategory) => {
  isEdit.value = true
  currentCategoryId.value = category.id
  formData.value = {
    name: category.name,
    description: category.description || '',
    sort_order: category.sort_order
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value && currentCategoryId.value) {
        await updateAdminTagCategory(currentCategoryId.value, {
          name: formData.value.name,
          description: formData.value.description || null,
          sort_order: formData.value.sort_order
        })
        ElMessage.success('更新成功')
      } else {
        await createAdminTagCategory({
          name: formData.value.name,
          description: formData.value.description || null,
          sort_order: formData.value.sort_order
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await loadCategories()
    } catch (error: any) {
      console.error('操作失败:', error)
      // 错误提示已由响应拦截器统一处理
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (category: TagCategory) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${category.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAdminTagCategory(category.id)
    ElMessage.success('删除成功')
    await loadCategories()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      // 错误提示已由响应拦截器统一处理
    }
  }
}

// 生命周期
onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.tag-category-admin {
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
</style>
