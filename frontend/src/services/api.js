import axios from 'axios'
import { ref } from 'vue'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器添加认证token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // 添加时间戳防止缓存
  if (config.method === 'get') {
    config.params = { ...config.params, _t: Date.now() }
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(response => {
  return response
}, error => {
  console.error('API Error:', error)
  
  if (error.response && error.response.status === 401) {
    // 未授权错误处理
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
  
  // 网络错误处理
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    console.error('请求超时，请检查网络连接')
  }
  
  if (error.code === 'ERR_NETWORK') {
    console.error('网络错误，请检查后端服务是否正常运行')
  }
  
  return Promise.reject(error)
})

const systemMessagesPage = ref(1)
const systemMessagesLimit = ref(10)

// 添加重试函数
const retryRequest = async (requestFn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      console.error(`请求失败 (尝试 ${i + 1}/${maxRetries}):`, error)
      if (i === maxRetries - 1) {
        throw error
      }
      // 等待一段时间后重试
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
}

const apiService = {
  // 用户认证
  async register(userData) {
    return api.post('/auth/register', userData)
  },
  
  async login(credentials) {
    return retryRequest(async () => {
      // 用 URLSearchParams 构造表单数据
      const formData = new URLSearchParams();
      formData.append('identifier', credentials.identifier);
      formData.append('password', credentials.password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token)
      }
      return response
    })
  },
  
  async adminLogin(credentials) {
    // 管理员登录不建议自动重试，以避免密码错误时多次尝试
    const formData = new URLSearchParams();
    formData.append('identifier', credentials.identifier);
    formData.append('password', credentials.password);

    const response = await api.post('/admin/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    // 登录成功后，依然将token存入localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }
    return response
  },
  
  async logout() {
    localStorage.removeItem('access_token')
    return api.post('/auth/logout')
  },
  
  // 用户信息
  async getCurrentUser() {
    return retryRequest(() => api.get('/users/me'))
  },
  
  async updateUser(userId, userData) {
    return api.put(`/users/${userId}`, userData)
  },
  
  // 更新用户资料
  updateProfile(userData) {
    return api.put('/profile/', userData)
  },
  
  // 上传头像
  async uploadAvatar(formData) {
    return api.put('/profile/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 商品操作
  async getItems(params = {}) {
    return retryRequest(() => api.get('/items', { params }))
  },
  
  // 添加获取单个商品方法
  async getItem(itemId) {
    return api.get(`/items/${itemId}`)
  },
  
  // 添加创建商品方法（支持FormData）
  async createItem(formData) {
    return api.post('/items/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 添加获取用户商品方法
  async getUserSellingItems(userId, params = {}) {
    return api.get(`/users/${userId}/items`, { 
      params: { ...params, status: 'selling' } 
    })
  },

  // 添加获取用户已下架商品方法
  async getUserOfflineItems(userId, params = {}) {
    return api.get(`/users/${userId}/items`, { 
      params: { ...params, status: 'offline' } 
    })
  },

  // 添加获取用户已售商品方法
  async getUserSoldItems(userId, params = {}) {
    return api.get(`/users/${userId}/items`, { 
      params: { ...params, status: 'sold' } 
    })
  },
  
  async updateItem(itemId, itemData) {
    return api.put(`/items/${itemId}`, itemData)
  },
  
  async deleteItem(itemId) {
    return api.delete(`/items/${itemId}`)
  },
  
  // 添加更新商品状态方法
  async updateItemStatus(itemId, status) {
    return api.patch(`/items/${itemId}/status?status=${status}`)
  },
  
  // 添加更新商品浏览量方法
  async updateItemViews(itemId) {
    return api.patch(`/items/${itemId}/views`)
  },
  
  // 消息操作
  async getConversations() {
    return api.get('/messages')
  },
  
  async getMessages(conversationId) {
    return api.get(`/messages/${conversationId}`)
  },
  
  async sendMessage(messageData) {
    return api.post('/messages', messageData)
  },

  // 添加获取未读消息数量方法
  async getUnreadCount() {
    return api.get('/messages/unread-count')
  },

  // 添加获取对话列表方法
  async getConversationsList() {
    return api.get('/messages/conversations')
  },

  // 添加获取特定商品对话方法
  async getConversationMessages(itemId, otherUserId) {
    return api.get(`/messages/conversation/${itemId}/${otherUserId}`)
  },

  // 搜索商品方法
  async searchItems(query, params = {}) {
    return retryRequest(() => api.get('/items/search', { 
      params: { ...params, q: query } 
   }))
  },

  // 添加获取用户信息方法
  async getUser(userId) {
    return api.get(`/users/${userId}`)
  },

  // 添加收藏相关方法
  async checkFavorite(userId, itemId) {
    return api.get(`/favorites/check?user_id=${userId}&item_id=${itemId}`)
  },

  async addFavorite(userId, itemId) {
    return api.post(`/favorites/add?user_id=${userId}&item_id=${itemId}`)
  },

  async removeFavorite(userId, itemId) {
    return api.delete(`/favorites/remove?user_id=${userId}&item_id=${itemId}`)
  },

  // 添加获取用户收藏商品列表方法
  async getUserFavorites(userId, params = {}) {
    return api.get(`/favorites/user/${userId}`, { params })
  },

  // 文件上传
  async uploadItemImages(itemId, files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('images', file)
    })
    return api.post(`/items/${itemId}/upload-images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 标记商品为已售
  async markItemSold(itemId) {
    return api.patch(`/items/${itemId}/sold`)
  },

  // 添加获取公共系统消息方法
  async getPublicSystemMessages() {
    return retryRequest(() => api.get('/messages/system/public'))
  },
  
  async getSystemMessage(messageId) {
    return retryRequest(() => api.get(`/messages/system/${messageId}`))
  },

  // 管理员API
  async getAdminStats() {
    return retryRequest(() => api.get('/admin/stats'))
  },

  async getAdminUsers(params = {}) {
    return retryRequest(() => api.get('/admin/users', { params }))
  },

  async getAdminUser(userId) {
    return retryRequest(() => api.get(`/admin/users/${userId}`))
  },

  async updateUserStatus(userId, isActive) {
    return retryRequest(() => api.patch(`/admin/users/${userId}/status?is_active=${isActive}`))
  },

  async updateUserAdminStatus(userId, isAdmin) {
    return retryRequest(() => api.patch(`/admin/users/${userId}/admin?is_admin=${isAdmin}`))
  },

  async deleteAdminUser(userId) {
    return retryRequest(() => api.delete(`/admin/users/${userId}`))
  },

  async getAdminItems(params = {}) {
    return retryRequest(() => api.get('/admin/items', { params }))
  },

  async getAdminItem(itemId) {
    return retryRequest(() => api.get(`/admin/items/${itemId}`))
  },

  async updateAdminItemStatus(itemId, status) {
    return retryRequest(() => api.patch(`/admin/items/${itemId}/status?status=${status}`))
  },

  async deleteAdminItem(itemId) {
    return retryRequest(() => api.delete(`/admin/items/${itemId}`))
  },

  // 添加获取系统消息的方法
  async getSystemMessages(params = {}) {
    return retryRequest(() => api.get('/admin/messages', { params }))
  },

  // 添加发布系统消息的方法
  async publishSystemMessage(messageData) {
    return retryRequest(() => api.post('/admin/messages', messageData))
  },

  getUsersByIds: (userIds) => api.post('/users/by_ids', { user_ids: userIds }),

  async deleteConversation(itemId, otherUserId) {
    return api.delete(`/messages/conversation/${itemId}/${otherUserId}`)
  },
}

export default apiService;