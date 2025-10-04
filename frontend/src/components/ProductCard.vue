<template>
  <div class="product-card-wrapper">
    <router-link :to="`/item/${product.id}`" class="product-card" @click="handleProductClick">
      <div class="image-container">
        <img :src="getFirstImage(product)" 
             :alt="product.title" 
             class="product-image"
             @error="handleImageError">
        <!-- 添加下架/已售状态显示 -->
        <div v-if="product.status === 'offline'" class="sold-badge">已下架</div>
        <div v-else-if="product.sold" class="sold-badge">已售出</div>
        <!-- 添加推广标识 -->
        <div v-if="product.is_promoted" class="promotion-badge">推广</div>
        <!-- 添加大数据推荐标识 -->
        <div v-if="product.is_bigdata_recommended" class="bigdata-badge">大数据推荐</div>
        <!-- 添加AI增强推荐标识 -->
        <div v-if="product.is_ai_recommended" class="ai-badge">AI增强推荐</div>
        <!-- 添加综合排序标识 -->
        <div v-if="product.is_comprehensive_sort" class="comprehensive-badge">综合排序</div>
      </div>
      
      <div class="product-info">
        <h3 class="product-title">{{ product.title }}</h3>
        <div class="product-price">¥{{ product.price }}</div>
        <div class="product-meta">
          <span>{{ product.location }}</span>
          <div class="stats">
            <span><i class="fas fa-eye"></i> {{ product.views }}</span>
            <span><i class="fas fa-heart"></i> {{ product.favorited_count || 0 }}</span>
          </div>
        </div>
        <span>发布时间：{{ formatDateTime(product.created_at) }}</span>
      </div>
    </router-link>
    
    <!-- 操作按钮区域 -->
    <div v-if="showActions" class="product-actions">
      <!-- 用户自己的商品按钮 -->
      <div v-if="!isFavorite">
        <!-- 在售商品的按钮 -->
        <div v-if="!product.sold">
          <div class="action-buttons">
            <button 
              v-if="product.status === 'online'"
              class="btn btn-danger btn-sm" 
              @click.stop="offlineItem"
            >
              <i class="fas fa-ban"></i> 下架
            </button>
            <button 
              v-else-if="product.status === 'offline'"
              class="btn btn-success btn-sm" 
              @click.stop="onlineItem"
            >
              <i class="fas fa-check"></i> 上架
            </button>
            <button 
              v-if="product.status === 'online'"
              class="btn btn-warning btn-sm"
              @click.stop="markSold"
            >
              <i class="fas fa-check-double"></i> 已售出
            </button>
            
            <!-- 编辑按钮 -->
            <button 
              class="btn btn-primary btn-sm"
              @click.stop="editItem"
              title="编辑商品"
            >
              <i class="fas fa-edit"></i> 编辑
            </button>
            
            <!-- 删除按钮 - 放在其他按钮右边 -->
            <button 
              class="btn btn-delete btn-sm"
              @click.stop="deleteItem"
              title="删除商品"
            >
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
        
        <!-- 已售商品的删除按钮 -->
        <div v-else>
          <button 
            class="btn btn-delete btn-sm"
            @click.stop="deleteItem"
            title="删除商品"
          >
            <i class="fas fa-trash"></i> 删除
          </button>
        </div>
      </div>
      
      <!-- 收藏商品的按钮 -->
      <div v-else>
        <button 
          class="btn btn-danger btn-sm"
          @click.stop="unfavoriteItem"
          title="取消收藏"
        >
          <i class="fas fa-heart-broken"></i> 取消收藏
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  props: {
    product: {
      type: Object,
      required: true
    },
    showActions: {
      type: Boolean,
      default: false
    },
    isFavorite: {
      type: Boolean,
      default: false
    }
  },
  emits: ['offline', 'online', 'sold', 'delete', 'unfavorite', 'edit'],
  methods: {
    getFirstImage(product) {
      if (!product || !product.images) {
        return this.defaultImage;
      }
      const firstImage = product.images.split(',')[0].trim();
      // 如果已经是完整URL（包含http），直接返回
      if (firstImage.startsWith('http')) {
        return firstImage;
      }
      // 如果是相对路径，添加/前缀
      if (firstImage.startsWith('/')) {
        return firstImage;
      }
      return `/${firstImage}`;
    },
    
    // 处理图片加载错误
    handleImageError(event) {
      // 使用默认图片替换
      event.target.src = this.defaultImage;
      
      // 防止无限循环
      event.target.onerror = null;
    },
    offlineItem() {
      // 触发下架事件
      this.$emit('offline', this.product.id);
    },
    onlineItem() {
      // 触发上架事件
      this.$emit('online', this.product.id);
    },
    markSold() {
      this.$emit('sold', this.product.id);
    },
    deleteItem() {
      // 触发删除事件
      this.$emit('delete', this.product.id);
    },
    unfavoriteItem() {
      this.$emit('unfavorite', this.product.id);
    },
    editItem() {
      // 触发编辑事件
      this.$emit('edit', this.product.id);
    },
    
    // 处理商品点击事件
    async handleProductClick() {
      // 记录用户浏览商品行为
      try {
        console.log('ProductCard记录用户行为:', { 
          behaviorType: 'view', 
          itemId: this.product.id,
          product: this.product.title 
        });
        const response = await api.recordUserBehavior('view', this.product.id, {
          title: this.product.title,
          category: this.product.category,
          price: this.product.price
        });
        console.log('ProductCard行为记录成功:', response);
      } catch (error) {
        console.error('记录商品浏览行为失败:', error);
        console.error('错误详情:', error.response?.data || error.message);
      }
    }
  },
  data() {
    return {
      // 使用公开URL或内联base64图片
      //defaultImage: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="100%" height="100%" fill="%23f0f0f0"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-family="Arial" font-size="16">无图片</text></svg>'
      
      // 或者使用在线默认图片：
       defaultImage: '/static/images/default_product.jpg'
    }
  },
  setup() {
    const formatDateTime = (datetime) => {
      const date = new Date(datetime);
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      const h = String(date.getHours()).padStart(2, '0');
      const min = String(date.getMinutes()).padStart(2, '0');
      return `${y}-${m}-${d} ${h}:${min}`;
    };
    return { formatDateTime };
  }
}
</script>

