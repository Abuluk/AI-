import axios from 'axios'
import { ref } from 'vue'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  timeout: 60000,
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
    // 不直接跳转，让路由守卫处理
    console.warn('Token已过期或无效，请重新登录')
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
      // 发送 JSON 格式数据
      const response = await api.post('/auth/login', {
        identifier: credentials.identifier,
        password: credentials.password
      }, {
        headers: {
          'Content-Type': 'application/json'
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
    return api.post('/items', formData, {
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
  
  // 添加商品点赞方法
  async likeItem(itemId) {
    return api.post(`/items/${itemId}/like`)
  },
  
  // 添加商品取消点赞方法
  async unlikeItem(itemId) {
    return api.post(`/items/${itemId}/unlike`)
  },
  
  // 消息操作
  // 获取对话列表
  async getConversationsList() {
    return api.get('/messages/conversations')
  },

  // 获取未读消息数量
  async getUnreadCount() {
    return api.get('/messages/unread-count')
  },

  // 标记系统消息为已读
  async markSystemMessageAsRead(messageId) {
    return api.patch(`/messages/system/${messageId}/read`)
  },

  // 批量标记点赞消息为已读
  async markLikeMessagesAsRead() {
    return api.patch('/messages/batch/like-messages/read')
  },

  /**
   * 获取对话消息（支持商品和求购）
   * @param {Object} params { type: 'item'|'buy_request', id, other_user_id }
   */
  async getConversationMessages({ type = 'item', id, other_user_id }) {
    // type: 'item' 或 'buy_request'
    return api.get(`/messages/conversation/${type}/${id}/${other_user_id}`)
  },

  /**
   * 发送消息（支持商品、求购和用户私聊）
   * @param {Object} messageData { content, other_user_id, type, id }
   */
  async sendMessage({ content, other_user_id, type = 'item', id }) {
    const data = {
      content,
      other_user_id
    }
    
    if (type === 'user') {
      // 用户私聊：使用target_user字段
      data.target_user = other_user_id
    } else {
      // 商品或求购消息：使用item_id或buy_request_id
      data.item_id = type === 'item' ? id : undefined
      data.buy_request_id = type === 'buy_request' ? id : undefined
    }
    
    return api.post('/messages', data)
  },

  /**
   * 删除对话（支持商品和求购）
   * @param {Object} params { type: 'item'|'buy_request', id, other_user_id }
   */
  async deleteConversation({ type = 'item', id, other_user_id }) {
    return api.delete(`/messages/conversation/${type}/${id}/${other_user_id}`)
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
    return retryRequest(async () => {
      const res = await api.get('/messages/system/public');
      // 过滤掉点赞相关的系统消息
      if (Array.isArray(res.data)) {
        res.data = res.data.filter(msg => !(msg.title && msg.title.includes('被点赞')));
      }
      return res;
    });
  },
  
  async getSystemMessage(messageId) {
    return retryRequest(() => api.get(`/messages/system/${messageId}`))
  },

  // 添加获取AI分析的低价好物推荐方法
  async getAICheapDeals(limit = 10) {
    return retryRequest(() => api.get('/items/ai-cheap-deals', { 
      params: { limit } 
    }))
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

  // 求购相关
  async createBuyRequest(data) {
    return api.post('/buy_requests', data)
  },

  async getBuyRequests(params = {}) {
    return api.get('/buy_requests', { params });
  },

  async getBuyRequest(id) {
    return api.get(`/buy_requests/${id}`);
  },

  // 新增：获取当前用户的求购信息
  async getMyBuyRequests(params = {}) {
    return api.get('/buy_requests/my_own', { params });
  },

  // 新增：删除求购信息
  async deleteBuyRequest(id) {
    return api.delete(`/buy_requests/${id}`);
  },

  // 新增：更新求购信息
  async updateBuyRequest(id, data) {
    return api.put(`/buy_requests/${id}`, data);
  },

  // AI自动补全商品信息（图片识别，支持多图片）
  async aiAutoCompleteItemByImage(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    // 直接用axios.post，确保可用
    return axios.post('http://127.0.0.1:8000/api/v1/items/ai-auto-complete', formData, {
      headers: {
        Authorization: localStorage.getItem('access_token') ? `Bearer ${localStorage.getItem('access_token')}` : undefined
      }
    });
  },

  // 新增：保存活动页banner配置
  async saveActivityBanners(banners) {
    return api.post('/admin/site_config/activity_banner', { value: banners })
  },

  // 新增：获取前台活动页banner
  async getActivityBanners() {
    return api.get('/site_config/activity_banner');
  },

  // 新增：获取后台活动页banner
  async getAdminActivityBanners() {
    return api.get('/admin/site_config/activity_banner');
  },

  // 新增：删除系统消息
  async deleteSystemMessage(id) {
    return api.delete(`/admin/messages/${id}`)
  },

  // 管理员求购信息管理
  async getAdminBuyRequests(params = {}) {
    return retryRequest(() => api.get('/admin/buy_requests', { params }))
  },

  async deleteAdminBuyRequest(buyRequestId) {
    return retryRequest(() => api.delete(`/admin/buy_requests/${buyRequestId}`))
  },

  requestPasswordReset(data) {
    return axios.post('/api/v1/users/request-password-reset', data);
  },

  resetPassword(data) {
    return axios.post('/api/v1/users/reset-password', data);
  },

  uploadBuyRequestImage(formData) {
    return api.post('/buy_requests/upload_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 评论相关
  async getComments(params = {}) {
    return api.get('/comments', { params })
  },
  async getMyRelatedComments() {
    return api.get('/comments/my_related')
  },
  async createComment(data) {
    return api.post('/comments', data)
  },
  async deleteComment(commentId) {
    return api.delete(`/comments/${commentId}`)
  },
  async getCommentTree(params = {}) {
    return api.get('/comments/tree', { params })
  },
  async likeComment(commentId) {
    return api.post(`/comments/${commentId}/like`)
  },
  async unlikeComment(commentId) {
    return api.post(`/comments/${commentId}/unlike`)
  },
  async getLikeMessages() {
    return api.get('/messages/likes')
  },

  // 聊天图片上传
  async uploadChatImage(formData) {
    return api.post('/messages/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 好友功能
  async addFriend(friendId) {
    return api.post('/friends/add', { friend_id: friendId })
  },

  async removeFriend(friendId) {
    return api.post('/friends/delete', { friend_id: friendId })
  },

  async getFriendsList() {
    return api.get('/friends/list')
  },

  async searchUsers(keyword) {
    return api.get(`/friends/search?keyword=${encodeURIComponent(keyword)}`)
  },

  async getFriendDetail(friendId) {
    return api.get(`/friends/${friendId}`)
  },

  // 黑名单功能
  async addToBlacklist(blockedUserId) {
    return api.post('/blacklist/add', { blocked_user_id: blockedUserId })
  },

  async removeFromBlacklist(blockedUserId) {
    return api.post('/blacklist/remove', { blocked_user_id: blockedUserId })
  },

  async getBlacklist() {
    return api.get('/blacklist/list')
  },

  // 商品推广位管理
  async getPromotedItems() {
    return api.get('/items/promoted')
  },

  async updatePromotedItems(itemIds) {
    return api.put('/admin/promoted_items', itemIds)
  },

  async getRecommendedItems(itemId, limit = 4) {
    return api.get(`/items/${itemId}/recommendations`, { params: { limit } })
  },

  async updateRecommendedItems(itemId, recommendedItemIds) {
    return api.put(`/admin/items/${itemId}/recommendations`, { 
      recommended_item_ids: recommendedItemIds 
    })
  },

  // 意见反馈相关
  async createFeedback(content) {
    return api.post('/feedback/', { content })
  },
  async getAllFeedbacks() {
    return api.get('/feedback/')
  },
  async solveFeedback(feedbackId) {
    return api.patch(`/feedback/${feedbackId}`)
  },
  async deleteFeedback(feedbackId) {
    return api.delete(`/feedback/${feedbackId}`)
  },

  // AI策略相关
  async getAIStrategyReport() {
    return api.post('/ai_strategy/', {}, { timeout: 600000 }) // 10分钟超时
  },

  async markAllMessagesAsRead() {
    return api.post('/messages/all-read')
  },

  // 商家认证相关
  async createMerchantApplication(data) {
    return api.post('/merchants/apply', data)
  },

  async getMerchantInfo() {
    return api.get('/merchants/my')
  },

  async updateMerchantInfo(data) {
    return api.put('/merchants/my', data)
  },

  async getMerchantDisplayConfig() {
    return api.get('/merchants/display-config')
  },

  async updateMerchantDisplayConfig(data) {
    return api.put('/merchants/display-config', data)
  },

  async cancelMerchantApplication() {
    return api.delete('/merchants/cancel-application')
  },

      // 管理员商家管理
    async getAllMerchants(params = {}) {
      return api.get('/merchants/admin/all', { params })
    },

  async approveMerchant(merchantId) {
    return api.post(`/merchants/${merchantId}/approve`)
  },

  async rejectMerchant(merchantId, reason) {
    return api.post(`/merchants/${merchantId}/reject`, { reason })
  },

  // 管理员获取用户商家信息
  async getUserMerchantInfo(userId) {
    return api.get(`/merchants/admin/user/${userId}`)
  },

  // 管理员通过待认证用户
  async approvePendingVerificationUser(userId) {
    return api.post(`/merchants/admin/user/${userId}/approve`)
  },

  // 管理员拒绝待认证用户
  async rejectPendingVerificationUser(userId, reason) {
    return api.post(`/merchants/admin/user/${userId}/reject`, { reason })
  },

  async deleteMerchant(merchantId, reason) {
    return api.delete(`/merchants/admin/${merchantId}`, { data: { reason } })
  },

  // 用户申请取消商家认证
  async cancelMerchantApplication(reason) {
    return api.post('/merchants/cancel-application', { reason })
  },

  async setPendingMerchant(userId, merchantData = {}) {
    const params = {
      user_id: userId,
      business_name: merchantData.business_name || '默认商家',
      contact_person: merchantData.contact_person || '默认联系人',
      contact_phone: merchantData.contact_phone || '13800000000',
      business_address: merchantData.business_address || '默认地址',
      business_description: merchantData.business_description || '默认描述'
    }
    return api.post(`/merchants/admin/set-pending-verification`, null, { params })
  },

  async searchUser(keyword) {
    return api.get(`/admin/users?search=${encodeURIComponent(keyword)}&limit=10`)
  },

  async getPendingVerificationUsers(params) {
    const queryParams = new URLSearchParams()
    if (params.skip) queryParams.append('skip', params.skip)
    if (params.limit) queryParams.append('limit', params.limit)
    if (params.search) queryParams.append('search', params.search)
    return api.get(`/users/pending-verification?${queryParams.toString()}`)
  },

  async removePendingVerification(userId) {
    return api.post(`/merchants/remove-pending-verification`, { user_id: userId })
  },

  async getDefaultDisplayFrequency() {
    return api.get('/merchants/admin/display-config/default')
  },

  async updateDefaultDisplayFrequency(frequency) {
    return api.put('/merchants/admin/display-config/default', { display_frequency: frequency })
  }
}

export default apiService;