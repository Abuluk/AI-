<template>
  <div class="container">
    <div class="product-detail card">
      <div class="detail-header">
        <h1 class="product-title">{{ product.title }}</h1>
        <div class="product-meta">
          <span>{{ product.location }}</span>
          <span>浏览: {{ product.views }}</span>
          <span>发布时间: {{ formatDateTime(product.created_at) }}</span>
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
          <!-- 新增：商品状态展示 -->
          <div class="detail-condition" v-if="product.condition">
            <strong>商品状态：</strong>{{ getConditionText(product.condition) }}
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
                <button class="btn btn-outline" @click="startChat" :disabled="isOwner">
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
                    <i class="fas fa-envelope"></i>
                    <span>联系方式：{{ seller.contact }}</span>
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
      <!-- 点赞按钮 -->
      <button class="btn btn-outline like-btn" :class="{ liked: product.liked_by_me }" @click="toggleLike" :disabled="likeLoading">
        <i class="fas fa-thumbs-up"></i> {{ product.liked_by_me ? '已点赞' : '点赞' }} ({{ product.like_count || 0 }})
      </button>
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

    <!-- 评论区 -->
    <CommentSection :itemId="product.id" :currentUser="user" :isOwner="isOwner" />
    <div class="related-products">
      <h2 class="section-title">推荐商品</h2>
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
import CommentSection from '@/components/CommentSection.vue'
import api from '@/services/api'
import { mapState } from 'pinia'
import { useAuthStore } from '@/store/auth'

