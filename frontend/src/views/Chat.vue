<template>
  <div class="container">
    <div class="chat-header card">
      <router-link to="/messages" class="back-btn">
        <i class="fas fa-arrow-left"></i>
      </router-link>
      <img :src="currentUser.avatar" class="avatar">
      <div class="user-info">
        <div class="username">{{ currentUser.username }}</div>
        <div class="status">在线</div>
      </div>
      <div class="header-actions">
        <button class="action-btn">
          <i class="fas fa-phone-alt"></i>
        </button>
        <button class="action-btn">
          <i class="fas fa-ellipsis-v"></i>
        </button>
      </div>
    </div>
    
    <div class="chat-container card">
      <div class="chat-messages">
        <div 
          v-for="(message, index) in messages" 
          :key="index"
          class="message"
          :class="{
            'sent': message.sender === 'me',
            'received': message.sender === 'other'
          }"
        >
          <img v-if="message.sender === 'other'" :src="currentUser.avatar" class="avatar">
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <button class="input-btn">
          <i class="fas fa-plus"></i>
        </button>
        <input 
          type="text" 
          v-model="newMessage" 
          placeholder="输入消息..." 
          @keyup.enter="sendMessage"
        >
        <button 
          class="input-btn send-btn"
          :disabled="!newMessage.trim()"
          @click="sendMessage"
        >
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>
    
    <div class="product-info card">
      <div class="product-header">
        <h3>相关商品</h3>
        <router-link :to="`/item/${product.id}`">查看商品</router-link>
      </div>
      <div class="product-details">
        <img :src="product.image" class="product-image">
        <div class="product-text">
          <div class="product-title">{{ product.title }}</div>
          <div class="product-price">¥{{ product.price }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      newMessage: '',
      currentUser: {
        id: 2,
        username: '李四',
        avatar: 'https://randomuser.me/api/portraits/women/44.jpg'
      },
      product: {
        id: 1,
        title: 'Apple iPhone 13 128GB 蓝色',
        price: 4299,
        image: 'https://picsum.photos/300/300?random=1'
      },
      messages: [
        {
          content: '你好，请问手机还在吗？',
          time: '10:28',
          sender: 'other'
        },
        {
          content: '还在的，您感兴趣吗？',
          time: '10:29',
          sender: 'me'
        },
        {
          content: '是的，最低多少钱能出？',
          time: '10:30',
          sender: 'other'
        },
        {
          content: '最低4200，几乎全新，还有半年保修',
          time: '10:32',
          sender: 'me'
        },
        {
          content: '能再便宜点吗？4000可以吗？',
          time: '10:33',
          sender: 'other'
        },
        {
          content: '不好意思，这个价格已经是最低了',
          time: '10:35',
          sender: 'me'
        }
      ]
    }
  },
  methods: {
    sendMessage() {
      if (!this.newMessage.trim()) return
      
      this.messages.push({
        content: this.newMessage,
        time: '刚刚',
        sender: 'me'
      })
      
      this.newMessage = ''
      
      // 模拟回复
      setTimeout(() => {
        this.messages.push({
          content: '那好吧，4200我要了',
          time: '刚刚',
          sender: 'other'
        })
        
        // 滚动到底部
        this.$nextTick(() => {
          const container = this.$el.querySelector('.chat-messages')
          container.scrollTop = container.scrollHeight
        })
      }, 1000)
      
      // 滚动到底部
      this.$nextTick(() => {
        const container = this.$el.querySelector('.chat-messages')
        container.scrollTop = container.scrollHeight
      })
    }
  },
  mounted() {
    // 滚动到底部
    this.$nextTick(() => {
      const container = this.$el.querySelector('.chat-messages')
      container.scrollTop = container.scrollHeight
    })
  }
}
</script>

<style scoped>
.chat-header {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 20px;
}

.back-btn {
  color: var(--text);
  font-size: 1.2rem;
  margin-right: 15px;
  text-decoration: none;
}

.avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
}

.user-info {
  flex: 1;
}

.username {
  font-weight: 600;
  margin-bottom: 3px;
}

.status {
  color: var(--text-light);
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  background: none;
  border: none;
  color: var(--text);
  font-size: 1.2rem;
  cursor: pointer;
}

.chat-container {
  padding: 0;
  margin-bottom: 20px;
}

.chat-messages {
  height: 60vh;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.message {
  display: flex;
  margin-bottom: 20px;
  max-width: 80%;
}

.message.sent {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.received {
  align-self: flex-start;
}

.message .avatar {
  width: 35px;
  height: 35px;
  margin: 0 10px;
  align-self: flex-end;
}

.message-content {
  max-width: 100%;
}

.message.sent .message-content {
  background-color: var(--primary);
  color: white;
  border-radius: 18px 18px 0 18px;
}

.message.received .message-content {
  background-color: var(--secondary);
  border-radius: 18px 18px 18px 0;
}

.message-text {
  padding: 10px 15px;
  word-break: break-word;
}

.message-time {
  font-size: 0.7rem;
  color: var(--text-light);
  padding: 5px 15px 8px;
  text-align: right;
}

.message.received .message-time {
  text-align: left;
}

.chat-input {
  display: flex;
  padding: 15px;
  border-top: 1px solid var(--border);
  align-items: center;
}

.input-btn {
  background: none;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
  color: var(--text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.input-btn.send-btn:not(:disabled) {
  color: var(--primary);
}

.chat-input input {
  flex: 1;
  padding: 10px 15px;
  border-radius: 20px;
  border: 1px solid var(--border);
  font-size: 1rem;
  margin: 0 10px;
}

.product-info {
  padding: 15px;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.product-header a {
  color: var(--primary);
  text-decoration: none;
  font-size: 0.9rem;
}

.product-details {
  display: flex;
  align-items: center;
}

.product-image {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 15px;
}

.product-title {
  font-weight: 500;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  color: var(--danger);
  font-weight: bold;
}
</style>