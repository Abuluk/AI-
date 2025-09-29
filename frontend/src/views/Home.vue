<template>
  <div class="container">
    <!-- 顶部导航栏 -->
    <div class="header-nav">
      <div class="logo">好物精选</div>
      <div class="user-area">
        <div v-if="authStore.user" class="user-info">
          <div class="profile-link" @click="goToProfile">
            <img :src="getUserAvatar(authStore.user?.avatar)" alt="用户头像" class="user-avatar" @error="handleImageError">
            <span class="user-name">{{ authStore.user.username }}</span>
          </div>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
        <button v-else @click="goToLogin" class="login-btn">登录/注册</button>
      </div>
    </div>
    <!-- banner区紧跟在导航栏下方 -->
    <div class="activity-banner-carousel">
      <template v-if="activityBanners.length">
        <div class="carousel-wrapper">
          <div class="carousel-slide" v-for="(banner, idx) in activityBanners" :key="idx" v-show="currentBanner === idx">
            <a :href="banner.link" target="_blank" style="width:100%;height:100%;display:block;">
              <img :src="banner.img" alt="活动图" class="activity-img" />
            </a>
          </div>
          <div class="carousel-controls" v-if="activityBanners.length > 1">
            <button @click="prevBanner">‹</button>
            <button @click="nextBanner">›</button>
          </div>
          <div class="carousel-dots" v-if="activityBanners.length > 1">
            <span v-for="(banner, idx) in activityBanners" :key="idx" :class="{active: currentBanner === idx}" @click="goToBanner(idx)"></span>
          </div>
        </div>
      </template>
      <template v-else>
        <div style="width:100%;height:60px;"></div>
      </template>
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
          <div class="filter-options">
            <input
              v-model="selectedLocation"
              placeholder="输入地区（如上海、北京）"
              class="location-input"
              @keyup.enter="onLocationInput"
              @blur="onLocationInput"
            />
            <select v-model="selectedCategory">
              <option value="">全部分类</option>
              <option v-for="cat in CATEGORY_MAP" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <div class="sort-options">
              <select v-model="sortOption">
                <option value="default">综合排序</option>
                <option value="dynamic_sort">智能排序</option>
                <option value="bigdata_recommendation">大数据推荐</option>
                <option value="price_asc">价格从低到高</option>
                <option value="price_desc">价格从高到低</option>
                <option value="newest">最新发布</option>
              </select>
            </div>
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
        <div style="text-align:center;margin-bottom:16px;" v-if="!aiEnabled">
          <button @click="enableAIRecommend" class="login-btn">启动AI推荐</button>
        </div>
        <div class="cheap-deals-header">
          <h3>AI智能推荐</h3>
          <div class="ai-status" :class="{ 'ai-active': aiAnalysis.success }">
            <span v-if="aiEnabled && aiAnalysis.success" class="ai-indicator">🤖 AI分析</span>
            <span v-else-if="aiEnabled && !aiAnalysis.success" class="ai-indicator">📊 基础推荐</span>
            <span v-else class="ai-indicator">💡 点击启动AI</span>
          </div>
        </div>
        <!-- AI分析结果展示 -->
        <div v-if="aiEnabled && aiAnalysis.success && aiAnalysis.analysis" class="ai-analysis">
          <div class="analysis-text">{{ aiAnalysis.analysis }}</div>
        </div>
        <div class="cheap-deals-list">
          <!-- AI未启用时显示最低价商品 -->
          <template v-if="!aiEnabled">
            <div class="deal-items">
              <div v-for="deal in lowestDeals" :key="deal.id" class="deal-item" @click="goToItemDetail(deal.id)">
                <div class="deal-title">{{ deal.title }}</div>
                <div class="deal-price-section">
                  <span class="deal-price">¥{{ deal.price }}</span>
                </div>
                <div class="deal-footer">
                  <span class="deal-user-name">
                    {{ deal.owner && deal.owner.username ? deal.owner.username : '未知用户' }}
                  </span>
                  <span class="deal-condition">{{ getConditionText(deal.condition) }}</span>
                </div>
              </div>
            </div>
          </template>
          <!-- AI启用后显示AI推荐商品 -->
          <template v-else>
            <div v-if="loadingCheapDeals" class="loading-deals">
              <div class="skeleton-deal" v-for="n in 3" :key="n"></div>
              <div class="loading-text">AI智能推荐加载中…</div>
            </div>
            <div v-else-if="cheapDeals.length === 0 && !aiAnalysis.success && !loadingCheapDeals" class="empty-deals">
              暂无推荐商品
            </div>
            <div v-else class="deal-items">
              <div v-for="deal in cheapDeals" :key="deal.id" class="deal-item" @click="goToItemDetail(deal.id)">
                <div class="deal-title">{{ deal.title }}</div>
                <div class="deal-price-section">
                  <span class="deal-price">¥{{ deal.price }}</span>
                  <span v-if="deal.ai_reason" class="ai-reason">{{ deal.ai_reason }}</span>
                </div>
                <div class="deal-footer">
                  <span class="deal-user-name">
                    {{ deal.owner && deal.owner.username ? deal.owner.username : '未知用户' }}
                  </span>
                  <span class="deal-condition">{{ getConditionText(deal.condition) }}</span>
                </div>
                <!-- 显示推荐类型标识 -->
                <div v-if="deal.recommendation_type" class="recommendation-type">
                  <span v-if="deal.recommendation_type === 'ai_behavior_based'" class="type-badge ai-based">AI推荐</span>
                  <span v-else-if="deal.recommendation_type === 'basic'" class="type-badge basic">热门</span>
                </div>
              </div>
            </div>
          </template>
        </div>
        
        <!-- 市场洞察 -->
        <div v-if="aiEnabled && aiAnalysis.success && aiAnalysis.market_insights" class="market-insights">
          <h4>市场洞察</h4>
          <p>{{ aiAnalysis.market_insights }}</p>
        </div>
        
        <!-- AI服务状态提示 -->
        <div v-if="aiEnabled && !aiAnalysis.success && aiAnalysis.message" class="ai-status-message">
          <p>{{ aiAnalysis.message }}</p>
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

