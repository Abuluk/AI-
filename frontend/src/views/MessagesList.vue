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
      
      <!-- 消息列表优化 -->
      <div class="conversations-list">
        <div 
          v-for="conversation in filteredConversations" 
          :key="conversation.id"
          class="conversation-item"
          :class="{ 
            unread: conversation.unread,
            active: activeConversationId === conversation.id
          }"
          @click="selectConversation(conversation)"
        >
          <!-- 用户头像和状态 -->
          <div class="avatar-container">
            <img :src="conversation.user.avatar" class="avatar">
            <span v-if="conversation.user.online" class="online-status"></span>
          </div>
          
          <!-- 消息详情 -->
          <div class="conversation-details">
            <div class="conversation-header">
              <span class="username">{{ conversation.user.username }}</span>
              <span class="time">{{ formatTime(conversation.lastMessage.timestamp) }}</span>
            </div>
            
            <!-- 关联商品 -->
            <div class="product-info" v-if="conversation.product">
              <span class="product-label">相关商品：</span>
              <span class="product-title">{{ conversation.product.title }}</span>
            </div>
            
            <div class="conversation-preview">
              <!-- 最后一条消息预览 -->
              <p class="message-preview">
                <span v-if="conversation.lastMessage.sender === 'me'" class="sent-indicator">
                  我：
                </span>
                {{ conversation.lastMessage.content }}
              </p>
              
              <!-- 未读标记 -->
              <div class="message-status">
                <span v-if="conversation.unread" class="unread-badge">
                  {{ conversation.unreadCount }}
                </span>
                <i v-if="conversation.lastMessage.sender === 'me' && !conversation.unread" 
                   class="fas fa-check read-indicator"></i>
              </div>
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
export default {
  data() {
    return {
      searchQuery: '',
      isSearchFocused: false,
      activeTab: 'all',
      activeConversationId: null,
      tabs: [
        { id: 'all', label: '全部' },
        { id: 'unread', label: '未读' },
        { id: 'products', label: '商品咨询' }
      ],
      conversations: [
        {
          id: 1,
          user: {
            id: 2,
            username: '李四',
            avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
            online: true
          },
          product: {
            id: 1,
            title: 'Apple iPhone 13 128GB 蓝色',
            price: 4299,
            thumbnail: 'https://picsum.photos/100/100?random=1'
          },
          lastMessage: {
            content: '你好，请问手机还在吗？最低多少钱能出？',
            timestamp: new Date(Date.now() - 1000 * 60 * 5), // 5分钟前
            sender: 'other'
          },
          unread: true,
          unreadCount: 3
        },
        {
          id: 2,
          user: {
            id: 3,
            username: '王五',
            avatar: 'https://randomuser.me/api/portraits/men/22.jpg',
            online: false
          },
          product: {
            id: 3,
            title: 'Sony PlayStation 5',
            price: 4499,
            thumbnail: 'https://picsum.photos/100/100?random=3'
          },
          lastMessage: {
            content: '好的，我明天下午过来取',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1天前
            sender: 'me'
          },
          unread: false,
          unreadCount: 0
        },
        {
          id: 3,
          user: {
            id: 4,
            username: '赵六',
            avatar: 'https://randomuser.me/api/portraits/women/68.jpg',
            online: true
          },
          product: {
            id: 5,
            title: 'Bose QuietComfort 45 耳机',
            price: 1599,
            thumbnail: 'https://picsum.photos/100/100?random=5'
          },
          lastMessage: {
            content: '耳机音质怎么样？有发票吗？',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3天前
            sender: 'other'
          },
          unread: false,
          unreadCount: 0
        }
      ]
    }
  },
  computed: {
    filteredConversations() {
      let conversations = this.conversations;
      
      // 按标签筛选
      if (this.activeTab === 'unread') {
        conversations = conversations.filter(conv => conv.unread);
      } else if (this.activeTab === 'products') {
        conversations = conversations.filter(conv => conv.product);
      }
      
      // 搜索筛选
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        conversations = conversations.filter(conv => 
          conv.user.username.toLowerCase().includes(query) || 
          (conv.product && conv.product.title.toLowerCase().includes(query)) ||
          conv.lastMessage.content.toLowerCase().includes(query)
        );
      }
      
      // 按时间排序（最近消息在前）
      return conversations.sort((a, b) => 
        new Date(b.lastMessage.timestamp) - new Date(a.lastMessage.timestamp)
      );
    }
  },
  methods: {
    formatTime(timestamp) {
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
    },
    selectConversation(conversation) {
      this.activeConversationId = conversation.id;
      this.$router.push({ name: 'Chat', params: { id: conversation.id } });
    },
    clearSearch() {
      this.searchQuery = '';
      this.isSearchFocused = false;
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

.avatar-container {
  position: relative;
  margin-right: 15px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.online-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #4caf50;
  border: 2px solid white;
}

.conversation-details {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.username {
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

.product-info {
  font-size: 0.85rem;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-label {
  color: #666;
}

.product-title {
  color: #42b983;
  font-weight: 500;
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
  max-width: 80%;
  margin: 0;
}

.sent-indicator {
  color: #42b983;
  font-weight: 500;
}

.message-status {
  display: flex;
  align-items: center;
}

.unread-badge {
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

.read-indicator {
  color: #aaa;
  font-size: 0.85rem;
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
</style>