export default {
  components: {
    ProductCard,
    CommentSection
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
        id: this.id,
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
      isFavorited: false,
      isOwner: false,
      likeLoading: false,
    }
  },
  async mounted() {
    await this.fetchItemData()
    if (this.user) {
      this.isOwner = this.user.id === this.product.owner_id
    }
    this.checkFavoriteStatus()
  },
  computed: {
    user() {
      return useAuthStore().user
    },
    isOwner() {
      return this.user && this.user.id === this.product.owner_id;
    }
  },
  watch: {
    async id(newId, oldId) {
      if (newId && newId !== oldId) {
        window.scrollTo(0, 0);
        await this.fetchItemData();
        if (this.user) {
          this.isOwner = this.user.id === this.product.owner_id;
        }
        this.checkFavoriteStatus();
      }
    }
  },
  methods: {
    async fetchItemData() {
      try {
        const response = await api.getItem(this.id)
        this.product = response.data
        this.isOwner = this.user && this.user.id === this.product.owner_id

        // 只做简单图片路径处理
        if (this.product.images) {
          const images = this.product.images.split(',')
          this.product.images = images.map(img => {
            if (!img) return '/default_product.png'
            let path = img.trim().replace(/\\/g, '/')
            if (!path.startsWith('/')) {
              path = '/' + path
            }
            return path
          })
        } else {
          this.product.images = ['/default_product.png']
        }

        this.mainImage = this.product.images[0]

        // 卖家头像
        if (this.product.owner_id) {
          try {
            const sellerResponse = await api.getUser(this.product.owner_id)
            this.seller = sellerResponse.data;
            if (this.seller.avatar && !this.seller.avatar.startsWith('/')) {
              this.seller.avatar = '/static/images/' + this.seller.avatar.replace(/^.*[\\/]/, '');
            }
            if (!this.seller.avatar) {
              this.seller.avatar = '/static/images/default_avatar.png';
            }
          } catch (error) {
            this.seller = { ...this.seller, username: '未知用户', avatar: '/static/images/default_avatar.png' };
          }
        }
        
        // 更新浏览量
        try {
          await api.updateItemViews(this.id)
          this.product.views += 1
        } catch (error) {
          console.warn('更新浏览量失败:', error)
        }
        
        await this.fetchRelatedProducts()
        
      } catch (error) {
        console.error('获取商品详情失败:', error)
      }
    },
    async checkFavoriteStatus() {
      if (!this.user) return;
      try {
        const response = await api.checkFavorite(this.user.id, this.id);
        this.isFavorited = response.data.is_favorited;
      } catch (error) {
        console.error('检查收藏状态失败:', error);
      }
    },
    async toggleFavorite() {
      if (!this.user) {
        return;
      }
      try {
        if (this.isFavorited) {
          await api.removeFavorite(this.user.id, this.id);
          this.product.favorited_count = Math.max(0, (this.product.favorited_count || 1) - 1);
        } else {
          await api.addFavorite(this.user.id, this.id);
          this.product.favorited_count = (this.product.favorited_count || 0) + 1;
        }
        this.isFavorited = !this.isFavorited;
      } catch (error) {
        console.error('切换收藏状态失败:', error);
      }
    },
    async offlineItem() {
      try {
        await api.updateItemStatus(this.id, 'offline');
        this.product.status = 'offline';
      } catch (error) {
        console.error('下架商品失败:', error);
      }
    },
    async onlineItem() {
      try {
        await api.updateItemStatus(this.id, 'online');
        this.product.status = 'online';
      } catch (error) {
        console.error('上架商品失败:', error);
      }
    },
    async purchaseItem() {
      this.$message && this.$message.info
        ? this.$message.info('请联系卖家购买')
        : alert('请联系卖家购买');
    },
    startChat() {
      if (this.isOwner) {
        return;
      }
      if (!this.user) {
        this.$router.push('/login');
        return;
      }
      this.$router.push(`/chat/${this.product.id}/${this.product.owner_id}`);
    },
    formatTime(time) {
      if (!time) return '未知';
      return new Date(time).toLocaleDateString();
    },
    formatJoinDate(time) {
      if (!time) return '未知';
      return new Date(time).toLocaleDateString();
    },
    formatLastActive(time) {
      if (!time) return '未知';
      const lastLogin = new Date(time);
      const now = new Date();
      const diff = Math.floor((now - lastLogin) / (1000 * 60 * 60 * 24));
      if (diff === 0) return '今天';
      if (diff < 30) return `${diff}天前`;
      return '很久以前';
    },
    handleAvatarError(event) {
      event.target.src = '/static/images/default_avatar.png';
      event.target.onerror = null;
    },
    async fetchRelatedProducts() {
      try {
        const response = await api.getItems({ limit: 5, order_by: 'created_at_desc' });
        this.relatedProducts = response.data.filter(p => p.id !== this.product.id).slice(0, 4);
      } catch (error) {
        console.error('获取推荐商品失败:', error);
      }
    },
    formatDateTime(datetime) {
      const date = new Date(datetime);
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      const h = String(date.getHours()).padStart(2, '0');
      const min = String(date.getMinutes()).padStart(2, '0');
      return `${y}-${m}-${d} ${h}:${min}`;
    },
    getConditionText(condition) {
      const conditionMap = {
        'new': '全新',
        'like_new': '几乎全新',
        'good': '轻微使用痕迹',
        'fair': '使用痕迹明显'
      };
      return conditionMap[condition] || condition || '未知状态';
    },
    async toggleLike() {
      if (!this.user) {
        console.log('用户未登录，无法点赞');
        return;
      }
      
      console.log('开始点赞操作，商品ID:', this.product.id, '当前点赞状态:', this.product.liked_by_me);
      this.likeLoading = true;
      
      try {
        if (!this.product.liked_by_me) {
          console.log('发送点赞请求...');
          const res = await api.likeItem(this.product.id);
          console.log('点赞成功，返回数据:', res.data);
          this.product.like_count = res.data.like_count;
          this.product.liked_by_me = true;
        } else {
          console.log('发送取消点赞请求...');
          const res = await api.unlikeItem(this.product.id);
          console.log('取消点赞成功，返回数据:', res.data);
          this.product.like_count = res.data.like_count;
          this.product.liked_by_me = false;
        }
      } catch (error) {
        console.error('点赞操作失败:', error);
        // 可以在这里添加用户提示
        alert('点赞操作失败，请稍后重试');
      } finally {
        this.likeLoading = false;
      }
    },
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

.related-products {
  margin-top: 32px;
  background: none;
  box-shadow: none;
  border-radius: 0;
  padding: 0;
}
.related-products .section-title {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #223;
}
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
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
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
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

.like-btn {
  margin-right: 10px;
  color: #888;
  border-color: #e67e22;
  transition: color 0.2s, border-color 0.2s;
}
.like-btn.liked {
  color: #e67e22;
  border-color: #e67e22;
  font-weight: bold;
}
</style>
