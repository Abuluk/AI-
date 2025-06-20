<template>
  <div class="container">
    <!-- 用户头部信息 -->
    <div class="profile-header card">
      <div class="user-info">
        <div class="avatar-container">
          <!-- 头像上传区域 -->
          <div class="avatar-wrapper" :class="{ 'loading': avatarLoading }">
            <img :src="user.avatar" class="user-avatar">
            <div class="avatar-overlay" v-if="avatarLoading">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
          </div>
          <label for="avatar-upload" class="avatar-edit">
            <i class="fas fa-camera"></i>
            <input 
              id="avatar-upload" 
              type="file" 
              accept="image/*" 
              @change="handleAvatarUpload($event, false)"
              hidden
            >
          </label>
          
          <!-- 头像上传进度 -->
          <div v-if="avatarUploadProgress > 0" class="upload-progress">
            <div class="progress-bar" :style="{ width: avatarUploadProgress + '%' }"></div>
            <span>{{ avatarUploadProgress }}%</span>
          </div>
          
          <!-- 头像上传错误提示 -->
          <div v-if="avatarError" class="avatar-error">
            <i class="fas fa-exclamation-triangle"></i> {{ avatarError }}
          </div>
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
      
      <div>
        <button class="btn btn-outline" @click="showEditModal = true">
          <i class="fas fa-edit"></i> 编辑资料
        </button>
      </div>
    </div>
      <!-- 修改后的按钮区域 - 添加布局类 -->
      <div class="profile-actions actions-right">
        <button class="btn btn-primary" @click="navigateToPublish">
          <i class="fas fa-plus"></i> 上传商品
        </button>
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
           <h3>在售商品</h3>
            <div class="sort-controls">
              <!-- 修复排序功能：移除@change事件，改为使用计算属性 -->
              <select v-model="sorting.selling">
              <option value="newest">最新发布</option>
               <option value="popular">最受欢迎</option>
               <option value="price_asc">价格从低到高</option>
               <option value="price_desc">价格从高到低</option>
              </select>
            </div>
           </div>
          
          <div v-if="loading.selling" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="sellingItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in sortedSellingItems" 
                :key="`selling-${item.id}`" 
                :product="item" 
              />
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-store-slash"></i>
              <p>暂无在售商品</p>
              <button class="btn btn-primary" @click="navigateToPublish">
                去发布商品
              </button>
            </div>
            
            <div class="pagination" v-if="sellingItems.length > 0 && hasMore.selling">
              <button 
                class="btn btn-outline" 
                @click="loadMore('selling')"
                :disabled="loading.more"
              >
                <span v-if="loading.more">加载中...</span>
                <span v-else>加载更多</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 已售商品 -->
        <div v-if="activeTab === 'sold'">
          <div class="section-header">
            <h3>已售商品</h3>
            <div class="sort-controls">
                <select v-model="sorting.sold" @change="fetchSoldItems(true)">
                <option value="newest">最新售出</option>
                <option value="oldest">最早售出</option>
                </select>
            </div>
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
              />
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-box-open"></i>
              <p>暂无已售商品</p>
            </div>
            
            <div class="pagination" v-if="soldItems.length > 0 && hasMore.sold">
              <button 
                class="btn btn-outline" 
                @click="loadMore('sold')"
                :disabled="loading.more"
              >
                <span v-if="loading.more">加载中...</span>
                <span v-else>加载更多</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 收藏商品 -->
        <div v-if="activeTab === 'favorites'">
          <div class="section-header">
            <h3>收藏的商品</h3>
          </div>
          
          <div v-if="loading.favorites" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="favoriteItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in favoriteItems" 
                :key="`fav-${item.id}`" 
                :product="item" 
              />
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-heart"></i>
              <p>暂无收藏商品</p>
              <button class="btn btn-primary" @click="navigateToDiscover">
                     去首页浏览
              </button>
            </div>
            
            <div class="pagination" v-if="favoriteItems.length > 0 && hasMore.favorites">
              <button 
                class="btn btn-outline" 
                @click="loadMore('favorites')"
                :disabled="loading.more"
              >
                <span v-if="loading.more">加载中...</span>
                <span v-else>加载更多</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑资料模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑个人资料</h3>
          <button class="modal-close" @click="closeEditModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>用户名</label>
            <input type="text" v-model="editForm.username" maxlength="20">
            <div class="char-count">{{ editForm.username.length }}/20</div>
          </div>
          
          <div class="form-group">
            <label>个人简介</label>
            <textarea v-model="editForm.bio" rows="3" maxlength="120"></textarea>
            <div class="char-count">{{ editForm.bio.length }}/120</div>
          </div>
          
          <div class="form-group">
            <label>头像</label>
            <div class="avatar-edit-preview">
                  <img 
                    :src="editForm.avatarPreview" 
                    class="preview-image"
                    @error="handlePreviewError"
                  >
              <label for="edit-avatar-upload" class="avatar-edit-btn">
                <i class="fas fa-camera"></i> 更换头像
                <input 
                  id="edit-avatar-upload" 
                  type="file" 
                  accept="image/*" 
                  @change="handleAvatarUpload"
                  hidden
                >
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>联系方式</label>
            <input type="text" v-model="editForm.contact" placeholder="微信/QQ/手机号">
          </div>
          
          <div class="form-group">
            <label>地址</label>
            <input type="text" v-model="editForm.location" placeholder="所在城市">
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeEditModal">取消</button>
          <button class="btn btn-primary" @click="saveProfile" :disabled="savingProfile">
            <span v-if="savingProfile">保存中...</span>
            <span v-else>保存资料</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import ProductCard from '@/components/ProductCard.vue'
