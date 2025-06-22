<template>
  <div class="container">
    <div class="header-nav">
      <div class="logo">好物精选</div>
      <div class="page-header">
        <h1><i class="fas fa-comments"></i> 我的消息</h1>
      </div>
    </div>
    
    <div class="messages-container card">
      <!-- 搜索框优化 -->
      <div class="search-conversations">
        <div class="search-input-container">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            placeholder="搜索对话" 
            v-model="searchQuery"
            @focus="isSearchFocused = true"
            @blur="isSearchFocused = false"
            :class="{ focused: isSearchFocused }"
          >
          <button v-if="searchQuery" @click="clearSearch" class="clear-search">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <!-- 添加筛选标签 -->
      <div class="filter-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="skeleton-row" v-for="n in 3" :key="n"></div>
      </div>
      
      <!-- 消息列表优化 -->
      <div v-else class="conversations-list">
        <div 
          v-for="conversation in filteredConversations" 
          :key="conversation.item_id"
          class="conversation-item"
          :class="{ 
            unread: conversation.unread_count > 0,
            active: activeConversationId === conversation.item_id
          }"
          @click="selectConversation(conversation)"
        >
          <!-- 商品图片 -->
          <div class="item-image-container">
            <img 
              :src="getItemImage(conversation.item_images)" 
              :alt="conversation.item_title"
              class="item-image"
            >
            <span v-if="conversation.unread_count > 0" class="unread-badge">
              {{ conversation.unread_count }}
            </span>
          </div>
          
          <!-- 对话详情 -->
          <div class="conversation-details">
            <div class="conversation-header">
              <span class="item-title">{{ conversation.item_title }}</span>
              <span class="time">{{ formatTime(conversation.last_message_time) }}</span>
            </div>
            
            <div class="conversation-info">
              <span class="price">¥{{ conversation.item_price }}</span>
              <span class="message-count">{{ conversation.message_count }}条消息</span>
            </div>
            
            <div class="conversation-preview">
              <p class="message-preview">
                <span v-if="conversation.is_seller" class="seller-indicator">
                  [卖家]
                </span>
                {{ getLastMessagePreview(conversation) }}
              </p>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="filteredConversations.length === 0" class="empty-state">
          <i class="fas fa-comment-slash"></i>
          <p>{{ searchQuery ? '没有找到相关对话' : '暂无消息' }}</p>
          <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
            清除搜索
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

