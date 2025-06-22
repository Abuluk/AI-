<template>
  <div class="container">
    <div class="product-detail card">
      <div class="detail-header">
        <h1 class="product-title">{{ product.title }}</h1>
        <div class="product-meta">
          <span>{{ product.location }}</span>
          <span>浏览: {{ product.views }}</span>
          <span>发布时间: {{ formatTime(product.created_at) }}</span>
        </div>
      </div>
      
      <div class="detail-content">
        <div class="detail-images">
          <img :src="mainImage" class="main-image">
          <div class="thumbnail-container">
            <img 
              v-for="(img, index) in product.images" 
              :key="index"
              :src="img" 
              class="thumbnail"
              :class="{ active: mainImage === img }"
              @click="mainImage = img"
            >
          </div>
        </div>
        
        <div class="detail-info">
          <div class="detail-price">¥{{ product.price }}</div>
          
          <div class="detail-description">
            <h3>商品描述</h3>
            <p>{{ product.description }}</p>
          </div>
          
          <div class="seller-info">
            <h3>卖家信息</h3>
            <div class="seller-card">
              <div class="seller-header">
                <img :src="seller.avatar" class="seller-avatar" @error="handleAvatarError">
                <div class="seller-basic-info">
                  <div class="seller-name">{{ seller.username }}</div>
                  <div class="seller-stats">
                    <span class="stat-item">
                      <i class="fas fa-box"></i>
                      {{ seller.items_count || 0 }} 件商品
                    </span>
                    <span class="stat-item">
                      <i class="fas fa-calendar-alt"></i>
                      {{ formatJoinDate(seller.created_at) }} 加入
                    </span>
                  </div>
                </div>
                <button class="btn btn-outline" @click="startChat">
                  <i class="fas fa-comment"></i> 联系卖家
                </button>
              </div>
              
              <div class="seller-details">
                <div v-if="seller.bio" class="seller-bio">
                  <h4>个人简介</h4>
                  <p>{{ seller.bio }}</p>
                </div>
                
                <div class="seller-contact-info">
                  <div v-if="seller.location" class="contact-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>所在地：{{ seller.location }}</span>
                  </div>
                  <div v-if="seller.contact" class="contact-item">
                    <i class="fas fa-phone"></i>
                    <span>联系方式：{{ seller.contact }}</span>
                  </div>
                  <div v-if="seller.phone" class="contact-item">
                    <i class="fas fa-mobile-alt"></i>
                    <span>手机：{{ seller.phone }}</span>
                  </div>
                </div>
                
                <div class="seller-activity">
                  <div class="activity-item">
                    <i class="fas fa-eye"></i>
                    <span>最近活跃：{{ formatLastActive(seller.last_login) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <!-- 收藏按钮 -->
      <button class="btn btn-outline" @click="toggleFavorite">
        <i :class="['fas', isFavorited ? 'fa-heart text-danger' : 'fa-heart']"></i> 
            {{ isFavorited ? '已收藏' : '收藏' }}
      </button>
            
      <!-- 购买按钮（仅显示给非所有者） -->
      <button 
        class="btn btn-primary" 
          v-if="!isOwner && !product.sold && product.status !== 'offline'"
            @click="purchaseItem"
          >
            <i class="fas fa-shopping-cart"></i> 立即购买
      </button>
            
      <!-- 下架按钮（仅显示给所有者） -->
      <button 
        v-if="isOwner && !product.sold && product.status !== 'offline'"
          class="btn btn-danger"
          @click="offlineItem"
            >
          <i class="fas fa-ban"></i> 已下架商品
      </button>
            
      <!-- 重新上架按钮（仅显示给所有者） -->
      <button 
        v-if="isOwner && product.status === 'offline'"
        class="btn btn-success"
        @click="onlineItem"
      >
        <i class="fas fa-check"></i> 重新上架
      </button>
    </div>

    <div class="related-products card">
      <h2>推荐商品</h2>
      <div class="products-grid">
        <ProductCard 
          v-for="product in relatedProducts" 
          :key="product.id" 
          :product="product" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import ProductCard from '@/components/ProductCard.vue'
import api from '@/services/api'
import { mapState } from 'pinia'
import { useAuthStore } from '@/store/auth'

export default {
  components: {
    ProductCard
  },
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      mainImage: '',
      product: {
        id: null,
        title: '',
        price: 0,
        description: '',
        location: '',
        views: 0,
        createdAt: '',
        images: [],
        status: 'online',
        sold: false,
        favorited_count: 0,
        owner_id: null
      },
      seller: {
        id: null,
        username: '',
        avatar: '',
        bio: '',
        location: '',
        contact: '',
        phone: '',
        created_at: '',
        last_login: '',
        items_count: 0
      },
      relatedProducts: [],
      isFavorited: false
    }
  },
  created() {
    this.mainImage = this.product.images[0]
  },
  async created() {
    await this.fetchItemData()
    this.checkFavoriteStatus()
  },
  computed: {
    user() {
      return useAuthStore().user
    },
    isOwner() {
      return this.user && this.user.id === this.product.owner_id
    }
  },
  methods: {
    async fetchItemData() {
      try {
        // 调用真实API获取商品数据
        const response = await api.getItem(this.id)
        this.product = response.data
        
        // 处理图片数据
        if (this.product.images) {
          const images = this.product.images.split(',')
          this.product.images = images.map(img => {
            if (!img) return 'default_product.png'
            img = img.trim()
            if (img.startsWith('http')) return img
            if (img.startsWith('/static/')) return img
            if (img.startsWith('images/')) return `/static/${img.replace(/^images[\\/]/, '')}`
            // 兜底：去掉多余static/images/前缀再拼接
            return `/static/images/${img.replace(/^static[\\/]images[\\/]/, '')}`
          })
        }
        
        // 设置主图片
        this.mainImage = this.product.images && this.product.images.length > 0 
          ? this.product.images[0] 
          : 'default_product.png'
        
        // 更新浏览量
        try {
          await api.updateItemViews(this.id)
          this.product.views += 1
        } catch (error) {
          console.warn('更新浏览量失败:', error)
        }
        
        // 获取卖家信息
        if (this.product.owner_id) {
          console.log('获取卖家信息，owner_id:', this.product.owner_id)
          try {
            const sellerResponse = await api.getUser(this.product.owner_id)
            console.log('卖家信息API响应:', sellerResponse.data)
            this.seller = {
              id: sellerResponse.data.id,
              username: sellerResponse.data.username || '未知用户',
              avatar: sellerResponse.data.avatar || 'default_avatar.png',
              bio: sellerResponse.data.bio || '',
              location: sellerResponse.data.location || '',
              contact: sellerResponse.data.contact || '',
              phone: sellerResponse.data.phone || '',
              created_at: sellerResponse.data.created_at || '',
              last_login: sellerResponse.data.last_login || '',
              items_count: sellerResponse.data.items_count || 0
            }
            console.log('设置卖家信息:', this.seller)
          } catch (error) {
            console.error('获取卖家信息失败:', error)
            // 使用默认卖家信息
            this.seller = {
              id: this.product.owner_id,
              username: '未知用户',
              avatar: 'default_avatar.png',
              bio: '',
              location: '',
              contact: '',
              phone: '',
              created_at: '',
              last_login: '',
              items_count: 0
            }
          }
        } else {
          console.warn('商品没有owner_id，无法获取卖家信息')
        }
        
        // 获取推荐商品（简化版，实际可以根据分类或标签获取）
        try {
          const relatedResponse = await api.getItems({ 
            limit: 3,
            skip: 0
          })
          this.relatedProducts = relatedResponse.data.filter(item => item.id !== this.id)
        } catch (error) {
          console.warn('获取推荐商品失败:', error)
        }
        
      } catch (error) {
        console.error('获取商品数据失败:', error)
        // 如果商品不存在或已被删除，跳转到首页
        if (error.response && error.response.status === 404) {
          alert('商品不存在或已被删除')
          this.$router.push('/')
        } else {
          alert('获取商品信息失败，请重试')
        }
      }
    },
    async checkFavoriteStatus() {
      if (!this.user) return
      try {
        // 调用真实API检查收藏状态
        const response = await api.checkFavorite(this.user.id, this.id)
        this.isFavorited = response.data.isFavorited
      } catch (error) {
        console.error('检查收藏状态失败:', error)
        this.isFavorited = false
      }
    },
    async toggleFavorite() {
      if (!this.user) {
        this.$router.push('/login')
        return
      }
      
      try {
        if (this.isFavorited) {
          // 移除收藏
          await api.removeFavorite(this.user.id, this.id)
          this.product.favorited_count = Math.max(0, (this.product.favorited_count || 0) - 1)
        } else {
          // 添加收藏
          await api.addFavorite(this.user.id, this.id)
          this.product.favorited_count = (this.product.favorited_count || 0) + 1
        }
        this.isFavorited = !this.isFavorited
      } catch (error) {
        console.error('收藏操作失败:', error)
        alert('操作失败，请重试')
      }
    },
    async offlineItem() {
      if (confirm('确定要下架该商品吗？下架后其他用户将无法看到此商品。')) {
        try {
          // 调用真实API下架商品
          await api.updateItemStatus(this.product.id, 'offline')
          
          // 更新本地状态
          this.product.status = 'offline'
          alert('商品已成功下架')
        } catch (error) {
          console.error('下架商品失败:', error)
          alert('操作失败，请重试')
        }
      }
    },
    async onlineItem() {
      try {
        // 调用真实API上架商品
        await api.updateItemStatus(this.product.id, 'online')
        
        // 更新本地状态
        this.product.status = 'online'
        alert('商品已重新上架')
      } catch (error) {
        console.error('上架商品失败:', error)
        alert('操作失败，请重试')
      }
    },
    purchaseItem() {
      // 购买商品逻辑
      alert('购买流程开始...')
    },
    startChat() {
      this.$router.push({ name: 'Chat', params: { id: this.seller.id } })
    },
    formatTime(createdAt) {
      if (!createdAt) return '未知时间'
      let date
      // 兼容 "2024-06-22 12:34:56" 和 "2024-06-22T12:34:56Z"
      if (typeof createdAt === 'string') {
        let iso = createdAt.replace(' ', 'T')
        if (!iso.endsWith('Z')) iso += 'Z'
        date = new Date(iso)
      } else {
        date = new Date(createdAt)
      }
      if (isNaN(date.getTime())) return '未知时间'
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const months = Math.floor(days / 30)
      const years = Math.floor(days / 365)
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 30) return `${days}天前`
      if (months < 12) return `${months}个月前`
      if (years >= 1) return `${years}年前`
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatJoinDate(createdAt) {
      if (!createdAt) return '未知时间'
      let date
      // 兼容 "2024-06-22 12:34:56" 和 "2024-06-22T12:34:56Z"
      if (typeof createdAt === 'string') {
        let iso = createdAt.replace(' ', 'T')
        if (!iso.endsWith('Z')) iso += 'Z'
        date = new Date(iso)
      } else {
        date = new Date(createdAt)
      }
      if (isNaN(date.getTime())) return '未知时间'
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const months = Math.floor(days / 30)
      const years = Math.floor(days / 365)
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 30) return `${days}天前`
      if (months < 12) return `${months}个月前`
      if (years >= 1) return `${years}年前`
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatLastActive(lastLogin) {
      if (!lastLogin) return '未知时间'
      let date
      // 兼容 "2024-06-22 12:34:56" 和 "2024-06-22T12:34:56Z"
      if (typeof lastLogin === 'string') {
        let iso = lastLogin.replace(' ', 'T')
        if (!iso.endsWith('Z')) iso += 'Z'
        date = new Date(iso)
      } else {
        date = new Date(lastLogin)
      }
      if (isNaN(date.getTime())) return '未知时间'
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const months = Math.floor(days / 30)
      const years = Math.floor(days / 365)
      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 30) return `${days}天前`
      if (months < 12) return `${months}个月前`
      if (years >= 1) return `${years}年前`
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    handleAvatarError() {
      this.seller.avatar = 'default_avatar.png'
    }
  }
}
</script>