import { useRouter } from 'vue-router'
import api from '@/services/api' // 添加这行导入API服务
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'

onBeforeUnmount(() => {
  // 清理临时头像 URL
  if (editForm.avatarPreview && editForm.avatarPreview.startsWith('blob:')) {
    URL.revokeObjectURL(editForm.avatarPreview);
  }
});
const router = useRouter()
const activeTab = ref('selling')
const showEditModal = ref(false)
const savingProfile = ref(false)
// 添加响应式时间戳
const avatarTimestamp = ref(Date.now())
const authStore = useAuthStore();

// 使用计算属性确保响应式更新
const avatarUrl = computed(() => {
  if (!authStore.user?.avatar) return 'default_avatar.png';
  
  // 添加时间戳强制刷新
  return `${authStore.user.avatar}?t=${avatarTimestamp.value}`;
});

// 监听头像变化，强制更新
watch(() => authStore.user?.avatar, (newAvatar) => {
  if (newAvatar) {
    console.log('检测到头像变化，强制刷新:', newAvatar);
    avatarTimestamp.value = Date.now();
  }
});

const handleImageError = (event) => {
  console.error('头像加载失败:', event.target.src);
  event.target.src = 'default_avatar.png';
};

// 头像上传状态
const avatarLoading = ref(false)
const avatarUploadProgress = ref(0)
const avatarError = ref('')

// 处理头像上传
const handleEditAvatarUpload = (e) => {
  handleAvatarUpload(e, false)
}

// 编辑表单
const editForm = reactive({
  username: '',
  bio: '',
  avatarPreview: '',
  contact: '',
  location: ''
})

// 用于保存新头像文件对象
const newAvatarFile = ref(null)

// 确保编辑模态框打开时正确初始化预览
const openEditModal = () => {
  initEditForm()
  showEditModal.value = true
}

// 初始化编辑表单
const initEditForm = () => {
  const user = authStore.user || {}
  editForm.username = user.username || ''
  editForm.bio = user.bio || ''
  editForm.avatarPreview = user.avatar || 'default_avatar.png'
  editForm.contact = user.contact || ''
  editForm.location = user.location || ''

   // 使用带时间戳的头像URL
  editForm.avatarPreview = user.avatar 
    ? `${user.avatar}?t=${Date.now()}` 
    : 'default_avatar.png'
    
  editForm.contact = user.contact || ''
  editForm.location = user.location || ''
  newAvatarFile.value = null
}

// 关闭编辑模态框
const closeEditModal = () => {
  showEditModal.value = false
  // 重置新头像文件
  newAvatarFile.value = null
}

