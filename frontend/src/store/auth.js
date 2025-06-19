import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }),
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await api.login(credentials)
        if (response.data.access_token) {
          this.isAuthenticated = true
          await this.fetchCurrentUser()
        }
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(userData) {
      this.loading = true
      this.error = null
      try {
        const response = await api.register(userData)
        // 注册后自动登录
        if (response.status === 201) {
          await this.login({
            username: userData.username,
            password: userData.password
          })
        }
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      try {
        await api.logout()
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('access_token')
      } catch (error) {
        console.error('登出失败:', error)
      }
    },
    
    async fetchCurrentUser() {
      try {
        const response = await api.getCurrentUser()
        this.user = response.data
        this.isAuthenticated = true
        return this.user
      } catch (error) {
        this.isAuthenticated = false
        this.user = null
        return null
      }
    },
    
    async updateUser(userData) {
      try {
        const response = await api.updateUser(this.user.id, userData)
        this.user = response.data
        return this.user
      } catch (error) {
        this.error = error.response?.data?.detail || '更新用户信息失败'
        throw error
      }
    },
    
    async updateAvatar(file) {
      try {
        const response = await api.uploadAvatar(file)
        this.user.avatar = response.data.avatar
        return this.user
      } catch (error) {
        this.error = '上传头像失败'
        throw error
      }
    },
    
    initialize() {
      if (localStorage.getItem('access_token')) {
        this.fetchCurrentUser()
      }
    }
  }
})