<style scoped>
.product-detail {
  margin-bottom: 30px;
}

.detail-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.product-title {
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.product-meta {
  display: flex;
  gap: 15px;
  color: var(--text-light);
  font-size: 0.9rem;
}

.detail-content {
  display: flex;
  padding: 20px;
}

.detail-images {
  width: 50%;
  padding-right: 20px;
}

.main-image {
  width: 100%;
  border-radius: 10px;
  margin-bottom: 15px;
  max-height: 500px;
  object-fit: contain;
}

.thumbnail-container {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 5px;
  object-fit: cover;
  cursor: pointer;
  border: 2px solid transparent;
}

.thumbnail.active {
  border-color: var(--primary);
}

.detail-info {
  width: 50%;
  padding-left: 20px;
}

.detail-price {
  font-size: 1.8rem;
  color: var(--danger);
  font-weight: bold;
  margin-bottom: 15px;
}

.detail-description {
  margin-bottom: 25px;
  line-height: 1.8;
}

.detail-description h3 {
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.seller-info h3 {
  margin-bottom: 10px;
  font-size: 1.2rem;
}

.seller-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #f9f9f9;
  margin-bottom: 20px;
}

.seller-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border);
}

.seller-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border);
}

.seller-basic-info {
  flex: 1;
}

.seller-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-dark);
}

