import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

interface User {
  id: number
  username: string
  email: string
  avatar: string
  bio: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const response = await api.post('/auth/login', { username, password })
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await fetchUser()
  }

  async function register(username: string, email: string, password: string) {
    await api.post('/auth/register', { username, email, password })
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/users/me')
      user.value = response.data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, login, register, fetchUser, logout }
})
