import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    token: localStorage.getItem('access_token') || null
  }),
  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await api.login(credentials)
        if (response.data.access_token) {
          this.isAuthenticated = true
          // 登录成功后，只获取用户信息，不再负责跳转
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
    
    async adminLogin(credentials) {
      this.loading = true
      this.error = null
      try {
        const response = await api.adminLogin(credentials)
        if (response.data.access_token) {
          this.isAuthenticated = true
          // 登录成功后，获取用户信息
          await this.fetchCurrentUser()
        }
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || '管理员登录失败'
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
        const response = await api.getCurrentUser();
        // 确保获取完整的用户信息，包括items_count
        this.user = { ...this.user, ...response.data };
        this.isAuthenticated = true;
        return this.user;
      } catch (error) {
        // ...错误处理...
      }
    },
    
    async updateUserProfile(userData) {
      try {
        const response = await api.updateProfile(userData)
        // 确保返回完整的用户对象
        this.user = { ...this.user, ...response.data }
        return this.user
      } catch (error) {
        this.error = error.response?.data?.detail || '更新用户信息失败'
        throw error
      }
    },
    
async updateAvatar(file) {
  try {
    console.log('上传文件信息:', {
      name: file.name,
      type: file.type,
      size: file.size
    });
    const formData = new FormData()
    formData.append('avatar', file)  // 创建FormData对象
    
    const response = await api.uploadAvatar(formData)  // 传递FormData对象
    console.log('头像上传响应:', response.data);

      if (response.data && response.data.avatar) {
      // 强制刷新时间戳
      const newAvatarUrl = `${response.data.avatar}?t=${Date.now()}`;
      // 更新用户头像
      this.user.avatar = response.data.avatar
      // 触发存储更新
      this.$patch({ user: this.user });
      // 强制刷新用户数据
      await this.fetchCurrentUser()
      
      console.log('更新后的用户头像:', this.user.avatar);
      return this.user;
      // 添加时间戳避免缓存
      this.user.avatar = `${response.data.avatar}?t=${new Date().getTime()}`
    }
    return this.user
  } catch (error) {
    console.error('头像上传失败:', error);
    this.error = '上传失败: ' + (error.response?.data?.detail || error.message);
    throw error;
  }
},
    
    // 在初始化时从本地存储加载token
    initialize() {
      if (this.token) {
        this.fetchCurrentUser()
      }
    }
  }
})