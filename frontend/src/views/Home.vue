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
    
    <div class="main-layout">
      <!-- 左侧求购信息栏 -->
      <div class="buying-requests-sidebar">
        <div class="buying-header">
          <h3>求购信息</h3>
          <button v-if="authStore.user" @click="goToPublishBuyRequest" class="post-request-btn">发布</button>
        </div>
        <div class="buying-list">
          <div v-if="loadingRequests" class="loading-requests">
            <div class="skeleton-request" v-for="n in 3" :key="n"></div>
          </div>
          <div v-else-if="buyingRequests.length === 0" class="empty-requests">
            暂无求购信息
          </div>
          <div v-else class="request-items">
            <div v-for="request in buyingRequests" :key="request.id" class="request-item" @click="goToBuyRequestDetail(request.id)">
              <div class="request-title">{{ request.title }}</div>
              <div class="request-footer">
                <span class="request-price">¥{{ request.budget }}</span>
                <span class="request-user-name">
                  <img v-if="request.user && request.user.avatar_url" :src="request.user.avatar_url" alt="头像" style="width:20px;height:20px;border-radius:50%;margin-right:4px;vertical-align:middle;">
                  {{ request.user ? request.user.username : '未知用户' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要内容区域 -->
      <div class="main-content">
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

      <!-- 右侧低价推荐栏 -->
      <div class="cheap-deals-sidebar">
        <div class="cheap-deals-header">
          <h3>低价好物</h3>
        </div>
        <div class="cheap-deals-list">
          <div v-if="loadingCheapDeals" class="loading-deals">
            <div class="skeleton-deal" v-for="n in 3" :key="n"></div>
          </div>
          <div v-else-if="cheapDeals.length === 0" class="empty-deals">
            暂无低价商品
          </div>
          <div v-else class="deal-items">
            <div v-for="deal in cheapDeals" :key="deal.id" class="deal-item" @click="goToItemDetail(deal.id)">
              <div class="deal-title">{{ deal.title }}</div>
              <div class="deal-footer">
                <span class="deal-price">¥{{ deal.price }}</span>
                <span class="deal-user-name">{{ deal.user.username }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProductCard from '@/components/ProductCard.vue'
import { useAuthStore } from '@/store/auth'
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import api from '@/services/api';

export default {
  name: 'HomeView',
  components: {
    ProductCard,
  },
  setup() {
    const authStore = useAuthStore();
    const formatDateTime = (datetime) => {
      if (!datetime) return '未知';
      const date = new Date(datetime);
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      const h = String(date.getHours()).padStart(2, '0');
      const min = String(date.getMinutes()).padStart(2, '0');
      return `${y}-${m}-${d} ${h}:${min}`;
    };
    // 防御式 user
    const user = computed(() => authStore.user || {});
    return {
      authStore,
      formatDateTime,
      user
    };
  },
  data() {
    return {
      sortOption: 'newest',
      products: [],
      loading: false,
      error: null,
      pagination: {
        page: 1,
        limit: 30
      },
      hasMore: true,
      buyingRequests: [],
      loadingRequests: false,
      cheapDeals: [],
      loadingCheapDeals: false
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
    this.fetchBuyingRequests();
    this.fetchCheapDeals();
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  },
  watch: {
    '$route.query.q': {
      handler() {
        this.pagination.page = 1;
        this.hasMore = true;
        this.fetchSellingItems();
      },
      immediate: true
    },
    sortOption: {
      handler() {
        this.pagination.page = 1;
        this.hasMore = true;
        this.fetchSellingItems();
      }
    }
  },
  methods: {
    async fetchSellingItems(isLoadMore = false) {
      if (this.loading) return;
      this.loading = true;
      try {
        const q = this.$route.query.q;
        let response;
        const params = {
          skip: (this.pagination.page - 1) * this.pagination.limit,
          limit: this.pagination.limit,
          order_by: this.getOrderByParam()
        };
        if (q) {
          response = await api.searchItems(q, params);
        } else {
          response = await api.getItems(params);
        }
        const items = response.data;
        if (isLoadMore) {
          this.products = [...this.products, ...items];
        } else {
          this.products = items;
        }
        this.hasMore = items.length === this.pagination.limit;
      } catch (error) {
        this.error = 'Failed to load products. Please try again later.';
        console.error('Error loading selling items:', error);
      } finally {
        this.loading = false;
      }
    },
    getOrderByParam() {
      switch(this.sortOption) {
        case 'newest': return 'created_at_desc';
        case 'price_asc': return 'price_asc';
        case 'price_desc': return 'price_desc';
        default: return 'created_at_desc';
      }
    },
    handleScroll() {
      if (this.loading || !this.hasMore) return;
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const docHeight = document.documentElement.scrollHeight;
      if (scrollTop + windowHeight >= docHeight - 100) {
        this.pagination.page++;
        this.fetchSellingItems(true);
      }
    },
    goToLogin() {
      this.$router.push('/login')
    },
    handleLogout() {
      this.authStore.logout()
    },
    goToProfile() {
      this.$router.push('/profile');
    },
    async fetchBuyingRequests() {
      this.loadingRequests = true;
      try {
        const response = await api.getBuyRequests({ skip: 0, limit: 10 });
        this.buyingRequests = response.data;
      } catch (error) {
        console.error('Error loading buying requests:', error);
      } finally {
        this.loadingRequests = false;
      }
    },
    async fetchCheapDeals() {
      this.loadingCheapDeals = true;
      try {
        this.cheapDeals = [
          {
            id: 1,
            title: "二手 iPad Air 4",
            price: 2000,
            user: {
              username: "李四"
            }
          },
          {
            id: 2,
            title: "99新 AirPods Pro",
            price: 800,
            user: {
              username: "王五"
            }
          }
        ];
      } catch (error) {
        console.error('Error loading cheap deals:', error);
      } finally {
        this.loadingCheapDeals = false;
      }
    },
    goToItemDetail(itemId) {
      this.$router.push(`/item/${itemId}`);
    },
    goToPublishBuyRequest() {
      this.$router.push('/publish-buy-request');
    },
    goToBuyRequestDetail(id) {
      this.$router.push(`/buy-request/${id}`)
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

/* 容器样式调整 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
}

.page-title {
  margin-top: 0;
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

/* 主布局样式 */
.main-layout {
  position: relative;
  max-width: 1000px;
  margin: 0 auto;
}

/* 左侧求购信息栏样式 */
.buying-requests-sidebar {
  position: absolute;
  left: -260px;
  top: 80px;
  width: 200px;
  background: transparent;
  padding: 0;
  box-shadow: none;
}

.buying-header {
  background: transparent;
  padding: 0;
  margin-bottom: 16px;
  box-shadow: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.buying-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
}

.post-request-btn {
  padding: 4px 8px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background-color 0.2s;
  margin-left: 8px;
  white-space: nowrap;
}

.post-request-btn:hover {
  background-color: #3aa776;
}

.request-items {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: auto;
  max-height: 600px;
  overflow-y: auto;
  padding: 1px;
}

.request-items::-webkit-scrollbar {
  width: 4px;
}

.request-items::-webkit-scrollbar-track {
  background: transparent;
}

.request-items::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 2px;
}

.request-items::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

.request-item {
  border: none;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
}

.request-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.request-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.request-price {
  font-size: 1.2rem;
  color: #f56c6c;
  font-weight: bold;
}

.request-user-name {
  font-size: 0.9rem;
  color: #666;
}

.request-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

/* 加载状态样式 */
.loading-requests {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-request {
  height: 60px;
  background: #f0f0f0;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

.empty-requests {
  text-align: center;
  padding: 12px;
  color: #999;
  font-size: 0.9rem;
}

/* 主要内容区域样式 */
.main-content {
  width: 100%;
}

/* 右侧低价推荐栏样式 */
.cheap-deals-sidebar {
  position: absolute;
  right: -260px;
  top: 80px;
  width: 200px;
  background: transparent;
  padding: 0;
}

.cheap-deals-header {
  background: transparent;
  padding: 0;
  margin-bottom: 16px;
  box-shadow: none;
}

.cheap-deals-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
}

.deal-items {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: auto;
  max-height: 600px;
  overflow-y: auto;
  padding: 1px;
}

.deal-item {
  border: none;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
}

.deal-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.deal-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.deal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.deal-price {
  font-size: 1.2rem;
  color: #f56c6c;
  font-weight: bold;
}

.deal-user-name {
  font-size: 0.9rem;
  color: #666;
}

.loading-deals {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-deal {
  height: 60px;
  background: #f0f0f0;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

.empty-deals {
  text-align: center;
  padding: 12px;
  color: #999;
  font-size: 0.9rem;
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .buying-requests-sidebar {
    position: static;
    margin-bottom: 20px;
    width: 100%;
  }
  
  .request-items {
    height: auto;
    max-height: 300px;
  }
  
  .main-layout {
    max-width: 100%;
  }
  
  .cheap-deals-sidebar {
    position: static;
    margin-top: 20px;
    width: 100%;
  }
  
  .deal-items {
    max-height: 300px;
  }
}
</style>