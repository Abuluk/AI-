<template>
  <div class="container">
    <div class="chat-header card">
      <router-link to="/messages" class="back-btn">
        <i class="fas fa-arrow-left"></i>
      </router-link>
      <div class="product-info-header">
        <img :src="getItemImage(item?.images)" class="product-avatar" v-if="chatType === 'item'">
        <img :src="'/static/images/default_avatar.png'" class="product-avatar" v-else>
        <div class="product-info">
          <div class="product-title">
            {{ chatType === 'item' ? (item?.title || '加载中...') : (item?.title || '加载中...') }}
          </div>
          <div class="product-price">
            <template v-if="chatType === 'item'">¥{{ item?.price || 0 }}</template>
            <template v-else>预算：¥{{ item?.budget || 0 }}</template>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <router-link v-if="chatType === 'item'" :to="`/item/${itemId}`" class="action-btn" title="查看商品">
          <i class="fas fa-external-link-alt"></i>
        </router-link>
        <router-link v-else :to="`/buy-request/${itemId}`" class="action-btn" title="查看求购">
          <i class="fas fa-external-link-alt"></i>
        </router-link>
      </div>
    </div>
    
    <div class="chat-container card">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载消息中...</p>
      </div>
      
      <div v-else class="chat-messages" ref="messagesContainer">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message"
          :class="{
            'sent': message.user_id === currentUserId,
            'received': message.user_id !== currentUserId,
            'system': message.is_system
          }"
        >
          <div v-if="!message.is_system" class="message-avatar">
            <img :src="getUserAvatar(message.user_id)" class="avatar" @error="handleAvatarError">
          </div>
          <div class="message-content">
            <div v-if="message.is_system" class="system-message">
              <i class="fas fa-bullhorn"></i>
              <span>{{ message.title || '系统消息' }}</span>
            </div>
            <div v-else-if="isImageMessage(message.content)" class="message-image">
              <img :src="getImageUrl(message.content)" style="max-width:180px;max-height:180px;border-radius:8px;" />
            </div>
            <div v-else-if="isLizhiEmoji(message.content) || isOnlyEmoji(message.content)" class="message-lizhi">
              <template v-for="part in parseLizhiContent(message.content)" :key="part.key">
                <img v-if="part.type === 'lizhi'" :src="lizhiUrl" alt="荔枝" style="width:32px;vertical-align:middle;" />
                <span v-else>{{ part.text }}</span>
              </template>
            </div>
            <div v-else class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatDateTime(message.created_at) }}</div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <i class="fas fa-comments"></i>
          <p>暂无消息，开始对话吧！</p>
        </div>
      </div>
      
      <div class="chat-input">
        <button class="input-btn" @click="showEmojiPicker = !showEmojiPicker">
          <i class="fas fa-smile"></i>
        </button>
        <button class="input-btn" @click="triggerImageUpload">
          <i class="fas fa-image"></i>
        </button>
        <input type="file" ref="imageInput" accept="image/*" style="display:none" @change="handleImageChange">
        <img v-if="imagePreview" :src="imagePreview" class="preview-image" />
        <input 
          type="text" 
          v-model="newMessage" 
          placeholder="输入消息..." 
          @keyup.enter="sendMessage"
          :disabled="!canSendMessage"
        >
        <button 
          class="input-btn send-btn"
          :disabled="!canSendMessage || (!newMessage.trim() && !imageFile)"
          @click="sendMessage"
        >
          <i class="fas fa-paper-plane"></i>
        </button>
        <div v-if="showEmojiPicker" class="emoji-picker">
          <span v-for="emoji in emojiList" :key="emoji" class="emoji-item" @click="insertEmoji(emoji)">{{ emoji }}</span>
          <img :src="lizhiUrl" alt="荔枝" class="emoji-item" style="width:28px;vertical-align:middle;cursor:pointer" @click="insertEmoji('[[lizhi]]')">
        </div>
      </div>
    </div>
    <button @click="handleDeleteConversation" class="delete-btn">删除对话</button>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

