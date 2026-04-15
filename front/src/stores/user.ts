// src/stores/user.ts
/**
 * 用户状态管理 Store
 * 管理用户登录状态、Token 和用户信息
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

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

  /** 是否为管理员（待后端实现） */
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  // ==================== 动作 (Actions) ====================

  /**
   * 设置用户信息和 Token
   * @param token - JWT 访问令牌
   * @param user - 用户信息对象
   */
  function setUserInfo(token: string, user: User) {
    accessToken.value = token
    userInfo.value = user

    // 持久化到 localStorage
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
   * 清除所有用户相关数据
   */
  function logout() {
    accessToken.value = ''
    userInfo.value = null

    // 清除 localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  /**
   * 更新用户信息
   * @param user - 新的用户信息
   */
  function updateUserInfo(user: User) {
    userInfo.value = user
    localStorage.setItem('user', JSON.stringify(user))
  }

  return {
    // 状态
    accessToken,
    userInfo,

    // 计算属性
    isLoggedIn,
    username,
    email,
    isAdmin,

    // 动作
    setUserInfo,
    restoreFromStorage,
    logout,
    updateUserInfo,
  }
})