// 保存资料
const saveProfile = async () => {
  savingProfile.value = true
  try {
    // 如果有新头像，先上传头像
    if (newAvatarFile.value) {
      const updatedUser = await authStore.updateAvatar(newAvatarFile.value)
      // 使用服务器返回的永久URL更新预览
      editForm.avatarPreview = updatedUser.avatar
      authStore.user.avatar = updatedUser.avatar
    }
    
    // 保存其他资料
    const { avatarPreview, ...profileData } = editForm
    const updatedUser = await authStore.updateUserProfile(profileData)
    
    // 更新本地用户信息
    authStore.user = { ...authStore.user, ...updatedUser }
    
   // 关闭编辑模态框
const closeEditModal = () => {
  // 如果当前预览是blob URL，则释放
  if (editForm.avatarPreview.startsWith('blob:')) {
    URL.revokeObjectURL(editForm.avatarPreview)
  }
  showEditModal.value = false
  newAvatarFile.value = null
}
  } catch (error) {
    console.error('保存资料失败:', error)
    
    // 显示更具体的错误信息
    let errorMessage = '保存失败，请重试'
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.message) {
      errorMessage = error.message
    }
    
    alert(errorMessage)
  } finally {
    savingProfile.value = false
  }
}

// 通用的头像上传处理函数
const handleAvatarUpload = async (e, isProfileHeader = false) => {
  const file = e.target.files[0]
  if (!file) return

  // 验证文件类型和大小
  const validImageTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!validImageTypes.includes(file.type)) {
    const errorMsg = '只支持 JPG, PNG 或 GIF 格式的图片'
    if (isProfileHeader) {
      avatarError.value = errorMsg
    } else {
      alert(errorMsg)
    }
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    const errorMsg = '图片大小不能超过 5MB'
    if (isProfileHeader) {
      avatarError.value = errorMsg
    } else {
      alert(errorMsg)
    }
    return
  }

  // 重置错误状态
  if (isProfileHeader) {
    avatarError.value = ''
  }

  // 创建预览
  const previewUrl = URL.createObjectURL(file)
  
  // 页面顶部的头像上传
  if (isProfileHeader) {
    avatarLoading.value = true
    avatarUploadProgress.value = 0
    avatarTimestamp.value = Date.now()
    try {
      // 模拟上传进度
      const interval = setInterval(() => {
        avatarUploadProgress.value += 10
        if (avatarUploadProgress.value >= 100) {
          clearInterval(interval)
        }
      }, 200)
      
      // 等待上传完成
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 实际调用API更新头像
      const updatedUser = await authStore.updateAvatar(file)
      
      // 重要：使用服务器返回的新头像URL，而不是临时预览URL
      // 因为临时URL会在页面刷新后失效
      authStore.user.avatar = updatedUser.avatar
      
    } catch (error) {
      console.error('头像上传失败:', error)
      avatarError.value = '上传失败，请重试'
      // 显示更具体的错误信息
      if (error.response?.data?.detail) {
        avatarError.value = error.response.data.detail
      }
    } finally {
      avatarLoading.value = false
      e.target.value = null
      setTimeout(() => {
        avatarUploadProgress.value = 0
      }, 2000)
    }
  } 
  // 编辑模态框中的头像上传
  else {
    // 释放之前的临时URL（如果存在）
    if (newAvatarFile.value && editForm.avatarPreview.startsWith('blob:')) {
      URL.revokeObjectURL(editForm.avatarPreview)
    }
    // 创建预览
    editForm.avatarPreview = previewUrl
    // 保存文件对象用于后续上传
    newAvatarFile.value = file
    e.target.value = null
  }
  // 在编辑模态框分支结束时添加：
  if (!isProfileHeader && newAvatarFile.value) {
    // 组件卸载时清理临时URL
    onBeforeUnmount(() => {
      if (editForm.avatarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(editForm.avatarPreview)
      }
    })
  }
};


// 添加获取真实数据的方法
// Profile.vue
// 修改监听器
watch(
  () => authStore.user?.items_count, // 使用可选链避免访问 null
  (newCount, oldCount) => {
    // 确保值存在且有效
    if (newCount !== undefined && oldCount !== undefined && newCount > oldCount) {
      fetchRealSellingItems();
    }
  }
);
const fetchRealSellingItems = async () => {
  try {
    // 确保用户信息存在
    if (!authStore.user || !authStore.user.id) {
      console.error('用户信息未加载');
      return;
    }
    
    loading.selling = true;
    
    // 使用正确的 API 方法
    const response = await api.getUserSellingItems(
      authStore.user.id,
      {
        skip: (pagination.selling.page - 1) * pagination.selling.perPage,
        limit: pagination.selling.perPage
      }
    );
    
    sellingItems.value = response.data;
    
    // 更新统计数据
    tabs.value[0].count = sellingItems.value.length;
  } catch (error) {
    console.error('获取商品失败:', error);
    alert('获取商品失败，请刷新页面重试');
  } finally {
    loading.selling = false;
  }
};

