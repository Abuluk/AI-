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
</style>