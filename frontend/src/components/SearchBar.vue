<template>
  <div class="search-bar-container">
    <div class="search-bar">
      <i class="fas fa-search"></i>
      <input 
        type="text" 
        placeholder="搜索商品..." 
        v-model="searchQuery"
        @keyup.enter="performSearch"
      >
    </div>
  </div>
</template>

<script>
import { useRoute, useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

export default {
  props: {
    initialQuery: String
  },
  
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const searchQuery = ref(props.initialQuery || '')
    
    // 监听路由变化更新搜索词
    watch(() => route.query.q, (newQuery) => {
      searchQuery.value = newQuery || ''
    })
    
    // 记录搜索行为
    const recordSearchBehavior = async (query) => {
      try {
        if (authStore.user) {
          console.log('记录搜索行为:', { query, userId: authStore.user.id })
          await api.recordUserBehavior('search', null, {
            query: query,
            timestamp: new Date().toISOString()
          })
          console.log('搜索行为记录成功')
        }
      } catch (error) {
        console.error('记录搜索行为失败:', error)
      }
    }
    
    const performSearch = async () => {
      if (searchQuery.value.trim()) {
        // 记录搜索行为
        await recordSearchBehavior(searchQuery.value.trim())
        
        // 导航到搜索页面（使用首页代替发现页）
        router.push({ 
          path: '/', 
          query: { 
            q: searchQuery.value.trim(),
            // 添加标识表示这是搜索请求
            search: 'true'
          } 
        })
      }
    }
    
    return {
      searchQuery,
      performSearch
    }
  }
}
</script>

<style scoped>
.search-bar-container {
  flex: 1;
  min-width: 250px;
  max-width: 600px;
  margin: 0 20px;
}

.search-bar {
  position: relative;
}

.search-bar input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border-radius: 30px;
  border: 1px solid var(--border);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.search-bar input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.search-bar i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
}

@media (max-width: 768px) {
  .search-bar-container {
    margin: 10px 0 0 0;
  }
  
  .search-bar input {
    padding: 8px 15px 8px 35px;
  }
}
</style>