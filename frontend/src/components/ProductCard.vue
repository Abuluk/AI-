<template>
  <div class="product-card-wrapper">
    <router-link :to="`/item/${product.id}`" class="product-card">
      <div class="image-container">
        <img :src="getFirstImage(product)" 
             :alt="product.title" 
             class="product-image"
             @error="handleImageError">
        <!-- 添加下架/已售状态显示 -->
        <div v-if="product.status === 'offline'" class="sold-badge">已下架</div>
        <div v-else-if="product.sold" class="sold-badge">已售出</div>
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
      </div>
    </router-link>
    
    <!-- 操作按钮区域 -->
    <div v-if="showActions && !product.sold" class="product-actions">
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
    </div>
  </div>
</template>

<script>
export default {
  props: {
    product: {
      type: Object,
      required: true
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  emits: ['offline', 'online'],
  methods: {
    // 获取并处理第一张图片
    getFirstImage(product) {
      // 处理图片路径：转换反斜杠为正斜杠，确保以 /static/ 开头
      const normalizePath = (path) => {
        if (!path) return '';
        
        // 替换所有反斜杠为正斜杠
        let normalized = path.replace(/\\/g, '/');
        
        // 确保路径以 /static/ 开头
        // 确保路径以绝对路径 /static/ 开头
        if (!normalized.startsWith('/static/')) {
          // 如果路径以 static/ 开头，添加前导斜杠
          if (normalized.startsWith('static/')) {
            normalized = `/${normalized}`;
          } else {
            normalized = `/static/${normalized}`;
          }
        }
        
        return normalized;
      };
      
      // 尝试获取第一张图片
      let firstImage = '';
      
      // 调试日志：检查商品对象是否包含图片相关字段
      if (!product.images && !product.image) {
        console.warn(`商品ID: ${product.id} 缺少图片字段(images/image)`);
      }
      
      if (product.images) {
        // 分割图片字符串并获取第一张
        const images = product.images.split(',');
        if (images.length > 0) {
          firstImage = images[0].trim();
        } else {
          console.warn(`商品ID: ${product.id} images字段为空`);
        }
      } else if (product.image) {
        firstImage = product.image;
      } else {
        // 尝试从其他可能的字段获取图片路径（根据后端实际情况调整）
        // 如果后端有其他图片字段名，请在此处添加
        // 尝试从其他可能的字段获取图片路径（根据后端实际情况调整）
        firstImage = product.img_url || product.picture || '';
        if (firstImage) {
          console.log(`商品ID: ${product.id} 使用备用图片字段: ${firstImage}`);
        } else {
          // 作为最后的备选方案：使用商品ID构造默认图片路径
          // 假设图片命名格式为：{id}_*.jpg
          // 构造具体的默认图片路径格式（移除通配符）
          firstImage = `${product.id}_default.jpg`;
          console.error(`商品ID: ${product.id} 严重警告: 后端未返回图片路径，使用默认路径: ${firstImage}。请检查后端API是否正确返回images/image字段`);
        }
      }
      
      // 返回处理后的路径或默认图片URL
      return normalizePath(firstImage) || this.defaultImage;
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
    }
  },
  data() {
    return {
      // 使用公开URL或内联base64图片
      //defaultImage: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="100%" height="100%" fill="%23f0f0f0"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-family="Arial" font-size="16">无图片</text></svg>'
      
      // 或者使用在线默认图片：
       defaultImage: 'https://picsum.photos/300/300?random=2'
    }
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

@media (max-width: 768px) {
  .product-image {
    height: 160px;
  }
}
</style>