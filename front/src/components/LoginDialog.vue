<template>
  <el-dialog
    v-model="visible"
    :width="360"
    :show-close="false"
    :close-on-click-modal="true"
    class="compact-login-dialog"
    align-center
  >
    <!-- 自定义关闭按钮 -->
    <div class="dialog-close" @click="close">
      <el-icon :size="18"><Close /></el-icon>
    </div>

    <!-- 弹窗内容 -->
    <div class="dialog-content">
      <!-- 标题区域 -->
      <div class="header-section">
        <h2 class="dialog-title">{{ isRegister ? '创建账号' : '欢迎回来' }}</h2>
        <p class="dialog-subtitle">{{ isRegister ? '开始您的收藏之旅' : '登录以继续' }}</p>
      </div>

      <!-- 全局错误提示 -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="true"
        show-icon
        class="error-alert"
        @close="errorMessage = ''"
      />

      <!-- 登录表单 -->
      <div v-if="!isRegister" class="form-section">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          class="auth-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="loginForm.email"
              placeholder="name@example.com"
              size="default"
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="输入密码"
              size="default"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
        </el-form>

        <!-- 登录按钮 -->
        <el-button
          type="primary"
          class="submit-btn"
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </el-button>

        <!-- 切换链接 -->
        <div class="switch-link">
          <span>还没有账号？</span>
          <a class="link-text" @click="toggleMode">立即注册</a>
        </div>
      </div>

      <!-- 注册表单 -->
      <div v-else class="form-section">
        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          label-position="top"
          class="auth-form"
          @submit.prevent="handleRegister"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="用户名"
              size="default"
              clearable
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="registerForm.email"
              placeholder="name@example.com"
              size="default"
              clearable
              @keyup.enter="handleRegister"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="至少6位"
              size="default"
              show-password
              @keyup.enter="handleRegister"
            />
          </el-form-item>
        </el-form>

        <!-- 注册按钮 -->
        <el-button
          type="primary"
          class="submit-btn"
          :loading="loading"
          @click="handleRegister"
        >
          注册
        </el-button>

        <!-- 切换链接 -->
        <div class="switch-link">
          <span>已有账号？</span>
          <a class="link-text" @click="toggleMode">去登录</a>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { login, register } from '@/api/auth'
import { getCurrentUser } from '@/api/user'
import type { AxiosError } from 'axios'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 弹窗显示状态
const visible = ref(false)

// 是否为注册模式
const isRegister = ref(false)

// 加载状态
const loading = ref(false)

// 错误信息
const errorMessage = ref('')

// 表单引用
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

// 登录表单数据
const loginForm = ref({
  email: '',
  password: '',
})

// 注册表单数据
const registerForm = ref({
  username: '',
  email: '',
  password: '',
})

// 登录表单验证规则
const loginRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' },
  ],
}

// 注册表单验证规则
const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度为2-20个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' },
  ],
}

/**
 * 解析错误信息
 */
const getErrorMessage = (error: AxiosError) => {
  const data = error.response?.data as any

  // 如果有 detail 字段，直接返回
  if (data?.detail) {
    return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
  }

  // 如果有 message 字段
  if (data?.message) {
    return data.message
  }

  // 默认错误信息
  return '操作失败，请稍后重试'
}

/**
 * 切换登录/注册模式
 */
const toggleMode = () => {
  isRegister.value = !isRegister.value
  errorMessage.value = ''
  loginFormRef.value?.clearValidate()
  registerFormRef.value?.clearValidate()
}

/**
 * 处理登录
 */
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    errorMessage.value = ''

    try {
      // 调用登录 API，直接返回 token 和用户基本信息
      const response = await login(loginForm.value.email, loginForm.value.password)

      console.log('登录响应:', response)

      // 先保存 token
      localStorage.setItem('access_token', response.access_token)

      // 获取完整的用户信息（包含 role）
      const userInfo = await getCurrentUser()

      console.log('用户信息:', userInfo)

      // 保存用户信息到 Store
      userStore.setUserInfo(response.access_token, userInfo)

      console.log('Token 已保存:', response.access_token)
      console.log('localStorage token:', localStorage.getItem('access_token'))

      ElMessage.success('登录成功！')
      visible.value = false

      // 跳转到重定向页面或首页
      const redirect = route.query.redirect as string
      router.push(redirect || '/')
    } catch (error: any) {
      // 显示具体错误信息
      errorMessage.value = getErrorMessage(error)
    } finally {
      loading.value = false
    }
  })
}

/**
 * 处理注册
 */