export default {
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const conversations = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const isSearchFocused = ref(false)
    const activeTab = ref('all')
    const activeConversationId = ref(null)
    
    const tabs = [
      { id: 'all', label: '全部' },
      { id: 'unread', label: '未读' },
      { id: 'buying', label: '购买' },
      { id: 'selling', label: '出售' }
    ]
    
    const filteredConversations = computed(() => {
      let filtered = conversations.value;
      
      // 按标签筛选
      if (activeTab.value === 'unread') {
        filtered = filtered.filter(conv => conv.unread_count > 0);
      } else if (activeTab.value === 'buying') {
        filtered = filtered.filter(conv => !conv.is_seller);
      } else if (activeTab.value === 'selling') {
        filtered = filtered.filter(conv => conv.is_seller);
      }
      
      // 搜索筛选
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        filtered = filtered.filter(conv => 
          conv.item_title.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    })
    
    const loadConversations = async () => {
      if (!authStore.isAuthenticated) {
        router.push('/login')
        return
      }
      
      loading.value = true
      try {
        const response = await api.getConversations()
        conversations.value = response.data
      } catch (error) {
        console.error('加载对话失败:', error)
        // 如果API不可用，使用模拟数据
        conversations.value = getMockConversations()
      } finally {
        loading.value = false
      }
    }
    
    const getMockConversations = () => {
      return [
        {
          item_id: 1,
          item_title: 'Apple iPhone 13 128GB 蓝色',
          item_price: 4299,
          item_images: 'https://picsum.photos/100/100?random=1',
          message_count: 5,
          last_message_time: new Date(Date.now() - 1000 * 60 * 5),
          unread_count: 3,
          is_seller: false
        },
        {
          item_id: 2,
          item_title: 'Sony PlayStation 5',
          item_price: 4499,
          item_images: 'https://picsum.photos/100/100?random=2',
          message_count: 8,
          last_message_time: new Date(Date.now() - 1000 * 60 * 60 * 24),
          unread_count: 0,
          is_seller: true
        }
      ]
    }
    
    const formatTime = (timestamp) => {
      const now = new Date();
      const date = new Date(timestamp);
      const diff = now - date;
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (minutes < 1) return '刚刚';
      if (minutes < 60) return `${minutes}分钟前`;
      if (hours < 24) return `${hours}小时前`;
      if (days === 1) return '昨天';
      if (days < 7) return `${days}天前`;
      
      return date.toLocaleDateString();
    }
    
    const getItemImage = (images) => {
      if (!images) return '/static/images/default.jpg'
      const imageList = images.split(',')
      return imageList[0] || '/static/images/default.jpg'
    }
    
    const getLastMessagePreview = (conversation) => {
      // 这里可以根据实际需求显示最后一条消息的预览
      return `关于"${conversation.item_title}"的对话`
    }
    
    const selectConversation = (conversation) => {
      activeConversationId.value = conversation.item_id;
      router.push({ name: 'Chat', params: { id: conversation.item_id } });
    }
    
    const clearSearch = () => {
      searchQuery.value = '';
      isSearchFocused.value = false;
    }
    
    onMounted(() => {
      loadConversations()
    })
    
    return {
      conversations,
      loading,
      searchQuery,
      isSearchFocused,
      activeTab,
      activeConversationId,
      tabs,
      filteredConversations,
      formatTime,
      getItemImage,
      getLastMessagePreview,
      selectConversation,
      clearSearch
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #42b983;
}

.page-header {
  flex: 1;
  display: flex;
  justify-content: center;
}

.page-header h1 {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.messages-container {
  padding: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.search-conversations {
  padding: 15px;
  border-bottom: 1px solid var(--border);
  background-color: #fafafa;
}

.search-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-container i {
  position: absolute;
  left: 15px;
  color: #aaa;
}

.search-input-container input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border-radius: 25px;
  border: 1px solid #ddd;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.search-input-container input.focused {
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.2);
}

.clear-search {
  position: absolute;
  right: 15px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 5px;
}

.clear-search:hover {
  color: #666;
}

.filter-tabs {
  display: flex;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
}

.filter-tabs button {
  padding: 8px 16px;
  background: none;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 10px;
  transition: all 0.2s;
}

.filter-tabs button.active {
  background-color: #42b983;
  color: white;
}

.conversations-list {
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.conversation-item:hover {
  background-color: #f9f9f9;
}

.conversation-item.unread {
  background-color: rgba(66, 185, 131, 0.05);
}

.conversation-item.active {
  background-color: #e8f5e9;
}

.item-image-container {
  position: relative;
  margin-right: 15px;
}

.item-image {
  width: 56px;
  height: 56px;
  border-radius: 8px;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.unread-badge {
  position: absolute;
  top: -5px;
  right: -8px;
  background-color: #ff4d4f;
  color: white;
  font-size: 0.75rem;
  min-width: 22px;
  height: 22px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.conversation-details {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.item-title {
  font-weight: 600;
  font-size: 1.05rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
}

.time {
  color: #888;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.conversation-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-bottom: 6px;
}

.price {
  color: #ff6b35;
  font-weight: 600;
}

.message-count {
  color: #888;
}

.conversation-preview {
  display: flex;
  justify-content: space-between;
}

.message-preview {
  color: #666;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
  margin: 0;
}

.seller-indicator {
  color: #42b983;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.3;
}

.empty-state p {
  margin-bottom: 15px;
}

.clear-btn {
  padding: 8px 20px;
  background-color: #f5f5f5;
  border: none;
  border-radius: 20px;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background-color: #eee;
}

.loading-state {
  padding: 20px;
}

.skeleton-row {
  height: 80px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 10px;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>