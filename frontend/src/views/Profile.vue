<template>
  <div class="container">
    <div class="profile-header card">
      <div class="user-info">
        <div class="avatar-container">
          <img :src="user.avatar" class="user-avatar">
          <label for="avatar-upload" class="avatar-edit">
            <i class="fas fa-camera"></i>
            <input 
              id="avatar-upload" 
              type="file" 
              accept="image/*" 
              @change="handleAvatarUpload"
              hidden
            >
          </label>
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
              <strong>{{ user.items || 0 }}</strong>
              <span>商品</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="profile-actions">
        <button class="btn btn-outline" @click="editProfile">
          <i class="fas fa-edit"></i> 编辑资料
        </button>
      </div>
    </div>
    
    <div class="profile-tabs card">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="tab-content">
        <!-- 在售商品 -->
        <div v-if="activeTab === 'selling'" class="selling-items">
          <h3>在售商品 ({{ sellingItems.length }})</h3>
          <div class="products-grid">
            <ProductCard 
              v-for="item in sellingItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
        </div>
        
        <!-- 已售商品 -->
        <div v-if="activeTab === 'sold'" class="sold-items">
          <h3>已售商品 ({{ soldItems.length }})</h3>
          <div v-if="soldItems.length > 0" class="products-grid">
            <ProductCard 
              v-for="item in soldItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
          <div v-else class="empty-state">
            <i class="fas fa-box-open"></i>
            <p>暂无已售商品</p>
          </div>
        </div>
        
        <!-- 收藏商品 -->
        <div v-if="activeTab === 'favorites'" class="favorite-items">
          <h3>收藏的商品 ({{ favoriteItems.length }})</h3>
          <div class="products-grid">
            <ProductCard 
              v-for="item in favoriteItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import ProductCard from '@/components/ProductCard.vue'

const authStore = useAuthStore()
const activeTab = ref('selling')

const tabs = [
  { id: 'selling', label: '在售' },
  { id: 'sold', label: '已售' },
  { id: 'favorites', label: '收藏' }
]

const user = computed(() => authStore.user || {
  id: 1,
  username: '加载中...',
  avatar: 'default_avatar.png',
  bio: '',
  followers: 0,
  following: 0,
  items: 0
})

const sellingItems = ref([])
const soldItems = ref([])
const favoriteItems = ref([])

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  // 获取用户商品数据
  // 实际项目中应从API获取
  sellingItems.value = [
    { 
      id: 1, 
      title: 'Apple iPhone 13 128GB 蓝色', 
      price: 4299, 
      image: 'https://picsum.photos/300/300?random=1', 
      location: '北京', 
      views: 128 
    },
    // 其他商品...
  ]
})

const handleAvatarUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  try {
    await authStore.updateAvatar(file)
  } catch (error) {
    console.error('头像上传失败:', error)
    alert('头像上传失败，请重试')
  } finally {
    e.target.value = null
  }
}

const editProfile = () => {
  // 跳转到编辑资料页面
}
</script>

<style scoped>
.avatar-container {
  position: relative;
  display: inline-block;
}

.avatar-edit {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
</style>