// 标签页数据
const tabs = computed(() => [
  { id: 'selling', label: '在售', count: sellingItems.value.length },
  { id: 'sold', label: '已售', count: soldItems.value.length },
  { id: 'favorites', label: '收藏', count: favoriteItems.value.length }
])

// 用户信息
const user = computed(() => {
  return authStore.user || {
    id: 0,
    username: '加载中...',
    avatar: 'default_avatar.png',
    bio: '',
    followers: 0,
    following: 0,
    items: 0,
    contact: '',
    location: '',
    items_count: 0 // 添加默认值
  }
});

// 分页相关状态
const pagination = reactive({
  selling: { page: 1, perPage: 8, total: 0 },
  sold: { page: 1, perPage: 8, total: 0 },
  favorites: { page: 1, perPage: 8, total: 0 }
})

const hasMore = reactive({
  selling: true,
  sold: true,
  favorites: true
})

const loading = reactive({
  selling: false,
  sold: false,
  favorites: false,
  more: false
})

const sorting = reactive({
  selling: 'newest'
})

const sellingItems = ref([])
const soldItems = ref([])
const favoriteItems = ref([])

// 计算属性：排序后的在售商品
const sortedSellingItems = computed(() => {
  if (sellingItems.value.length === 0) return []
  
  // 创建副本以避免修改原始数据
  const items = [...sellingItems.value]
  
  switch (sorting.selling) {
    case 'price_asc':
      // 价格从低到高
      return items.sort((a, b) => a.price - b.price)
    case 'price_desc':
      // 价格从高到低
      return items.sort((a, b) => b.price - a.price)
    case 'popular':
      // 最受欢迎（按浏览量）
      return items.sort((a, b) => b.views - a.views)
    case 'newest':
    default:
      // 最新发布（按创建时间）
      return items.sort((a, b) => 
        new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      )
  }
})

// 添加排序计算属性
const sortedSoldItems = computed(() => {
  if (soldItems.value.length === 0) return [];
  
  const items = [...soldItems.value];
  
  switch (sorting.sold) {
    case 'oldest':
      return items.sort((a, b) => 
        new Date(a.soldAt).getTime() - new Date(b.soldAt).getTime()
      );
    case 'newest':
    default:
      return items.sort((a, b) => 
        new Date(b.soldAt).getTime() - new Date(a.soldAt).getTime()
      );
  }
})

// 监听标签切换
watch(activeTab, (newTab) => {
  if (newTab === 'selling' && sellingItems.value.length === 0) {
    fetchSellingItems()
  } else if (newTab === 'sold' && soldItems.value.length === 0) {
    fetchSoldItems()
  } else if (newTab === 'favorites' && favoriteItems.value.length === 0) {
    fetchFavoriteItems()
  }
})

// 修改onMounted钩子
onMounted(async () => {
  try {
    // 确保用户信息已加载
    if (!authStore.user) {
      await authStore.fetchCurrentUser();
    }
    
    // 使用真实 API 获取数据
    await fetchRealSellingItems();
  } catch (error) {
    console.error('初始化失败:', error);
    alert('加载用户信息失败，请刷新页面');
  }
});

// 切换标签
const changeTab = (tabId) => {
  activeTab.value = tabId
  // 如果数据为空则加载
  if ((tabId === 'selling' && sellingItems.value.length === 0) ||
      (tabId === 'sold' && soldItems.value.length === 0) ||
      (tabId === 'favorites' && favoriteItems.value.length === 0)) {
    fetchTabData(tabId)
  }
}

// 获取标签数据
const fetchTabData = (tabId) => {
  if (tabId === 'selling') {
    fetchSellingItems()
  } else if (tabId === 'sold') {
    fetchSoldItems()
  } else if (tabId === 'favorites') {
    fetchFavoriteItems()
  }
}