// 分类映射表
const CATEGORY_MAP = [
  { id: 1, name: '手机数码' },
  { id: 2, name: '电脑办公' },
  { id: 3, name: '家用电器' },
  { id: 4, name: '服装鞋包' },
  { id: 5, name: '美妆护肤' },
  { id: 6, name: '图书文娱' },
  { id: 7, name: '运动户外' },
  { id: 8, name: '家居家装' },
  { id: 9, name: '食品饮料' },
  { id: 10, name: '母婴用品' },
  { id: 11, name: '汽车用品' },
  { id: 12, name: '宠物用品' },
  { id: 13, name: '乐器音响' },
  { id: 14, name: '收藏品' },
  { id: 15, name: '游戏动漫' },
  { id: 16, name: '珠宝配饰' },
  { id: 17, name: '箱包旅行' },
  { id: 18, name: '园艺花卉' },
  { id: 19, name: '手工DIY' },
  { id: 20, name: '其他' }
];

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
      user,
      CATEGORY_MAP
    };
  },
  data() {
    return {
      sortOption: 'default',
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
      loadingCheapDeals: false,
      aiAnalysis: {
        success: false,
        analysis: null,
        market_insights: null,
        message: null
      },
      aiEnabled: false,
      lowestDeals: [],
      selectedLocation: '',
      selectedCategory: '',
      activityBanners: [],
      currentBanner: 0,
      bannerTimer: null,
      hasPromotedItems: false,
    }
  },
  computed: {
    promotedProducts() {
      return this.sortedProducts.filter(p => p.is_promoted)
    },
    normalProducts() {
      return this.sortedProducts.filter(p => !p.is_promoted)
    },
    sortedProducts() {
      let products = [...this.products];
      
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
      
      // 先按推广商品优先排序，然后在每个组内按选择的排序方式排序
      products.sort((a, b) => {
        // 首先按推广商品优先排序
        if (a.is_promoted && !b.is_promoted) return -1;
        if (!a.is_promoted && b.is_promoted) return 1;
        
        // 如果都是推广商品或都不是推广商品，则按选择的排序方式排序
        switch(this.sortOption) {
          case 'price_asc':
            return a.price - b.price
          case 'price_desc':
            return b.price - a.price
          case 'newest':
            return parseTime(b.created_at) - parseTime(a.created_at)
          default:
            return 0
        }
      });
      
      return products;
    }
  },
  mounted() {
    this.fetchSellingItems();
    this.fetchBuyingRequests();
    this.fetchLowestDeals();
    this.fetchActivityBanners();
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
    if (this.bannerTimer) clearInterval(this.bannerTimer);
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
        // 如果选择大数据推荐但用户未登录，提示登录
        if (this.sortOption === 'bigdata_recommendation' && !this.authStore.user) {
          alert('大数据推荐需要登录后才能使用，请先登录！');
          this.sortOption = 'default'; // 重置为默认排序
          return;
        }
        
        this.pagination.page = 1;
        this.hasMore = true;
        this.fetchSellingItems();
      }
    },
    selectedLocation() {
      this.pagination.page = 1;
      this.hasMore = true;
      this.fetchSellingItems();
    },
    selectedCategory() {
      this.pagination.page = 1;
      this.hasMore = true;
      
      // 记录分类点击行为
      if (this.selectedCategory) {
        const categoryName = this.CATEGORY_MAP.find(cat => cat.id == this.selectedCategory)?.name || '未知分类';
        this.recordUserBehavior('category_click', null, {
          category_id: this.selectedCategory,
          category_name: categoryName
        });
      }
      
      this.fetchSellingItems();
    }
  },
  methods: {
    onLocationInput() {
      this.pagination.page = 1;
      this.hasMore = true;
      this.fetchSellingItems();
    },
    async fetchSellingItems(isLoadMore = false) {
      if (this.loading) return;
      this.loading = true;
      try {
        const q = this.$route.query.q;
        let response;
        const params = {
          skip: (this.pagination.page - 1) * this.pagination.limit,
          limit: this.pagination.limit,
          order_by: this.getOrderByParam(),
          location: this.selectedLocation,
          category: this.selectedCategory ? Number(this.selectedCategory) : undefined,
          status: 'online', // 只获取在售商品
          sold: false, // 只获取未售出商品
          // 为大数据推荐添加用户ID
          user_id: this.authStore.user?.id
        };
        
        // 如果是第一页且没有搜索条件，优先获取推广商品
        if (this.pagination.page === 1 && !q && !this.selectedLocation && !this.selectedCategory) {
          console.log('尝试获取推广商品...');
          try {
            const promotedResponse = await api.getPromotedItems();
            console.log('推广商品API响应:', promotedResponse.data);
            if (promotedResponse.data && promotedResponse.data.length > 0) {
              // 将推广商品放在前面
              const promotedItems = promotedResponse.data.map(item => ({
                ...item,
                is_promoted: true
              }));
              console.log('处理后的推广商品:', promotedItems);
              const remainingLimit = this.pagination.limit - promotedItems.length;
              
              if (remainingLimit > 0) {
                // 获取剩余的商品
                const remainingParams = {
                  ...params,
                  limit: remainingLimit,
                  exclude_promoted: true // 排除已推广的商品
                };
                console.log('获取剩余商品参数:', remainingParams);
                const remainingResponse = await api.getItems(remainingParams);
                const remainingItems = remainingResponse.data.map(item => ({
                  ...item,
                  is_promoted: false
                }));
                console.log('剩余商品:', remainingItems);
                
                // 合并推广商品和普通商品
                this.products = [...promotedItems, ...remainingItems];
                this.hasMore = remainingItems.length === remainingLimit;
                this.hasPromotedItems = true;
                // 调试：输出products首位
                console.log('合并后的商品列表:', this.products);
                console.log('首页products首位：', this.products[0]);
                this.loading = false;
                return;
              }
            } else {
              console.log('没有推广商品');
            }
          } catch (promotedError) {
            console.warn('获取推广商品失败，使用默认商品:', promotedError);
          }
        } else {
          console.log('不满足推广商品获取条件:', {
            page: this.pagination.page,
            q: q,
            location: this.selectedLocation,
            category: this.selectedCategory
          });
        }
        
        // 如果没有推广商品或获取失败，使用原来的逻辑
        if (q) {
          response = await api.searchItems(q, params);
        } else {
          response = await api.getItems(params);
        }
        
        // 检查大数据推荐的错误响应
        if (this.sortOption === 'bigdata_recommendation' && response.data && response.data.error) {
          alert(response.data.message || '大数据推荐需要登录后才能使用！');
          this.sortOption = 'default'; // 重置为默认排序
          this.fetchSellingItems(); // 重新获取默认排序的商品
          return;
        }
        
        let items = response.data;
        
        // 过滤掉已售出和下架的商品
        items = items.filter(item => item.status === 'online' && !item.sold);
        
        // 为所有商品添加is_promoted标识
        items = items.map(item => ({
          ...item,
          is_promoted: false
        }));
        
        // 地区模糊匹配（忽略大小写）
        if (this.selectedLocation) {
          const loc = this.selectedLocation.trim().toLowerCase();
          items = items.filter(item =>
            item.location && item.location.toLowerCase().includes(loc)
          );
        }
        // 分类严格匹配数字ID
        if (this.selectedCategory) {
          items = items.filter(item => Number(item.category) === Number(this.selectedCategory));
        }
        if (isLoadMore) {
          this.products = [...this.products, ...items];
        } else {
          this.products = items;
          this.hasPromotedItems = false;
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
        case 'dynamic_sort': return 'dynamic_sort';
        case 'bigdata_recommendation': return 'bigdata_recommendation';
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
    async fetchLowestDeals() {
      // 获取最低价商品，取前10个
      try {
        const params = {
          skip: 0,
          limit: 10,
          order_by: 'price_asc',
        };
        const response = await api.getItems(params);
        this.lowestDeals = (response.data || []).filter(
          item => item.status === 'online' && !item.sold
        );
      } catch (e) {
        this.lowestDeals = [];
      }
    },
    enableAIRecommend() {
      this.aiEnabled = true;
      this.fetchCheapDeals();
    },
    async fetchCheapDeals() {
      this.loadingCheapDeals = true;
      try {
        // 使用新的AI推荐API
        const response = await api.getAIRecommendations(10);
        
        if (response.data.success) {
          // AI分析成功
          this.aiAnalysis = {
            success: true,
            analysis: response.data.analysis,
            market_insights: response.data.market_insights,
            message: null
          };
          this.cheapDeals = response.data.recommendations || [];
        } else {
          // AI分析失败，使用备用数据
          this.aiAnalysis = {
            success: false,
            analysis: null,
            market_insights: null,
            message: response.data.message || "AI分析服务暂时不可用"
          };
          this.cheapDeals = response.data.recommendations || [];
        }
      } catch (error) {
        console.error('Error loading AI recommendations:', error);
        // 如果API调用失败，显示错误提示
        this.aiAnalysis = {
          success: false,
          analysis: null,
          market_insights: null,
          message: "AI服务连接失败，暂无法获取推荐"
        };
        this.cheapDeals = [];
      } finally {
        this.loadingCheapDeals = false;
      }
    },
    goToItemDetail(itemId) {
      // 记录用户点击行为
      this.recordUserBehavior('click', itemId);
      this.$router.push(`/item/${itemId}`);
    },
    
    // 记录用户行为
    async recordUserBehavior(behaviorType, itemId = null, behaviorData = null) {
      try {
        if (this.authStore.user) {
          console.log('记录用户行为:', { behaviorType, itemId, behaviorData, userId: this.authStore.user.id });
          const response = await api.recordUserBehavior(behaviorType, itemId, behaviorData);
          console.log('行为记录成功:', response);
        } else {
          console.log('用户未登录，跳过行为记录');
        }
      } catch (error) {
        console.error('记录用户行为失败:', error);
        console.error('错误详情:', error.response?.data || error.message);
      }
    },
    goToPublishBuyRequest() {
      this.$router.push('/publish-buy-request');
    },
    goToBuyRequestDetail(id) {
      this.$router.push(`/buy-request/${id}`)
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
    async fetchActivityBanners() {
      try {
        const res = await api.getActivityBanners();
        console.log('活动页banner接口返回', res);
        this.activityBanners = res.data.value || [];
        this.currentBanner = 0;
        if (this.activityBanners.length > 1) {
          this.startBannerAutoPlay();
        }
      } catch (e) {
        console.error('获取活动页banner失败', e);
        this.activityBanners = [];
      }
    },
    startBannerAutoPlay() {
      if (this.bannerTimer) clearInterval(this.bannerTimer);
      this.bannerTimer = setInterval(() => {
        this.nextBanner();
      }, 10000);
    },
    nextBanner() {
      this.currentBanner = (this.currentBanner + 1) % this.activityBanners.length;
    },
    prevBanner() {
      this.currentBanner = (this.currentBanner - 1 + this.activityBanners.length) % this.activityBanners.length;
    },
    goToBanner(idx) {
      this.currentBanner = idx;
    },
    handleImageError(e) {
      e.target.src = '/static/images/default_avatar.png';
    },
    getUserAvatar(avatar) {
      if (!avatar) return '/static/images/default_avatar.png';
      // 修复HTTPS协议问题
      if (avatar.startsWith('https://127.0.0.1:8000')) {
        return avatar.replace('https://127.0.0.1:8000', 'http://127.0.0.1:8000');
      }
      return avatar;
    },
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

.filter-options {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-options select {
  padding: 8px 12px;
  border-radius: 5px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
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

.deal-price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.deal-price {
  font-size: 1.2rem;
  color: #f56c6c;
  font-weight: bold;
}

.deal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.deal-user-name {
  font-size: 0.9rem;
  color: #666;
}

.deal-condition {
  font-size: 0.9rem;
  color: #666;
}

.ai-status {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 5px 10px;
  border-radius: 4px;
  background-color: #f0f0f0;
  margin-top: 10px;
}

.ai-active {
  background-color: #42b983;
}

.ai-indicator {
  font-size: 0.9rem;
  font-weight: 600;
  color: white;
  margin-left: 5px;
}

.ai-analysis {
  margin-top: 10px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.analysis-text {
  font-size: 1rem;
  color: #333;
}

.market-insights {
  margin-top: 10px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.market-insights h4 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.market-insights p {
  font-size: 1rem;
  color: #666;
}

.ai-status-message {
  margin-top: 10px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

/* 加载状态样式 */
.loading-deals {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.skeleton-deal {
  height: 60px;
  background: #f0f0f0;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}

.loading-text {
  margin-top: 10px;
  color: #42b983;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 1px;
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

.location-input {
  padding: 8px 12px;
  border-radius: 5px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: text;
  width: 120px;
}

.activity-banner-carousel {
  width: 100%;
  max-width: 1200px;
  aspect-ratio: 5 / 1;
  min-height: 80px;
  margin: 24px auto;
  overflow: hidden;
  background: transparent;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carousel-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
}
.carousel-slide {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  left: 0;
  top: 0;
  opacity: 1;
  transition: opacity 0.5s;
}
.activity-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.carousel-controls {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 10;
  pointer-events: none;
}
.carousel-controls button {
  background: transparent !important;
  border: none;
  color: #fff;
  font-size: 28px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  pointer-events: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 11;
  transition: background 0.2s;
  opacity: 1;
}
.carousel-controls button:hover {
  background: transparent !important;
}
.carousel-dots {
  position: absolute;
  bottom: 16px;
  left: 0;
  width: 100%;
  text-align: center;
}
.carousel-dots span {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin: 0 4px;
  background: #ddd;
  border-radius: 50%;
  cursor: pointer;
}
  .carousel-dots .active {
    background: #409eff;
  }

  /* 推荐类型标识样式 */
  .recommendation-type {
    position: absolute;
    top: 8px;
    right: 8px;
  }

  .type-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 500;
    color: white;
  }

  .type-badge.ai-based {
    background: linear-gradient(135deg, #42b983, #3aa776);
  }

  .type-badge.basic {
    background: linear-gradient(135deg, #f56c6c, #e74c3c);
  }

/* 推广商品标识样式 */
.promotion-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 10px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  animation: pulse 2s infinite;
}

.promotion-badge i {
  font-size: 0.7rem;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.promoted-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.normal-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .activity-banner-carousel {
    height: 120px;
    min-height: 80px;
  }
  .activity-img {
    height: 120px;
    min-height: 80px;
    width: 100%;
    object-fit: cover;
  }
  .carousel-controls button {
    font-size: 20px;
    width: 28px;
    height: 28px;
  }
  .carousel-dots span {
    width: 8px;
    height: 8px;
  }
}
</style>