export default {
  props: {
    id: {
      type: [String, Number],
      required: true
    },
    other_user_id: {
      type: [String, Number],
      required: true
    },
    type: {
      type: String,
      required: false
    }
  },
  setup(props) {
    const router = useRouter()
    const authStore = useAuthStore()
    const route = useRoute()

    const chatType = computed(() => props.type || route.params.type || 'item')
    const itemId = computed(() => props.id)
    const otherUserId = computed(() => props.other_user_id)
    const currentUserId = computed(() => authStore.user?.id)

    const messages = ref([])
    const item = ref(null)
    const usersInfo = ref({})
    const newMessage = ref('')
    const loading = ref(false)
    const sending = ref(false)
    const messagesContainer = ref(null)
    const showEmojiPicker = ref(false)
    const imageInput = ref(null)
    const imageFile = ref(null)
    const imagePreview = ref('')
    const emojiList = [
      '😀','😂','😍','😎','😭','😡','👍','🎉','❤️','🥳','🤔','😅','😏','😳','😱','😴','😇','😜','😋','😢'
    ]
    
    const canSendMessage = computed(() => {
      return authStore.isAuthenticated && item.value && !sending.value
    })
    
    // 统一图片URL处理
    const resolveUrl = (path) => {
      if (!path) {
        path = '/static/images/default_avatar.png';
      }
      if (path.startsWith('http')) {
        return path;
      }
      const baseUrl = 'http://localhost:8000';
      const cleanedPath = path.startsWith('/') ? path.substring(1) : path;
      return `${baseUrl}/${cleanedPath.replace(/\\/g, '/')}`;
    }

    // 获取商品或求购信息
    const loadItem = async () => {
      try {
        if (chatType.value === 'buy_request') {
          const response = await api.getBuyRequest(itemId.value)
          item.value = response.data
        } else {
          const response = await api.getItem(itemId.value)
          item.value = response.data
        }
      } catch (error) {
        console.error('加载信息失败:', error)
        alert(chatType.value === 'buy_request' ? '求购信息不存在或已被删除' : '商品不存在或已被删除')
        router.push('/messages')
      }
    }

    // 获取对话双方用户信息
    const loadUsersInfo = async () => {
      const userIds = [currentUserId.value, otherUserId.value].filter(id => id);
      if (userIds.length > 0) {
        try {
          const res = await api.getUsersByIds(userIds);
          res.data.forEach(user => {
            usersInfo.value[user.id] = user;
          });
        } catch (e) {
          console.error('获取用户信息失败', e);
        }
      }
    }
    
    const loadMessages = async () => {
      if (!authStore.isAuthenticated) {
        router.push('/login')
        return
      }
      loading.value = true
      try {
        const response = await api.getConversationMessages({ type: chatType.value, id: itemId.value, other_user_id: otherUserId.value })
        messages.value = response.data
        scrollToBottom()
      } catch (error) {
        console.error('加载消息失败:', error)
        messages.value = []
      } finally {
        loading.value = false
      }
    }
    
    const triggerImageUpload = () => {
      imageInput.value && imageInput.value.click()
    }
    const handleImageChange = (e) => {
      const file = e.target.files[0]
      if (file) {
        imageFile.value = file
        imagePreview.value = URL.createObjectURL(file)
      }
    }
    const insertEmoji = (emoji) => {
      if (emoji === '[[lizhi]]') {
        newMessage.value += '[[lizhi]]'
      } else {
        newMessage.value += emoji
      }
      showEmojiPicker.value = false
    }
    const isImageMessage = (content) => {
      return typeof content === 'string' && (
        content.startsWith('/static/images/') ||
        (content.startsWith('http') && (
          content.endsWith('.jpg') || content.endsWith('.png') || content.endsWith('.jpeg') || content.endsWith('.gif')))
      )
    }
    const isLizhiEmoji = (content) => {
      return typeof content === 'string' && content.includes('[[lizhi]]')
    }
    const isOnlyEmoji = (content) => {
      // 只包含emoji或空格
      return typeof content === 'string' && /^[\p{Emoji}\s]+$/u.test(content)
    }
    const sendMessage = async () => {
      if ((!newMessage.value.trim() && !imageFile.value) || !canSendMessage.value) return
      let messageContent = newMessage.value.trim()
      if (imageFile.value) {
        const formData = new FormData()
        formData.append('file', imageFile.value)
        const res = await api.uploadChatImage(formData)
        messageContent = res.data.url
        imageFile.value = null
        imagePreview.value = ''
        imageInput.value.value = ''
      }
      newMessage.value = ''
      sending.value = true
      try {
        const response = await api.sendMessage({
          content: messageContent,
          other_user_id: otherUserId.value,
          type: chatType.value,
          id: itemId.value
        })
        messages.value.push(response.data)
        scrollToBottom()
      } catch (error) {
        console.error('发送消息失败:', error)
        alert('发送失败，请重试')
        newMessage.value = messageContent
      } finally {
        sending.value = false
      }
    }
    
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    const formatDateTime = (timestamp) => {
      const date = new Date(timestamp)
      const y = date.getFullYear();
      const m = String(date.getMonth() + 1).padStart(2, '0');
      const d = String(date.getDate()).padStart(2, '0');
      const h = String(date.getHours()).padStart(2, '0');
      const min = String(date.getMinutes()).padStart(2, '0');
      return `${y}-${m}-${d} ${h}:${min}`;
    }
    
    const getItemImage = (images) => {
      if (!images) return '';
      return resolveUrl(images.split(',')[0]);
    }
    
    const getUserAvatar = (userId) => {
      const user = usersInfo.value[userId];
      console.log('getUserAvatar user:', user); // 调试用
      if (user && user.avatar) {
        return resolveUrl(user.avatar);
      }
      // 如果没有头像，返回默认头像
      return resolveUrl('/static/images/default_avatar.png');
    }
    
    const handleAvatarError = (event) => {
      if (event.target.src.endsWith('/static/images/default_avatar.png')) {
        event.target.onerror = null;
        return;
      }
      event.target.onerror = null;
      event.target.src = 'http://localhost:8000/static/images/default_avatar.png';
    }
    
    const handleDeleteConversation = async () => {
      if (confirm('确定要删除该对话吗？此操作不可恢复！')) {
        try {
          await api.deleteConversation({ type: chatType.value, id: itemId.value, other_user_id: otherUserId.value })
          alert('对话已删除')
          router.push('/messages')
        } catch (e) {
          alert('删除失败，请重试')
        }
      }
    }
    
    const lizhiUrl = window.location.origin + '/static/images/lizhi.png'
    
    const getImageUrl = (content) => {
      if (content.startsWith('/static/')) {
        return window.location.origin + content
      }
      return content
    }
    
    const parseLizhiContent = (content) => {
      // 将内容按[[lizhi]]分割，保留顺序，支持emoji
      const parts = []
      let idx = 0
      const arr = content.split('[[lizhi]]')
      arr.forEach((txt, i) => {
        if (txt) {
          // 拆分emoji和文本，逐字符处理
          for (const char of Array.from(txt)) {
            // 判断是否emoji（利用unicode范围）
            if (/\p{Emoji}/u.test(char)) {
              parts.push({ type: 'text', text: char, key: idx++ })
            } else {
              parts.push({ type: 'text', text: char, key: idx++ })
            }
          }
        }
        if (i < arr.length - 1) parts.push({ type: 'lizhi', key: idx++ })
      })
      return parts
    }
    
    onMounted(async () => {
      await loadItem();
      await loadUsersInfo();
      loadMessages();
    })
    
    // 监听消息变化，自动滚动到底部
    watch(messages, () => {
      scrollToBottom()
    }, { deep: true })
    
    return {
      itemId,
      otherUserId,
      currentUserId,
      messages,
      item,
      newMessage,
      loading,
      sending,
      messagesContainer,
      showEmojiPicker,
      canSendMessage,
      sendMessage,
      formatDateTime,
      getItemImage,
      getUserAvatar,
      handleAvatarError,
      usersInfo,
      handleDeleteConversation,
      chatType,
      imageInput,
      imageFile,
      imagePreview,
      emojiList,
      triggerImageUpload,
      handleImageChange,
      insertEmoji,
      isImageMessage,
      isLizhiEmoji,
      isOnlyEmoji,
      lizhiUrl,
      getImageUrl,
      parseLizhiContent
    }
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
  background-color: #fff !important;
  color: #333;
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
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  color: var(--danger);
  font-weight: bold;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-state i {
  font-size: 2rem;
  color: var(--text-light);
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-light);
  font-size: 1rem;
}

.product-info-header {
  display: flex;
  align-items: center;
  flex: 1;
}

.product-avatar {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 15px;
}

.product-info {
  flex: 1;
}

.product-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text);
  margin-bottom: 4px;
}

