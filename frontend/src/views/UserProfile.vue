<template>
  <div class="container">
    <!-- 用户头部信息 -->
    <div class="profile-header card">
      <div class="user-info">
        <div class="avatar-container">
          <img :src="getUserAvatar(user.avatar)" class="user-avatar" @error="handleAvatarError">
        </div>
        
        <div class="user-details">
          <h2 class="username">{{ user.username }}</h2>
          <p class="user-bio">{{ user.bio || '这个人很懒，什么都没留下' }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <strong>{{ user.followers || 0 }}</strong>
              <span>粉丝</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.following || 0 }}</strong>
              <span>关注</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.items_count || 0 }}</strong>
              <span>商品</span>
            </div>
          </div>
          <div class="user-contact" v-if="user.location || user.contact">
            <div v-if="user.location" class="contact-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ user.location }}</span>
            </div>
            <div v-if="user.contact" class="contact-item">
              <i class="fas fa-envelope"></i>
              <span>{{ user.contact }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="user-actions">
        <button v-if="!isCurrentUser" class="btn btn-primary" @click="startChat">
          <i class="fas fa-comment"></i> 联系TA
        </button>
        <button v-if="!isCurrentUser && !isFriend" class="btn btn-outline" @click="addFriend">
          <i class="fas fa-user-plus"></i> 添加好友
        </button>
        <button v-if="!isCurrentUser && isFriend" class="btn btn-outline" @click="removeFriend">
          <i class="fas fa-user-minus"></i> 删除好友
        </button>
      </div>
    </div>
    
    <!-- 商品标签页 -->
    <div class="profile-tabs card">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="{ active: activeTab === tab.id }"
          @click="changeTab(tab.id)"
        >
          {{ tab.label }}
          <span class="badge" v-if="tab.count > 0">{{ tab.count }}</span>
        </button>
      </div>
      
      <div class="tab-content">
        <!-- 在售商品标签页 -->
        <div v-if="activeTab === 'selling'">
          <div class="section-header">
            <h3>在售商品 ({{ sellingItems.length }})</h3>
          </div>
          
          <div v-if="loading.selling" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="sellingItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in sellingItems" 
                :key="`selling-${item.id}`" 
                :product="item" 
                :showActions="false"
              >
                <span>发布时间：{{ formatDateTime(item.created_at) }}</span>
              </ProductCard>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-store-slash"></i>
              <p>暂无在售商品</p>
            </div>
          </div>
        </div>
        
        <!-- 已售商品 -->
        <div v-if="activeTab === 'sold'">
          <div class="section-header">
            <h3>已售商品 ({{ soldItems.length }})</h3>
          </div>
          
          <div v-if="loading.sold" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="soldItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in soldItems" 
                :key="`sold-${item.id}`" 
                :product="item" 
                :sold="true"
                :showActions="false"
              >
                <span>售出时间：{{ formatDateTime(item.soldAt) }}</span>
              </ProductCard>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-box-open"></i>
              <p>暂无已售商品</p>
            </div>
          </div>
        </div>
        
        <!-- 求购信息tab -->
        <div v-else-if="activeTab === 'buy_requests'" class="tab-content">
          <div class="section-header">
            <h3>求购信息 ({{ buyRequests.length }})</h3>
          </div>
          <div v-if="buyRequests.length === 0" class="empty-state">
            <i class="fas fa-shopping-cart"></i>
            <p>暂无求购信息</p>
          </div>
          <div v-else>
            <div v-for="buyRequest in buyRequests" :key="buyRequest.id" class="buy-request-card">
              <div class="buy-request-main">
                <img :src="getBuyRequestImage(buyRequest.images)" :alt="buyRequest.title" class="buy-request-img">
                <div class="buy-request-info">
                  <h4>{{ buyRequest.title }}</h4>
                  <div class="budget">预算：<span class="price">¥{{ buyRequest.budget }}</span></div>
                  <div class="desc">{{ buyRequest.description }}</div>
                  <div class="meta">
                    <span class="time">{{ formatDateTime(buyRequest.created_at) }}</span>
                    <span class="likes">👍 {{ buyRequest.like_count || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import ProductCard from '@/components/ProductCard.vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'
import { ref, reactive, computed, onMounted, watch } from 'vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const props = defineProps({
  id: {
    type: [String, Number],
    required: true
  }
})

const activeTab = ref('selling')
const user = ref({
  id: 0,
  username: '加载中...',
  avatar: 'default_avatar.png',
  bio: '',
  followers: 0,
  following: 0,
  items_count: 0,
  contact: '',
  location: ''
})

const loading = reactive({
  selling: false,
  sold: false,
  buyRequests: false
})

const sellingItems = ref([])
const soldItems = ref([])
const buyRequests = ref([])
const isFriend = ref(false)

// 计算属性
const isCurrentUser = computed(() => {
  return authStore.user && authStore.user.id === parseInt(props.id)
})

// 标签页数据
const tabs = computed(() => [
  { id: 'selling', label: '在售', count: sellingItems.value.length },
  { id: 'sold', label: '已售', count: soldItems.value.length },
  { id: 'buy_requests', label: '求购', count: buyRequests.value.length }
])

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await api.getUser(props.id)
    user.value = response.data
    
    // 检查是否是好友
    if (authStore.user && !isCurrentUser.value) {
      await checkFriendStatus()
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    alert('获取用户信息失败')
  }
}

// 检查好友状态
const checkFriendStatus = async () => {
  try {
    const friendsResponse = await api.getFriendsList()
    isFriend.value = friendsResponse.data.some(friend => friend.id === parseInt(props.id))
  } catch (error) {
    console.error('检查好友状态失败:', error)
  }
}

