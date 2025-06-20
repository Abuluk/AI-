<template>
  <div class="container">
    <div class="product-detail card">
      <div class="detail-header">
        <h1 class="product-title">{{ product.title }}</h1>
        <div class="product-meta">
          <span>{{ product.location }}</span>
          <span>浏览: {{ product.views }}</span>
          <span>发布时间: {{ product.createdAt }}</span>
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
              <img :src="seller.avatar" class="seller-avatar">
              <div class="seller-details">
                <div class="seller-name">{{ seller.username }}</div>
                <div class="seller-rating">
                  <i class="fas fa-star"></i>
                  <span>4.8 (256评价)</span>
                </div>
              </div>
              <button class="btn btn-outline" @click="startChat">
                <i class="fas fa-comment"></i> 联系卖家
              </button>
            </div>
          </div>
          
          <div class="action-buttons">
            <button class="btn btn-outline">
              <i class="fas fa-heart"></i> 收藏
            </button>
            <button class="btn btn-primary">
              <i class="fas fa-shopping-cart"></i> 立即购买
            </button>
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
          <i class="fas fa-ban"></i> 下架商品
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
        id: 1,
        title: 'Apple iPhone 13 128GB 蓝色 国行在保',
        price: 4299,
        description: '国行在保，99新，全套包装配件齐全，无任何划痕。购买于2022年10月，还有半年保修期。因换新机转让，支持验机。',
        location: '北京',
        views: 129,
        createdAt: '2023-06-10',
        images: [
          'https://picsum.photos/600/600?random=1',
          'https://picsum.photos/600/600?random=2',
          'https://picsum.photos/600/600?random=3',
          'https://picsum.photos/600/600?random=4'
        ]
      },
      seller: {
        id: 1,
        username: '张三',
        avatar: 'https://randomuser.me/api/portraits/men/32.jpg'
      },
      relatedProducts: [
        { 
          id: 7, 
          title: 'Apple iPhone 12 64GB 黑色', 
          price: 3299, 
          image: 'https://picsum.photos/300/300?random=7', 
          location: '北京', 
          views: 98 
        },
        { 
          id: 8, 
          title: 'Apple Watch Series 7 GPS版', 
          price: 2499, 
          image: 'https://picsum.photos/300/300?random=8', 
          location: '上海', 
          views: 45 
        },
        { 
          id: 9, 
          title: 'AirPods Pro 第二代', 
          price: 1499, 
          image: 'https://picsum.photos/300/300?random=9', 
          location: '广州', 
          views: 78 
        }
      ]
    }
  },
  created() {
    this.mainImage = this.product.images[0]
  },
  methods: {
    startChat() {
      this.$router.push({ name: 'Chat', params: { id: this.seller.id } })
    }
  },

  computed: {
  user() {
    return useAuthStore().user
  },
  isOwner() {
    return this.user && this.user.id === this.product.owner_id
  }
},
  async created() {
    await this.fetchItemData()
    this.checkFavoriteStatus()
  },
  methods: {
    async fetchItemData() {
      try {
        // 实际项目中替换为API调用
        // const response = await api.getItem(this.id)
        // this.product = response.data
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 更新浏览量
        // await api.updateItem(this.id, { views: this.product.views + 1 })
        this.product.views += 1
        
        // 获取卖家信息
        // const sellerResponse = await api.getUser(this.product.owner_id)
        // this.seller = sellerResponse.data
      } catch (error) {
        console.error('获取商品数据失败:', error)
      }
    },
    async checkFavoriteStatus() {
      if (!this.user) return
      try {
        // 实际项目中替换为API调用
        // const response = await api.checkFavorite(this.user.id, this.id)
        // this.isFavorited = response.data.isFavorited
        
        // 模拟检查收藏状态
        this.isFavorited = Math.random() > 0.5
      } catch (error) {
        console.error('检查收藏状态失败:', error)
      }
    },
    async toggleFavorite() {
      if (!this.user) {
        this.$router.push('/login')
        return
      }
      
      try {
        if (this.isFavorited) {
          // await api.removeFavorite(this.user.id, this.id)
          console.log(`移除收藏: 用户 ${this.user.id}, 商品 ${this.id}`)
        } else {
          // await api.addFavorite(this.user.id, this.id)
          console.log(`添加收藏: 用户 ${this.user.id}, 商品 ${this.id}`)
        }
        this.isFavorited = !this.isFavorited
      } catch (error) {
        console.error('收藏操作失败:', error)
      }
    },
    async offlineItem() {
      if (confirm('确定要下架该商品吗？下架后其他用户将无法看到此商品。')) {
        try {
          // 实际项目中调用API
          // await api.updateItemStatus(this.product.id, 'offline')
          
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
        // 实际项目中调用API
        // await api.updateItemStatus(this.product.id, 'online')
        
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
  align-items: center;
  padding: 15px;
  background-color: var(--secondary);
  border-radius: 8px;
  margin-bottom: 20px;
}

.seller-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.seller-details {
  flex: 1;
}

.seller-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.seller-rating {
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 5px;
}

.seller-rating i {
  color: #ffc107;
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
  
  .detail-images, .detail-info {
    width: 100%;
    padding: 0;
  }
  
  .detail-images {
    margin-bottom: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
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