.product-price {
  color: var(--primary);
  font-weight: 600;
  font-size: 0.9rem;
}

.message-avatar {
  margin-right: 10px;
}

.message-avatar .avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  object-fit: cover;
}

.system-message {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.system-message i {
  font-size: 0.8rem;
}

.message.sent {
  flex-direction: row-reverse;
}

.message.sent .message-avatar {
  margin-right: 0;
  margin-left: 10px;
}

.message.sent .message-content {
  align-items: flex-end;
}

.message.sent .message-text {
  background: var(--primary);
  color: white;
}

.message.sent .message-time {
  text-align: right;
}

.message.system {
  justify-content: center;
  margin: 20px 0;
}

.message.system .message-content {
  max-width: 80%;
  text-align: center;
}

.delete-btn {
  background: none;
  border: none;
  color: var(--danger);
  font-size: 1rem;
  cursor: pointer;
  padding: 10px;
  margin-top: 10px;
}

.preview-image {
  max-width: 80px;
  max-height: 80px;
  border-radius: 8px;
  margin: 0 8px;
  vertical-align: middle;
}

.emoji-picker {
  position: absolute;
  bottom: 60px;
  left: 20px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 8px 12px;
  z-index: 10;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.emoji-item {
  font-size: 22px;
  cursor: pointer;
  margin: 2px;
}
</style>