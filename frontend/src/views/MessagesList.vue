<template>
  <div class="container">
    <h1 class="page-title">消息</h1>
    
    <div class="messages-container card">
      <div class="search-conversations">
        <i class="fas fa-search"></i>
        <input type="text" placeholder="搜索对话" v-model="searchQuery">
      </div>
      
      <div class="conversations-list">
        <div 
          v-for="conversation in filteredConversations" 
          :key="conversation.id"
          class="conversation-item"
          :class="{ unread: conversation.unread }"
          @click="$router.push({ name: 'Chat', params: { id: conversation.id } })"
        >
          <img :src="conversation.user.avatar" class="avatar">
          <div class="conversation-details">
            <div class="conversation-header">
              <span class="username">{{ conversation.user.username }}</span>
              <span class="time">{{ conversation.lastMessage.time }}</span>
            </div>
            <div class="conversation-preview">
              <p class="message-preview">{{ conversation.lastMessage.content }}</p>
              <span v-if="conversation.unread" class="unread-badge">{{ conversation.unreadCount }}</span>
            </div>
          </div>
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
      conversations: [
        {
          id: 1,
          user: {
            id: 2,
            username: '李四',
            avatar: 'https://randomuser.me/api/portraits/women/44.jpg'
          },
          product: {
            id: 1,
            title: 'Apple iPhone 13 128GB 蓝色'
          },
          lastMessage: {
            content: '你好，请问手机还在吗？最低多少钱能出？',
            time: '10:30',
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
            avatar: 'https://randomuser.me/api/portraits/men/22.jpg'
          },
          product: {
            id: 3,
            title: 'Sony PlayStation 5'
          },
          lastMessage: {
            content: '好的，我明天下午过来取',
            time: '昨天',
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
            avatar: 'https://randomuser.me/api/portraits/women/68.jpg'
          },
          product: {
            id: 5,
            title: 'Bose QuietComfort 45 耳机'
          },
          lastMessage: {
            content: '耳机音质怎么样？有发票吗？',
            time: '6月15日',
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
      if (!this.searchQuery) return this.conversations
      
      const query = this.searchQuery.toLowerCase()
      return this.conversations.filter(conv => 
        conv.user.username.toLowerCase().includes(query) || 
        conv.product.title.toLowerCase().includes(query)
      )
    }
  }
}
</script>

<style scoped>
.messages-container {
  padding: 0;
}

.search-conversations {
  position: relative;
  padding: 15px;
  border-bottom: 1px solid var(--border);
}

.search-conversations i {
  position: absolute;
  left: 30px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
}

.search-conversations input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border-radius: 20px;
  border: 1px solid var(--border);
  font-size: 1rem;
  outline: none;
}

.conversations-list {
  max-height: 70vh;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background-color 0.3s;
}

.conversation-item:hover {
  background-color: var(--secondary);
}

.conversation-item.unread {
  background-color: rgba(52, 152, 219, 0.05);
}

.avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.conversation-details {
  flex: 1;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.username {
  font-weight: 600;
}

.time {
  color: var(--text-light);
  font-size: 0.9rem;
}

.conversation-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-preview {
  color: var(--text-light);
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80%;
}

.unread-badge {
  background-color: var(--danger);
  color: white;
  font-size: 0.8rem;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>