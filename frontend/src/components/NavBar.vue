<template>
  <header>
    <div class="navbar">
      <router-link to="/" class="logo">
        <i class="fas fa-fish"></i>
        <span>我不是刘川豪</span>
      </router-link>
      
      <!-- 搜索框组件 - 添加了查询参数绑定 -->
      <SearchBar :initialQuery="route.query.q" />
      
      <div class="nav-icons">
        <router-link to="/messages" class="nav-icon">
          <i class="fas fa-comment-alt"></i>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </router-link>
        <router-link to="/profile" class="nav-icon">
          <i class="fas fa-user-circle"></i>
        </router-link>
        <router-link to="/publish" class="nav-icon">
          <i class="fas fa-plus-circle"></i>
        </router-link>
        <!-- 管理员入口 -->
        <router-link v-if="isAdmin" to="/admin" class="nav-icon admin-icon" title="管理员控制台">
          <i class="fas fa-cog"></i>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script>
import SearchBar from './SearchBar.vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { computed, ref, onMounted, onUnmounted } from 'vue'
import api from '@/services/api'

export default {
  components: {
    SearchBar
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()
    const unreadCount = ref(0)
    let intervalId = null
    
    const isAdmin = computed(() => {
      return authStore.user && authStore.user.is_admin
    })
    
    const loadUnreadCount = async () => {
      if (!authStore.isAuthenticated) {
        unreadCount.value = 0
        return
      }
      
      try {
        const response = await api.getUnreadCount()
        unreadCount.value = response.data.unread_count || 0
      } catch (error) {
        console.error('获取未读消息数量失败:', error)
        // 如果API不可用，使用模拟数据
        unreadCount.value = Math.floor(Math.random() * 5)
      }
    }
    
    onMounted(() => {
      loadUnreadCount()
      // 每30秒刷新一次未读消息数量
      intervalId = setInterval(loadUnreadCount, 30000)
    })
    
    onUnmounted(() => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    })
    
    return {
      route,
      isAdmin,
      unreadCount
    }
  }
}
</script>

<style scoped>
header {
  background-color: var(--card-bg);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary);
  text-decoration: none;
  min-width: 120px;
}

.logo i {
  margin-right: 8px;
}

.nav-icons {
  display: flex;
  gap: 20px;
  min-width: 120px;
  justify-content: flex-end;
}

.nav-icon {
  position: relative;
  color: var(--text);
  font-size: 1.2rem;
  text-decoration: none;
}

.nav-icon i {
  transition: color 0.3s;
}

.nav-icon:hover i,
.nav-icon.router-link-active i {
  color: var(--primary);
}

.badge {
  position: absolute;
  top: -5px;
  right: -8px;
  background-color: var(--danger);
  color: white;
  font-size: 0.7rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-icon {
  color: #e74c3c !important;
}

.admin-icon:hover i,
.admin-icon.router-link-active i {
  color: #c0392b !important;
}

@media (max-width: 768px) {
  .navbar {
    padding: 10px 15px;
    flex-wrap: wrap;
  }
  
  .logo {
    order: 1;
  }
  
  .nav-icons {
    order: 2;
  }
  
  .search-bar-container {
    order: 3;
    width: 100%;
    margin-top: 10px;
    max-width: 100%;
  }
  
  .search-bar {
    max-width: 100%;
  }
}
</style>