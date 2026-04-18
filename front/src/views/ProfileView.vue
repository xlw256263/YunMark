<template>
  <div class="profile-container">
    <div class="profile-card-wrapper">
      <div class="profile-header">
        <h2 class="header-title">
          <el-icon :size="28" class="header-icon"><User /></el-icon>
          个人中心
        </h2>
      </div>

      <div class="profile-card">
        <div class="avatar-section">
          <el-avatar :size="120" :src="displayAvatar" class="user-avatar" @click="triggerUpload">
            <el-icon :size="60"><User /></el-icon>
          </el-avatar>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleAvatarChange"
            accept="image/jpeg,image/png,image/gif,image/webp"
            class="avatar-uploader"
            style="display: none;"
          >
            <el-button type="primary" size="small" circle class="upload-btn">
              <el-icon><Camera /></el-icon>
            </el-button>
          </el-upload>
        </div>

        <div class="user-info">
          <h3 class="username">{{ userStore.userInfo?.username }}</h3>
          <p class="email">{{ userStore.userInfo?.email }}</p>
          <el-tag v-if="userStore.userInfo?.bio" size="small" class="bio-tag">
            {{ userStore.userInfo.bio }}
          </el-tag>
        </div>

        <div class="menu-list">
          <div class="menu-item" @click="showBasicInfoDialog">
            <el-icon><User /></el-icon>
            <span>基本信息</span>
          </div>
          <div class="menu-item" @click="showPasswordDialog">
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </div>
          <div class="menu-item" @click="showSecurityDialog">
            <el-icon><Key /></el-icon>
            <span>账号安全</span>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="basicInfoVisible" title="基本信息" width="500px" :close-on-click-modal="false">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ userStore.userInfo?.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userStore.userInfo?.email }}</el-descriptions-item>
        <el-descriptions-item label="个人简介">{{ userStore.userInfo?.bio || '暂无简介' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="startEditBasic">编辑资料</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editBasicVisible" title="编辑资料" width="500px" :close-on-click-modal="false">
      <el-form ref="basicFormRef" :model="editForm" :rules="basicRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="简介" prop="bio">
          <el-input v-model="editForm.bio" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editBasicVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveBasic" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="passwordVisible" title="修改密码" width="450px" :close-on-click-modal="false">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="changingPassword">确认修改</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="securityVisible" title="账号安全" width="450px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="注册时间">{{ formatDate(userStore.userInfo?.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="账号状态">
          <el-tag :type="userStore.userInfo?.is_active === 1 ? 'success' : 'danger'" size="small">
            {{ userStore.userInfo?.is_active === 1 ? '正常' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户角色">
          <el-tag :type="userStore.userInfo?.role === 'admin' ? 'warning' : 'info'" size="small">
            {{ userStore.userInfo?.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <el-alert title="注销账号后，所有数据将被清空且无法恢复" type="error" :closable="false" show-icon>
        <template #default>
          <el-popconfirm title="确定要注销账号吗？此操作不可恢复！" @confirm="handleDeleteAccount">
            <template #reference>
              <el-button type="danger" size="small" style="margin-top: 12px;">注销账号</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-alert>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Camera, Lock, Key } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { updateProfile, changePassword, uploadAvatar, deleteUser } from '@/api/user'
import type { UserProfileUpdate, PasswordChange, UploadFile, FormInstance, FormRules } from 'element-plus'

const userStore = useUserStore()
const saving = ref(false)
const changingPassword = ref(false)
const uploadRef = ref()
const basicFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const basicInfoVisible = ref(false)
const editBasicVisible = ref(false)
const passwordVisible = ref(false)
const securityVisible = ref(false)

const editForm = reactive({ username: '', email: '', bio: '' })
const passwordForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const basicRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 2, max: 50, message: '用户名长度为 2-50 个字符', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
  bio: [{ max: 500, message: '个人简介不能超过 500 个字符', trigger: 'blur' }]
}

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, max: 100, message: '密码长度为 6-100 个字符', trigger: 'blur' }],
  confirm_password: [{ required: true, message: '请再次输入新密码', trigger: 'blur' }, {
    validator: (rule: any, value: string, callback: any) => {
      if (value !== passwordForm.new_password) callback(new Error('两次输入的密码不一致'))
      else callback()
    }, trigger: 'blur'
  }]
}

const displayAvatar = computed(() => {
  const avatar = userStore.userInfo?.avatar
  if (!avatar) return ''
  if (avatar.startsWith('http')) return avatar
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  return `${baseUrl.replace('/api/v1', '')}${avatar}`
})

const triggerUpload = () => {
  const uploadEl = uploadRef.value?.$el?.querySelector('input[type="file"]')
  if (uploadEl) {
    uploadEl.click()
  }
}

const showBasicInfoDialog = () => { basicInfoVisible.value = true }
const showPasswordDialog = () => { passwordVisible.value = true }
const showSecurityDialog = () => { securityVisible.value = true }

const startEditBasic = () => {
  editForm.username = userStore.userInfo?.username || ''
  editForm.email = userStore.userInfo?.email || ''
  editForm.bio = userStore.userInfo?.bio || ''
  basicInfoVisible.value = false
  editBasicVisible.value = true
}

const handleSaveBasic = async () => {
  if (!basicFormRef.value) return
  await basicFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const data: UserProfileUpdate = { username: editForm.username, email: editForm.email, bio: editForm.bio }
      const response = await updateProfile(data)
      userStore.updateUserInfo(response)
      ElMessage.success('保存成功')
      editBasicVisible.value = false
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const handleAvatarChange = async (file: UploadFile) => {
  if (!file.raw) return
  const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.raw.type)
  const isLt5M = file.raw.size / 1024 / 1024 < 5
  if (!isImage) { ElMessage.error('只支持 JPG、PNG、GIF、WEBP 格式'); return }
  if (!isLt5M) { ElMessage.error('图片大小不能超过 5MB'); return }

  try {
    saving.value = true
    const response = await uploadAvatar(file.raw)
    const updatedUser = { ...userStore.userInfo!, avatar: response.avatar_url }
    userStore.updateUserInfo(updatedUser)
    ElMessage.success('头像上传成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '头像上传失败')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    changingPassword.value = true
    try {
      const data: PasswordChange = { old_password: passwordForm.old_password, new_password: passwordForm.new_password }
      await changePassword(data)
      ElMessage.success('密码修改成功，请重新登录')
      passwordVisible.value = false
      userStore.logout()
      setTimeout(() => { window.location.href = '/' }, 1500)
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '密码修改失败')
    } finally {
      changingPassword.value = false
    }
  })
}

const handleDeleteAccount = async () => {
  try {
    await deleteUser()
    ElMessage.success('账号已注销')
    userStore.logout()
    setTimeout(() => { window.location.href = '/' }, 1500)
  } catch (error: any) {
    ElMessage.error('注销失败')
  }
}

const formatDate = (dateStr?: string) => dateStr ? new Date(dateStr).toLocaleString('zh-CN') : '未知'

</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 20px;
  min-height: calc(100vh - 60px);
  background: #0f1923;
}

.profile-card-wrapper {
  width: 100%;
  max-width: 400px;
}

.profile-header {
  text-align: center;
  margin-bottom: 30px;
}

.header-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.header-icon {
  color: #818cf8;
}

.profile-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px 30px;
  color: white;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
}

.avatar-section {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.user-avatar {
  border: 4px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar:hover { transform: scale(1.05); border-color: rgba(255, 255, 255, 0.7); }

.user-info { text-align: center; margin-bottom: 32px; }
.username { font-size: 24px; font-weight: 600; margin: 0 0 8px 0; color: white; }
.email { font-size: 14px; color: rgba(255, 255, 255, 0.85); margin: 0 0 12px 0; }
.bio-tag { background: rgba(255, 255, 255, 0.2) !important; border: none !important; color: white !important; }

.menu-list { display: flex; flex-direction: column; gap: 12px; }

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
  font-weight: 500;
  color: white;
}

.menu-item:hover { background: rgba(255, 255, 255, 0.25); transform: translateX(4px); }
.menu-item .el-icon { font-size: 20px; }
</style>