// 获取在售商品
const fetchSellingItems = async () => {
  loading.selling = true
  try {
    const response = await api.getUserSellingItems(props.id, {
      skip: 0,
      limit: 50
    })
    sellingItems.value = response.data.data || []
  } catch (error) {
    console.error('获取在售商品失败:', error)
  } finally {
    loading.selling = false
  }
}

// 获取已售商品
const fetchSoldItems = async () => {
  loading.sold = true
  try {
    const response = await api.getUserSoldItems(props.id, {
      skip: 0,
      limit: 50
    })
    soldItems.value = response.data.data || []
  } catch (error) {
    console.error('获取已售商品失败:', error)
  } finally {
    loading.sold = false
  }
}

// 获取求购信息
const fetchBuyRequests = async () => {
  loading.buyRequests = true
  try {
    const response = await api.getBuyRequests({ 
      skip: 0, 
      limit: 50,
      user_id: props.id 
    })
    buyRequests.value = response.data || []
  } catch (error) {
    console.error('获取求购信息失败:', error)
  } finally {
    loading.buyRequests = false
  }
}

// 切换标签
const changeTab = (tabId) => {
  activeTab.value = tabId
  if (tabId === 'selling' && sellingItems.value.length === 0) {
    fetchSellingItems()
  } else if (tabId === 'sold' && soldItems.value.length === 0) {
    fetchSoldItems()
  } else if (tabId === 'buy_requests' && buyRequests.value.length === 0) {
    fetchBuyRequests()
  }
}

// 添加好友
const addFriend = async () => {
  try {
    await api.addFriend(props.id)
    isFriend.value = true
    alert('添加好友成功')
  } catch (error) {
    console.error('添加好友失败:', error)
    alert('添加好友失败')
  }
}

// 删除好友
const removeFriend = async () => {
  if (!confirm('确定要删除该好友吗？')) return
  try {
    await api.removeFriend(props.id)
    isFriend.value = false
    alert('删除好友成功')
  } catch (error) {
    console.error('删除好友失败:', error)
    alert('删除好友失败')
  }
}

// 开始聊天
const startChat = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  router.push(`/chat/${props.id}/${props.id}/user`)
}

// 工具函数
const getUserAvatar = (avatar) => {
  if (!avatar || avatar.includes('default')) {
    return '/static/images/default_avatar.png'
  }
  if (avatar.startsWith('http')) {
    // 修复HTTPS协议问题
    if (avatar.startsWith('https://127.0.0.1:8000')) {
      return avatar.replace('https://127.0.0.1:8000', 'http://127.0.0.1:8000');
    }
    return avatar
  }
  return `http://127.0.0.1:8000/static/images/${avatar.replace(/^static[\\/]images[\\/]/, '')}`
}

const handleAvatarError = (event) => {
  event.target.src = '/static/images/default_avatar.png'
}

const formatDateTime = (datetime) => {
  if (!datetime) return '未知'
  const date = new Date(datetime)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

const getBuyRequestImage = (images) => {
  if (!images) return '/static/images/default_product.png'
  let img = ''
  if (typeof images === 'string') {
    img = images.split(',')[0]
  } else if (Array.isArray(images)) {
    img = images[0]
  }
  if (!img) return '/static/images/default_product.png'
  if (img.startsWith('http')) return img
  if (img.startsWith('/static')) return 'http://127.0.0.1:8000' + img
  return 'http://127.0.0.1:8000/static/images/' + img
}

// 监听路由参数变化
watch(() => props.id, (newId) => {
  if (newId) {
    fetchUserInfo()
    fetchSellingItems()
  }
})

onMounted(() => {
  fetchUserInfo()
  fetchSellingItems()
})
</script>

<style scoped>
.profile-header {
  margin-bottom: 30px;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.user-info {
  display: flex;
  gap: 20px;
  flex: 1;
}

.avatar-container {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f5f5f5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.user-bio {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.user-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.stat-item {
  text-align: center;
}

.stat-item strong {
  display: block;
  font-size: 1.2rem;
  color: #333;
}

.stat-item span {
  font-size: 0.9rem;
  color: #666;
}

.user-contact {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 0.9rem;
}

.contact-item i {
  color: #3498db;
}

.user-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.profile-tabs {
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.tabs button {
  position: relative;
  padding: 12px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.3s;
}

.tabs button.active {
  color: #3498db;
  font-weight: 600;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background: #3498db;
  border-radius: 3px 3px 0 0;
}

.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 8px;
  background: #fff;
  border-radius: 10px;
  font-size: 15px;
  font-weight: bold;
  color: #3498db;
  box-shadow: none;
  border: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 16px;
}

.skeleton-card {
  height: 250px;
  background: #f5f5f5;
  border-radius: 8px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state i {
  font-size: 60px;
  margin-bottom: 20px;
  color: #e0e0e0;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 0 16px;
}

.buy-request-card {
  display: flex;
  align-items: flex-start;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 16px;
  margin-bottom: 18px;
  gap: 16px;
}

.buy-request-main {
  display: flex;
  align-items: flex-start;
  width: 100%;
}

.buy-request-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  background: #f5f5f5;
  margin-right: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid #eee;
}

.buy-request-info {
  flex: 1;
}

.buy-request-info h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: #333;
}

.budget .price {
  color: #e74c3c;
  font-weight: bold;
  margin-left: 4px;
}

.desc {
  color: #666;
  margin: 8px 0;
  line-height: 1.5;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 0.9rem;
  color: #999;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .user-contact {
    justify-content: center;
  }
  
  .user-actions {
    width: 100%;
    justify-content: center;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .tabs button {
    padding: 10px 16px;
    font-size: 14px;
  }
}
</style> 