<template>
  <div class="container">
    <!-- 顶部导航栏 -->
    <div class="header-nav">
      <div class="logo">好物精选</div>
      <div class="user-area">
        <div v-if="authStore.user" class="user-info">
          
          <!-- 个人主页入口 -->
          <div class="profile-link" @click="goToProfile">
            <img :src="authStore.user.avatar" alt="用户头像" class="user-avatar">
            <span class="user-name">{{ authStore.user.username }}</span>
          </div>
          
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
        <button v-else @click="goToLogin" class="login-btn">登录/注册</button>
      </div>
    </div>
    
    <h1 class="page-title">发现好物</h1>
    
    <div class="section-header">
      <h2 class="section-title">推荐商品</h2>
      <div class="sort-options">
        <select v-model="sortOption">
          <option value="default">综合排序</option>
          <option value="price_asc">价格从低到高</option>
          <option value="price_desc">价格从高到低</option>
          <option value="newest">最新发布</option>
        </select>
      </div>
    </div>
    
    <div class="products-grid">
      <ProductCard 
        v-for="product in sortedProducts" 
        :key="product.id" 
        :product="product" 
      />
    </div>
  </div>
</template>

<script>
import ProductCard from '@/components/ProductCard.vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { ref } from 'vue';

export default {
  name: 'HomeView',
  components: {
    ProductCard
  },
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    return {
      authStore,
      router
    }
  },
  data() {
    return {
      sortOption: 'default',
      products: [
        { 
          id: 1, 
          title: 'Apple iPhone 13 128GB 蓝色 国行在保', 
          price: 4299, 
          image: 'https://picsum.photos/300/300?random=1', 
          location: '北京', 
          views: 128,
          createdAt: '2023-06-10'
        },
        { 
          id: 2, 
          title: '华为MateBook X Pro 13.9英寸笔记本电脑', 
          price: 6999, 
          image: 'https://picsum.photos/300/300?random=2', 
          location: '上海', 
          views: 89,
          createdAt: '2023-06-12'
        },
        { 
          id: 3, 
          title: 'Sony PlayStation 5 光驱版 双手柄套装', 
          price: 4499, 
          image: 'https://picsum.photos/300/300?random=3', 
          location: '广州', 
          views: 210,
          createdAt: '2023-06-15'
        },
        { 
          id: 4, 
          title: '佳能 EOS R5 全画幅微单相机 95新', 
          price: 18999, 
          image: 'https://picsum.photos/300/300?random=4', 
          location: '深圳', 
          views: 45,
          createdAt: '2023-06-16'
        },
        { 
          id: 5, 
          title: 'Bose QuietComfort 45 无线降噪耳机', 
          price: 1599, 
          image: 'https://picsum.photos/300/300?random=5', 
          location: '杭州', 
          views: 76,
          createdAt: '2023-06-17'
        },
        { 
          id: 6, 
          title: 'Kindle Paperwhite 4 32GB 黑色 全新未拆', 
          price: 998, 
          image: 'https://picsum.photos/300/300?random=6', 
          location: '南京', 
          views: 62,
          createdAt: '2023-06-18'
        }
      ]
    }
  },
  computed: {
    sortedProducts() {
      const products = [...this.products]
      
      switch(this.sortOption) {
        case 'price_asc':
          return products.sort((a, b) => a.price - b.price)
        case 'price_desc':
          return products.sort((a, b) => b.price - a.price)
        case 'newest':
          return products.sort((a, b) => 
            new Date(b.createdAt) - new Date(a.createdAt))
        default:
          return products
      }
    }
  },
  methods: {
    // 跳转到登录页面
    goToLogin() {
      this.router.push('/login')
    },
    
    // 退出登录
    handleLogout() {
      this.authStore.logout()
      // 可以添加登出后的操作，如跳转页面等
    },

    goToProfile() {
      this.router.push('/profile');
    }
    
  }
}
</script>

<style scoped>
/* 顶部导航栏样式 */
.header-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #42b983; /* Vue主题色 */
}

.profile-link {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.2s;
}

.profile-link:hover {
  background-color: #f5f5f5;
}

.user-area {
  display: flex;
  align-items: center;
}

.login-btn {
  padding: 8px 16px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #3aa776;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}

.user-name {
  font-size: 0.9rem;
}

.logout-btn {
  padding: 5px 10px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.logout-btn:hover {
  background: #eee;
}

/* 原有样式保持不变 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 600;
}

.sort-options select {
  padding: 8px 12px;
  border-radius: 5px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}
</style>