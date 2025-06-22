import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
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
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response && error.response.status === 401) {
    // 未授权错误处理
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
  return Promise.reject(error)
})

export default {
  // 用户认证
  async register(userData) {
    return api.post('/auth/register', userData)
  },
  
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
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
    return api.get('/users/me')
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
    return api.get('/items', { params })
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

  // 搜索商品方法
  async searchItems(query, params = {}) {
    return api.get('/items/search', { 
      params: { ...params, q: query } 
   })
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
  }
}