// 获取已售商品
const fetchSoldItems = async () => {
  loading.sold = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    const mockData = generateMockSoldItems(pagination.sold.perPage)
    
    if (pagination.sold.page === 1) {
      soldItems.value = mockData
    } else {
      soldItems.value = [...soldItems.value, ...mockData]
    }
    
    pagination.sold.total = 12
    hasMore.sold = soldItems.value.length < pagination.sold.total
  } catch (error) {
    console.error('获取已售商品失败:', error)
  } finally {
    loading.sold = false
    loading.more = false
  }
}

// 获取收藏商品
const fetchFavoriteItems = async () => {
  loading.favorites = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    const mockData = generateMockFavoriteItems(pagination.favorites.perPage)
    
    if (pagination.favorites.page === 1) {
      favoriteItems.value = mockData
    } else {
      favoriteItems.value = [...favoriteItems.value, ...mockData]
    }
    
    pagination.favorites.total = 24
    hasMore.favorites = favoriteItems.value.length < pagination.favorites.total
  } catch (error) {
    console.error('获取收藏商品失败:', error)
  } finally {
    loading.favorites = false
    loading.more = false
  }
}

// 加载更多
const loadMore = (type) => {
  loading.more = true
  pagination[type].page += 1
  
  if (type === 'selling') {
    fetchSellingItems()
  } else if (type === 'sold') {
    fetchSoldItems()
  } else if (type === 'favorites') {
    fetchFavoriteItems()
  }
}

// 导航函数
const navigateToPublish = () => {
  router.push({ name: 'Publish' }); // 确保与路由配置中的名称匹配
}

const navigateToDiscover = () => {
  router.push({ path: '/' })
}

// 模拟数据生成函数
const generateMockSellingItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1 + (pagination.selling.page - 1) * pagination.selling.perPage,
    title: `商品 ${i + 1 + (pagination.selling.page - 1) * pagination.selling.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    views: Math.floor(Math.random() * 500),
    createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
}

const generateMockSoldItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `sold-${i + 1 + (pagination.sold.page - 1) * pagination.sold.perPage}`,
    title: `已售商品 ${i + 1 + (pagination.sold.page - 1) * pagination.sold.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    soldAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
}

const generateMockFavoriteItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `fav-${i + 1 + (pagination.favorites.page - 1) * pagination.favorites.perPage}`,
    title: `收藏商品 ${i + 1 + (pagination.favorites.page - 1) * pagination.favorites.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    favoritedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
}

</script>

<style scoped>
/* 原有样式保持不变 */

/* 头像上传加载状态 */
/* 固定圆形头像容器（建议根据需求调整尺寸） */
.avatar-container {
  position: relative;
  width: 100px; /* 固定宽度 */
  height: 100px; /* 固定高度 */
  margin: 0 auto; /* 水平居中 */
  margin-left: -20px; /* 向左移动20px，负值为左移，正值为右移 */
  border-radius: 50%; /* 圆形边框 */
  overflow: hidden; /* 超出部分隐藏 */
  background-color: #f5f5f5; /* 背景色（加载时显示） */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 阴影效果 */
}

.avatar-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 图片等比填充 */
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.upload-progress {
  margin-top: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  height: 24px;
  position: relative;
  width: 100%;
  max-width: 150px;
}

.progress-bar {
  height: 100%;
  background: #3498db;
  border-radius: 4px;
  transition: width 0.3s;
}

.upload-progress span {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 12px;
  font-weight: bold;
}

.avatar-error {
  margin-top: 8px;
  color: #e74c3c;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 编辑资料模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 8px;
}

.modal-body {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.avatar-edit-preview {
  display: flex;
  align-items: center;
  gap: 20px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
  background-color: #f5f5f5;
}

.avatar-edit-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  font-size: 14px;
}

.avatar-edit-btn:hover {
  background: #eaeaea;
}

/* 加载状态 */
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

/* 空状态 */
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

.empty-state .btn {
  margin-top: 10px;
}

/* 标签页样式 */
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
  padding: 2px 6px;
  background: #f0f0f0;
  border-radius: 10px;
  font-size: 12px;
  font-weight: normal;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 16px;
}

.sort-controls select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

/* 商品网格 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 0 16px;
}

.pagination {
  text-align: center;
  margin: 30px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .tabs button {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .sort-controls {
    align-self: flex-end;
  }
  
  .avatar-edit-preview {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 添加上传按钮样式 */
.profile-actions {
  display: flex;
  gap: 10px; /* 按钮间距 */
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

/* 空状态按钮优化 */
.empty-state .btn {
  margin-top: 15px;
}
</style>