.seller-stats {
  color: var(--text-light);
  display: flex;
  gap: 15px;
  font-size: 0.9rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-item i {
  color: var(--primary);
}

.seller-details {
  width: 100%;
}

.seller-bio {
  margin-bottom: 20px;
  text-align: left;
}

.seller-bio h4 {
  margin-bottom: 10px;
  font-size: 1.1rem;
  color: var(--text-dark);
}

.seller-bio p {
  color: var(--text-light);
  line-height: 1.5;
}

.seller-contact-info {
  margin-bottom: 20px;
  text-align: left;
}

.contact-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: var(--text-light);
}

.contact-item i {
  margin-right: 8px;
  width: 16px;
  color: var(--primary);
}

.seller-activity {
  text-align: left;
}

.activity-item {
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 8px;
}

.activity-item i {
  color: var(--primary);
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.related-products h2 {
  margin-bottom: 15px;
}

.related-products .products-grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

@media (max-width: 768px) {
  .detail-content {
    flex-direction: column;
  }
  
  .detail-images {
    margin-bottom: 20px;
  }
  
  .main-image {
    height: 300px;
  }
  
  .thumbnail-container {
    justify-content: center;
  }
  
  .seller-header {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .seller-stats {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-buttons .btn {
    width: 100%;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
}
/* 状态标签样式 */
.status-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 10px;
  font-weight: bold;
}

.status-online {
  background-color: #d4edda;
  color: #155724;
}

.status-offline {
  background-color: #f8d7da;
  color: #721c24;
}

.status-sold {
  background-color: #fff3cd;
  color: #856404;
}
</style>
