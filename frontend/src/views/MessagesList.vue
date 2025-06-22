<template>
  <div class="messages-page">
    <div class="header">
      <h2><i class="fas fa-comments"></i> 消息中心</h2>
    </div>

    <!-- 系统通知 -->
    <div class="system-notifications card">
      <div class="card-header">
        <h3><i class="fas fa-bullhorn"></i> 系统通知</h3>
        <a href="#" class="see-all">查看全部</a>
      </div>
      <div v-if="loading.system" class="loading-state">
        <div class="skeleton-row small"></div>
      </div>
      <ul v-else-if="systemMessages.length > 0" class="notification-list">
        <li v-for="msg in systemMessages.slice(0, 3)" :key="msg.id">
          <span class="notification-title">{{ msg.title || '系统消息' }}</span>
          <span class="notification-content">{{ msg.content }}</span>
          <span class="notification-time">{{ formatTime(msg.created_at) }}</span>
        </li>
      </ul>
      <div v-else class="empty-state small">
        <p>暂无系统通知</p>
      </div>
    </div>

    <!-- 我的对话 -->
    <div class="conversations card">
      <div class="card-header">
        <h3><i class="fas fa-user-friends"></i> 我的对话</h3>
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
      </div>
      <div v-if="loading.conversations" class="loading-state">
        <div class="skeleton-row" v-for="n in 3" :key="n"></div>
      </div>
      <div v-else-if="filteredConversations.length > 0" class="conversations-list">
        <div 
          v-for="conv in filteredConversations" 
          :key="`${conv.item_id}-${conv.other_user_id}`"
          class="conversation-item"
          :class="{ unread: conv.unread_count > 0 }"
          @click="selectConversation(conv)"
        >
          <img :src="getUserAvatar(conv.other_user_avatar)" :alt="conv.other_user_name" class="item-image">
          <div class="conversation-content">
            <div class="conversation-header">
              <span class="item-title">{{ conv.other_user_name }}</span>
              <span class="time">{{ formatTime(conv.last_message_time) }}</span>
            </div>
            <p class="last-message">{{ conv.last_message_content }}</p>
          </div>
          <div v-if="conv.unread_count > 0" class="unread-dot"></div>
        </div>
      </div>
      <div v-else class="empty-state">
        <p>暂无对话</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

// Data
const systemMessages = ref([]);
const conversations = ref([]);
const loading = ref({ system: false, conversations: false });
const activeTab = ref('all');
const tabs = [
  { id: 'all', label: '全部' },
  { id: 'unread', label: '未读' },
];

// Computed
const filteredConversations = computed(() => {
  if (activeTab.value === 'unread') {
    return conversations.value.filter(c => c.unread_count > 0);
  }
  return conversations.value;
});

// Methods
const fetchSystemMessages = async () => {
  loading.value.system = true;
  try {
    const response = await api.getPublicSystemMessages();
    systemMessages.value = response.data;
  } catch (error) {
    console.error('获取系统通知失败:', error);
  } finally {
    loading.value.system = false;
  }
};

const fetchConversations = async () => {
  loading.value.conversations = true;
  try {
    const response = await api.getConversationsList();
    conversations.value = response.data;
  } catch (error) {
    console.error('加载对话列表失败:', error);
  } finally {
    loading.value.conversations = false;
  }
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return ''; //
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24 && date.getDate() === now.getDate()) return `${hours}小时前`;
  if (now.getDate() - date.getDate() === 1) return '昨天';
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
};

const getUserAvatar = (avatar) => {
  if (!avatar || avatar.includes('default')) {
    return '/vite.svg'; // 默认头像
  }
  // 确保路径正确
  if (avatar.startsWith('http')) {
      return avatar;
  }
  return `http://localhost:8000/static/images/${avatar.replace(/^static[\\/]images[\\/]/, '')}`;
};

const selectConversation = (conv) => {
  router.push({ 
    name: 'Chat', 
    params: { 
      id: conv.item_id, 
      other_user_id: conv.other_user_id 
    } 
  });
};

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  fetchSystemMessages();
  fetchConversations();
});
</script>

<style scoped>
.messages-page {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 15px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
}

.see-all {
  font-size: 13px;
  color: #007bff;
  text-decoration: none;
}

/* System Notifications */
.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notification-list li {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
  cursor: pointer;
}

.notification-list li:last-child {
  border-bottom: none;
}

.notification-list li:hover {
  background-color: #f9f9f9;
}

.notification-title {
  font-weight: 500;
  color: #007bff;
  margin-right: 15px;
  white-space: nowrap;
}

.notification-content {
  flex-grow: 1;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-time {
  font-size: 12px;
  color: #999;
  margin-left: 15px;
}

/* Conversations */
.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tabs button {
  background: none;
  border: 1px solid #ddd;
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tabs button.active {
  background-color: #007bff;
  color: #fff;
  border-color: #007bff;
}

.conversations-list {
  padding: 8px 0;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.conversation-item:hover {
  background-color: #f9f9f9;
}

.item-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
  margin-right: 15px;
  flex-shrink: 0;
}

.conversation-content {
  flex-grow: 1;
  overflow: hidden;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.item-title {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.time {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
  margin-left: 10px;
}

.last-message {
  font-size: 14px;
  color: #777;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.unread-dot {
  width: 10px;
  height: 10px;
  background-color: #007bff;
  border-radius: 50%;
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
}

.conversation-item.unread .item-title {
  font-weight: 700;
}
.conversation-item.unread .last-message {
  color: #333;
  font-weight: 500;
}

/* States */
.loading-state, .empty-state {
  padding: 30px 20px;
  text-align: center;
  color: #999;
}

.empty-state.small {
  padding: 20px;
}

.skeleton-row {
  height: 60px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-pulse 1.5s infinite;
  border-radius: 8px;
  margin: 10px;
}

.skeleton-row.small {
  height: 40px;
}

@keyframes skeleton-pulse {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>