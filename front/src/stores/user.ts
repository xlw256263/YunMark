import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return true
    
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    const exp = payload.exp
    if (!exp) return true
    
    const now = Math.floor(Date.now() / 1000)
    return exp < now
  } catch {
    return true
  }
}

export const useUserStore = defineStore('user', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref<User | null>(null)
  const shouldShowLoginDialog = ref(false)

  const isLoggedIn = computed(() => !!accessToken.value)
  const username = computed(() => userInfo.value?.username || '')
  const email = computed(() => userInfo.value?.email || '')
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  /**
   * 登录时设置用户信息和 Token
   */
  function setUserInfoWithToken(token: string, user: User) {
    accessToken.value = token
    userInfo.value = user

    localStorage.setItem('access_token', token)
    localStorage.setItem('user', JSON.stringify(user))
  }

  /**
   * 从 localStorage 恢复用户信息
   */
  function restoreFromStorage() {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')

    if (token && userStr) {
      try {
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
   * 更新用户信息（个人中心编辑后调用）
   */
  function updateUserInfo(user: User) {
    userInfo.value = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  /**
   * 触发显示登录弹窗
   */
  function triggerLoginDialog() {
    shouldShowLoginDialog.value = true
  }

  /**
   * 关闭登录弹窗
   */
  function closeLoginDialog() {
    shouldShowLoginDialog.value = false
  }

  return {
    accessToken,
    userInfo,
    isLoggedIn,
    username,
    email,
    isAdmin,
    shouldShowLoginDialog,
    setUserInfoWithToken,
    restoreFromStorage,
    logout,
    updateUserInfo,
    triggerLoginDialog,
    closeLoginDialog,
  }
})
