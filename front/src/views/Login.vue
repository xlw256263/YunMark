<template>
  <div class="login-container">
    <div class="login-form">
      <h2>欢迎来到私人精品网页推荐</h2>

      <div v-if="showRegister" class="form-section">
        <h3>注册账号</h3>
        <form @submit.prevent="handleRegister">
          <div class="input-group">
            <label>用户名</label>
            <input
              v-model="registerForm.username"
              type="text"
              placeholder="请输入用户名"
              required
            />
          </div>
          <div class="input-group">
            <label>邮箱</label>
            <input
              v-model="registerForm.email"
              type="email"
              placeholder="请输入邮箱"
              required
            />
          </div>
          <div class="input-group">
            <label>密码</label>
            <input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary">注册</button>
        </form>
      </div>

      <div v-else class="form-section">
        <h3>登录账号</h3>
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <label>邮箱</label>
            <input
              v-model="loginForm.email"
              type="email"
              placeholder="请输入邮箱"
              required
            />
          </div>
          <div class="input-group">
            <label>密码</label>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              required
            />
          </div>
          <button type="submit" class="btn btn-primary">登录</button>
        </form>
      </div>

      <div class="switch-form">
        <p>
          {{ showRegister ? '已有账号？' : '没有账号？' }}
          <a href="#" @click.prevent="toggleForm">
            {{ showRegister ? '去登录' : '去注册' }}
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import request from '@/api/request'

const router = useRouter()
const userStore = useUserStore()

const showRegister = ref(false)
const loading = ref(false)

const loginForm = ref({
  email: '',
  password: ''
})

const registerForm = ref({
  username: '',
  email: '',
  password: ''
})

const toggleForm = () => {
  showRegister.value = !showRegister.value
  // 清空表单
  loginForm.value = { email: '', password: '' }
  registerForm.value = { username: '', email: '', password: '' }
}

const handleLogin = async () => {
  if (!loginForm.value.email || !loginForm.value.password) {
    alert('请填写完整的登录信息')
    return
  }

  loading.value = true
  
  try {
    // 使用 OAuth2 标准格式发送登录请求
    const formData = new FormData()
    formData.append('username', loginForm.value.email)  // OAuth2 要求字段名为 username
    formData.append('password', loginForm.value.password)

    const response = await request.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 保存 token 和用户信息
    userStore.setUserInfo(
      response.access_token,
      response.username,
      response.email
    )

    alert('登录成功！')
    router.push(`/dashboard?username=${response.username}`)
  } catch (error) {
    console.error('登录错误:', error)
    const errorMsg = error.response?.data?.detail || '登录失败，请检查邮箱和密码'
    alert(errorMsg)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    alert('请填写完整的注册信息')
    return
  }

  if (registerForm.value.password.length < 6) {
    alert('密码长度至少为6位')
    return
  }

  loading.value = true
  
  try {
    const response = await request.post('/auth/register', {
      username: registerForm.value.username,
      email: registerForm.value.email,
      password: registerForm.value.password
    })

    alert('注册成功！请登录')
    showRegister.value = false
    registerForm.value = { username: '', email: '', password: '' }
  } catch (error) {
    console.error('注册错误:', error)
    const errorMsg = error.response?.data?.detail || '注册失败，请稍后重试'
    alert(errorMsg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.form-section h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.switch-form {
  text-align: center;
  margin-top: 20px;
}

.switch-form p {
  color: #666;
}

.switch-form a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.switch-form a:hover {
  text-decoration: underline;
}
</style>