const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    errorMessage.value = ''

    try {
      // 调用注册 API
      await register(registerForm.value)

      ElMessage.success('注册成功！请登录')

      // 切换到登录模式
      isRegister.value = false
      loginForm.value.email = registerForm.value.email
      registerForm.value = { username: '', email: '', password: '' }
      errorMessage.value = ''
    } catch (error: any) {
      // 显示具体错误信息
      errorMessage.value = getErrorMessage(error)
    } finally {
      loading.value = false
    }
  })
}

/**
 * 打开弹窗
 */
const open = () => {
  visible.value = true
  errorMessage.value = ''
}

/**
 * 关闭弹窗
 */
const close = () => {
  visible.value = false
  errorMessage.value = ''
}

// 监听 URL 中的 login 参数
watch(
  () => route.query.login,
  (val) => {
    if (val === '1') {
      open()
    }
  },
  { immediate: true }
)

// 暴露方法给父组件
defineExpose({
  open,
  close,
})
</script>

<style scoped>
/* ========== 关闭按钮 ========== */
.dialog-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94A3B8;
  transition: all 0.2s;
  z-index: 10;
}

.dialog-close:hover {
  background: #F1F5F9;
  color: #1E293B;
}

/* ========== 内容区域 ========== */
.dialog-content {
  padding: 0;
}

/* ========== 错误提示 ========== */
.error-alert {
  margin-bottom: 16px;
  font-size: 13px;
}

/* ========== 头部区域 ========== */
.header-section {
  margin-bottom: 20px;
}

.dialog-title {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 20px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 4px 0;
  letter-spacing: -0.3px;
}

.dialog-subtitle {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 13px;
  font-weight: 400;
  color: #94A3B8;
  margin: 0;
}

/* ========== 表单区域 ========== */
.form-section {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
}

.auth-form {
  margin-bottom: 0;
}

/* 表单项间距 */
.auth-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

/* 标签样式 */
.auth-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #1E293B;
  padding-bottom: 6px;
  line-height: 1.4;
}

/* ========== 登录/注册按钮 ========== */
.submit-btn {
  width: 100%;
  height: 40px;
  margin-top: 20px;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 14px;
  font-weight: 600;
  border-radius: 32px;
  background: #0F172A;
  border: none;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: #1E293B;
  transform: translateY(-1px);
}

.submit-btn:active {
  transform: translateY(0);
}

/* ========== 切换链接 ========== */
.switch-link {
  text-align: center;
  margin-top: 16px;
  font-size: 13px;
  color: #94A3B8;
}

.switch-link span {
  margin-right: 4px;
}

.link-text {
  color: #64748B;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
  transition: color 0.2s;
  font-weight: 500;
}

.link-text:hover {
  color: #1E293B;
}
</style>

<style>
/* ========== 全局 Dialog 样式 ========== */
.compact-login-dialog {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.12);
  background: #FFFFFF;
}

.compact-login-dialog .el-dialog__header {
  padding: 0;
  margin: 0;
}

.compact-login-dialog .el-dialog__body {
  padding: 24px 20px;
}

/* ========== 输入框样式 - 彻底移除内边框 ========== */
.compact-login-dialog .el-input__wrapper {
  background: #FFFFFF !important;
  border-radius: 10px;
  padding: 10px 14px;
  transition: all 0.2s ease;
  /* 默认状态：细边框 */
  border: 1px solid #E2E8F0;
  /* 移除所有内阴影 */
  box-shadow: none !important;
}

.compact-login-dialog .el-input__wrapper:hover {
  border-color: #CBD5E1;
}

/* 聚焦状态：只保留外发光，完全移除内边框 */
.compact-login-dialog .el-input__wrapper.is-focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* 错误状态 */
.compact-login-dialog .el-input__wrapper.is-error {
  border-color: #EF4444;
  box-shadow: none !important;
}

.compact-login-dialog .el-input__inner {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 14px;
  color: #1E293B;
  font-weight: 400;
  /* 确保输入框本身没有边框 */
  border: none !important;
  box-shadow: none !important;
}

.compact-login-dialog .el-input__inner::placeholder {
  color: #94A3B8;
  font-weight: 400;
}

/* 清除图标和显示密码图标 */
.compact-login-dialog .el-input__clear,
.compact-login-dialog .el-input__suffix-inner {
  color: #94A3B8;
}

/* 错误提示 */
.compact-login-dialog .el-form-item__error {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro', sans-serif;
  font-size: 12px;
  color: #EF4444;
  padding-top: 4px;
}

/* Alert 样式覆盖 */
.compact-login-dialog .el-alert {
  border-radius: 8px;
  padding: 12px 16px;
}

.compact-login-dialog .el-alert__title {
  font-size: 13px;
}
</style>
