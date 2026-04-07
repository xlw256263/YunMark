import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const email = ref(localStorage.getItem('email') || '')

  function setUserInfo(newToken, newUsername, newEmail) {
    token.value = newToken
    username.value = newUsername
    email.value = newEmail
    localStorage.setItem('token', newToken)
    localStorage.setItem('username', newUsername)
    localStorage.setItem('email', newEmail)
  }

  function logout() {
    token.value = ''
    username.value = ''
    email.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('email')
  }

  return {
    token,
    username,
    email,
    setUserInfo,
    logout
  }
})
