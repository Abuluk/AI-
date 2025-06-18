<template>
  <div class="container">
    <div class="profile-header card">
      <div class="user-info">
        <img :src="user.avatar" class="user-avatar">
        <div class="user-details">
          <h2 class="username">{{ user.username }}</h2>
          <p class="user-bio">{{ user.bio || '这个人很懒，什么都没留下' }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <strong>{{ user.followers }}</strong>
              <span>粉丝</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.following }}</strong>
              <span>关注</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.items }}</strong>
              <span>商品</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="profile-actions">
        <button class="btn btn-outline">
          <i class="fas fa-cog"></i> 设置
        </button>
        <button class="btn btn-primary">
          <i class="fas fa-edit"></i> 编辑资料
        </button>
      </div>
    </div>
    
    <div class="profile-tabs card">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <div class="tab-content">
        <div v-if="activeTab === 'selling'" class="selling-items">
          <h3>在售商品 ({{ sellingItems.length }})</h3>
          <div class="products-grid">
            <ProductCard 
              v-for="item in sellingItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
        </div>
        
        <div v-if="activeTab === 'sold'" class="sold-items">
          <h3>已售商品 ({{ soldItems.length }})</h3>
          <div v-if="soldItems.length > 0" class="products-grid">
            <ProductCard 
              v-for="item in soldItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
          <div v-else class="empty-state">
            <i class="fas fa-box-open"></i>
            <p>暂无已售商品</p>
          </div>
        </div>
        
        <div v-if="activeTab === 'favorites'" class="favorite-items">
          <h3>收藏的商品 ({{ favoriteItems.length }})</h3>
          <div class="products-grid">
            <ProductCard 
              v-for="item in favoriteItems" 
              :key="item.id" 
              :product="item" 
            />
          </div>
        </div>
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
  data() {
    return {
      activeTab: 'selling',
      tabs: [
        { id: 'selling', label: '在售' },
        { id: 'sold', label: '已售' },
        { id: 'favorites', label: '收藏' }
      ],
      user: {
        id: 1,
        username: '张三',
        avatar: 'https://randomuser.me/api/portraits/men/32.jpg',
        bio: '数码产品爱好者，喜欢分享好物',
        followers: 128,
        following: 56,
        items: 12
      },
      sellingItems: [
        { 
          id: 1, 
          title: 'Apple iPhone 13 128GB 蓝色', 
          price: 4299, 
          image: 'https://picsum.photos/300/300?random=1', 
          location: '北京', 
          views: 128 
        },
        { 
          id: 2, 
          title: '华为MateBook X Pro', 
          price: 6999, 
          image: 'https://picsum.photos/300/300?random=2', 
          location: '北京', 
          views: 89 
        },
        { 
          id: 3, 
          title: 'Sony PlayStation 5', 
          price: 4499, 
          image: 'https://picsum.photos/300/300?random=3', 
          location: '北京', 
          views: 210 
        }
      ],
      soldItems: [
        { 
          id: 4, 
          title: '佳能 EOS R5 全画幅微单', 
          price: 18999, 
          image: 'https://picsum.photos/300/300?random=4', 
          location: '北京', 
          views: 45 
        }
      ],
      favoriteItems: [
        { 
          id: 5, 
          title: 'Bose QuietComfort 45 耳机', 
          price: 1599, 
          image: 'https://picsum.photos/300/300?random=5', 
          location: '上海', 
          views: 76 
        },
        { 
          id: 6, 
          title: 'Kindle Paperwhite 4', 
          price: 998, 
          image: 'https://picsum.photos/300/300?random=6', 
          location: '杭州', 
          views: 62 
        }
      ]
    }
  }
}
</script>

<style scoped>
.profile-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  margin-bottom: 20px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 20px;
}

.user-details {
  flex: 1;
}

.username {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.user-bio {
  color: var(--text-light);
  margin-bottom: 15px;
}

.user-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-item strong {
  display: block;
  font-size: 1.2rem;
  margin-bottom: 3px;
}

.stat-item span {
  color: var(--text-light);
  font-size: 0.9rem;
}

.profile-actions {
  display: flex;
  gap: 15px;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}

.tabs button {
  padding: 12px 20px;
  background: none;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-light);
  cursor: pointer;
  position: relative;
}

.tabs button.active {
  color: var(--primary);
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background-color: var(--primary);
}

.tab-content h3 {
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--text-light);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.3;
}

@media (max-width: 768px) {
  .user-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .user-avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .profile-actions {
    flex-direction: column;
  }
  
  .tabs {
    overflow-x: auto;
  }
}
</style>