<style scoped>
/* 原有样式保持不变 */
.product-card-wrapper {
  position: relative;
}

.product-card {
  background-color: var(--card-bg);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  display: block;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  height: 200px;
  width: 100%;
  object-fit: cover;
  border-bottom: 1px solid var(--border);
}

.product-info {
  padding: 15px;
}

.product-title {
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 42px;
}

.product-price {
  color: var(--danger);
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-light);
  font-size: 0.9rem;
}

.image-container {
  position: relative;
}

.sold-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--danger);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.promotion-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--success);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.bigdata-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.ai-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(45deg, #ff6b35 0%, #f7931e 50%, #ffd23f 100%);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  animation: ai-glow 2s ease-in-out infinite alternate;
}

.comprehensive-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(45deg, #4CAF50 0%, #8BC34A 100%);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

@keyframes ai-glow {
  from {
    box-shadow: 0 2px 4px rgba(0,0,0,0.3), 0 0 10px rgba(255, 107, 53, 0.5);
  }
  to {
    box-shadow: 0 2px 4px rgba(0,0,0,0.3), 0 0 20px rgba(255, 107, 53, 0.8);
  }
}

.stats {
  display: flex;
  gap: 10px;
}

.product-actions {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-success {
  background-color: #27ae60;
  color: white;
}

.btn-success:hover {
  background-color: #229954;
}

.btn-warning {
  background-color: #f39c12;
  color: white;
}

.btn-warning:hover {
  background-color: #d68910;
}

.btn-delete {
  background-color: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background-color: #c0392b;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .product-image {
    height: 160px;
  }
}
</style>