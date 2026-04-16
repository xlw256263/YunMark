import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

/**
 * 检查 JWT Token 是否过期
 */
function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true
    
    // JWT payload 是 Base64Url 编码
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    const exp = payload.exp
    if (!exp) return true
    
    // exp 是秒级时间戳
    const now = Math.floor(Date.now() / 1000)
    return exp < now
  } catch {
    return true
  }
}

export const useUserStore = defineStore('user', () => {
  // ==================== 状态 (State) ====================

  /** JWT 访问令牌 */
  const accessToken = ref(localStorage.getItem('access_token') || '')

  /** 当前用户信息 */
  const userInfo = ref<User | null>(null)

  // ==================== 计算属性 (Getters) ====================

  /** 是否已登录 */
  const isLoggedIn = computed(() => !!accessToken.value)

  /** 用户名 */
  const username = computed(() => userInfo.value?.username || '')

  /** 邮箱 */
  const email = computed(() => userInfo.value?.email || '')

  /** 是否为管理员 */
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  // ==================== 动作 (Actions) ====================

  /**
   * 设置用户信息和 Token
   */
  function setUserInfo(token: string, user: User) {
    accessToken.value = token
    userInfo.value = user

    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(user))
  }

  /**
   * 从 localStorage 恢复用户信息（页面刷新时调用）
   */
  function restoreFromStorage() {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    if (token && userStr) {
      try {
        // 关键修复：检查 Token 是否已过期
        if (isTokenExpired(token)) {
          console.log('[UserStore] Token 已过期，清除本地存储')
          logout()
          return
        }
        
        accessToken.value = token
        userInfo.value = JSON.parse(userStr)
      } catch (error) {
        console.error('恢复用户信息失败:', error)
        logout()
      }
    }
  }

  /**
   * 登出
   */
  function logout() {
    accessToken.value = ''
    userInfo.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  /**
   * 更新用户信息
   */
  function updateUserInfo(user: User) {
    userInfo.value = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  return {
    accessToken,
    userInfo,
    isLoggedIn,
    username,
    email,
    isAdmin,
    setUserInfo,
    restoreFromStorage,
    logout,
    updateUserInfo,
  }
})
