<template>
  <div id="app">
    <!-- NavBar Start: 内容已直接内联 -->
    <header class="navbar-header">
      <div class="navbar">
        <router-link to="/" class="logo">
          <i class="fas fa-fish"></i>
          <span>上电校园二手站</span>
        </router-link>
        
        <SearchBar :initialQuery="route.query.q" />
        
        <div class="nav-icons">
          <router-link to="/messages" class="nav-icon" title="消息">
            <i class="fas fa-comment-alt"></i>
            <span v-if="authStore.isAuthenticated && unreadCount > 0" class="badge">
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </router-link>
          
          <router-link to="/profile" class="nav-icon" title="我的">
            <i class="fas fa-user-circle"></i>
          </router-link>
          
          <router-link to="/friends" class="nav-icon" title="好友">
            <i class="fas fa-user-friends"></i>
          </router-link>
          
          <router-link to="/publish" class="nav-icon" title="发布">
            <i class="fas fa-plus-circle"></i>
          </router-link>
          
          <router-link v-if="isAdmin" to="/admin" class="nav-icon admin-icon" title="管理员控制台">
            <i class="fas fa-cog"></i>
          </router-link>
        </div>
      </div>
    </header>
    <!-- NavBar End -->

    <router-view />
    <BottomNav />
  </div>
</template>

<script>
// 原 NavBar 的导入
import SearchBar from '@/components/SearchBar.vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import api from '@/services/api'

// 原 App.vue 的导入
import BottomNav from '@/components/BottomNav.vue'

export default {
  components: {
    // 合并后的组件
    SearchBar,
    BottomNav
  },
  setup() {
    // --- 原 NavBar 的 setup ---
    const route = useRoute()
    const authStore = useAuthStore()
    const unreadCount = ref(0)
    let intervalId = null
    
    const isAdmin = computed(() => authStore.user && authStore.user.is_admin)
    
    const loadUnreadCount = async () => {
      if (!authStore.isAuthenticated) {
        unreadCount.value = 0
        return
      }
      try {
        const response = await api.getUnreadCount()
        unreadCount.value = response.data?.unread_count || 0
      } catch (error) {
        console.error('获取未读消息数量失败:', error)
        unreadCount.value = 0
      }
    }

    watch(() => authStore.isAuthenticated, (isAuth) => {
      if (isAuth) {
        loadUnreadCount()
      } else {
        unreadCount.value = 0
      }
    }, { immediate: true })
    
    onMounted(() => {
      if (authStore.isAuthenticated) {
        loadUnreadCount()
      }
      intervalId = setInterval(() => {
        if (authStore.isAuthenticated) {
          loadUnreadCount()
        }
      }, 30000)
    })
    
    onUnmounted(() => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    })

    // --- 返回合并后的数据 ---
    return {
      route,
      authStore,
      isAdmin,
      unreadCount
    }
  }
}
</script>

<style>
:root {
  --primary: #3498db;
  --primary-dark: #2980b9;
  --secondary: #f1f2f6;
  --success: #2ecc71;
  --danger: #e74c3c;
  --text: #2c3e50;
  --text-light: #7f8c8d;
  --border: #dfe6e9;
  --card-bg: #ffffff;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background-color: var(--secondary);
  color: var(--text);
  line-height: 1.6;
  padding-bottom: 60px; /* 为底部导航留空间 */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.page-title {
  font-size: 1.5rem;
  margin: 20px 0;
  font-weight: 600;
}

.card {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 20px;
  border-radius: 5px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
  flex: 1;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
}

.btn-outline:hover {
  background-color: rgba(52, 152, 219, 0.1);
}

@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
}

/* --- 原 NavBar 的 scoped style --- */
/* 注意：为了在App.vue中生效，scoped被移除了，并用特定类名.navbar-header来限定作用域 */
.navbar-header {
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

button, .btn {
  box-sizing: border-box;
}
/* 避免全局 .btn 影响评论区按钮横排 */
.comment-actions > button,
.reply-btn, .delete-btn, .expand-btn, .like-btn, .submit-btn {
  display: inline-flex !important;
  width: auto !important;
  min-width: 0 !important;
  max-width: none !important;
  margin: 0 !important;
}
</style>