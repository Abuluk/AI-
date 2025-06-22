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
    
    <div v-if="loading" class="loading-state">
      <div class="skeleton-card" v-for="n in 4" :key="n"></div>
    </div>
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchSellingItems" class="btn btn-primary">重试</button>
    </div>
    <div v-else-if="products.length === 0" class="empty-state">
      <p>暂无在售商品</p>
    </div>
    <div v-else class="products-grid">
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
import SearchBar from '@/components/SearchBar.vue'
import { ref, onMounted, watch } from 'vue';
import api from '@/services/api';

export default {
  name: 'HomeView',
  components: {
    ProductCard,
    SearchBar 
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
      sortOption: 'newest',
      products: [],
      loading: false,
      error: null,
      pagination: {
        page: 1,
        limit: 10
      }
    }
  },
  computed: {
    sortedProducts() {
      const products = [...this.products]
      const parseTime = (t) => {
        if (!t) return 0
        let date
        if (typeof t === 'string') {
          let iso = t.replace(' ', 'T')
          if (!iso.endsWith('Z')) iso += 'Z'
          date = new Date(iso)
        } else {
          date = new Date(t)
        }
        return isNaN(date.getTime()) ? 0 : date.getTime()
      }
      switch(this.sortOption) {
        case 'price_asc':
          return products.sort((a, b) => a.price - b.price)
        case 'price_desc':
          return products.sort((a, b) => b.price - a.price)
        case 'newest':
          return products.sort((a, b) => parseTime(b.created_at) - parseTime(a.created_at))
        default:
          return products
      }
    }
  },
  mounted() {
    this.fetchSellingItems();
  },
  watch: {
    '$route.query.q': {
      handler() {
        this.fetchSellingItems();
      },
      immediate: true
    },
    sortOption: {
      handler() {
        this.fetchSellingItems();
      }
    }
  },
  methods: {
    async fetchSellingItems() {
      this.loading = true;
      try {
        const q = this.$route.query.q;
        let response;
        
        // 构建请求参数，包括排序参数
        const params = {
          skip: (this.pagination.page - 1) * this.pagination.limit,
          limit: this.pagination.limit
        };
        
        // 根据排序选项添加排序参数
        switch(this.sortOption) {
          case 'newest':
            params.order_by = 'created_at_desc';
            break;
          case 'price_asc':
            params.order_by = 'price_asc';
            break;
          case 'price_desc':
            params.order_by = 'price_desc';
            break;
          default:
            params.order_by = 'created_at_desc'; // 默认按最新发布排序
        }
        
        if (q) {
          response = await api.searchItems(q, params);
        } else {
          response = await api.getItems(params);
        }
        this.products = response.data;
      } catch (error) {
        this.error = 'Failed to load products. Please try again later.';
        console.error('Error loading selling items:', error);
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
      } finally {
        this.loading = false;
      }
    },
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

.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.skeleton-card {
  height: 300px;
  background: #f0f0f0;
  border-radius: 8px;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 0.5; }
}

.error-state {
  text-align: center;
  padding: 40px;
  color: #e74c3c;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #777;
}
</style>