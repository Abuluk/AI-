<template>
  <div class="system-messages-all-container">
    <div class="header">
      <router-link to="/messages" class="back-link">&lt; 返回消息中心</router-link>
      <h1>所有系统通知</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="skeleton-item" v-for="n in 5" :key="n"></div>
    </div>
    <div v-else-if="error" class="error-state">
      <p>加载通知失败：{{ error }}</p>
      <button @click="fetchAllMessages">重试</button>
    </div>
    <ul v-else-if="messages.length > 0" class="messages-list">
      <li v-for="msg in messages" :key="msg.id">
        <router-link :to="`/system-messages/${msg.id}`" class="message-link">
          <div class="message-content">
            <span class="message-title">{{ msg.title }}</span>
            <p class="message-excerpt">{{ truncate(msg.content) }}</p>
          </div>
          <span class="message-time">{{ formatTime(msg.created_at) }}</span>
        </router-link>
      </li>
    </ul>
    <div v-else class="empty-state">
      <p>这里空空如也，一条系统通知都没有。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const messages = ref([]);
const loading = ref(true);
const error = ref('');

const fetchAllMessages = async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await api.getPublicSystemMessages();
    messages.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.detail || '无法连接到服务器';
    console.error('获取所有系统消息失败:', err);
  } finally {
    loading.value = false;
  }
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  return date.toLocaleDateString('zh-CN');
};

const truncate = (text, length = 100) => {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
};

onMounted(fetchAllMessages);
</script>

<style scoped>
.system-messages-all-container {
  max-width: 800px;
  margin: 30px auto;
  padding: 20px;
}
.header {
  margin-bottom: 30px;
}
.header h1 {
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
}
.back-link {
  color: #007bff;
  text-decoration: none;
  margin-bottom: 10px;
  display: inline-block;
}
.messages-list {
  list-style: none;
  padding: 0;
}
.message-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 15px;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}
.message-link:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.message-title {
  font-size: 1.1rem;
  font-weight: 600;
  display: block;
  margin-bottom: 8px;
}
.message-excerpt {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}
.message-time {
  font-size: 0.85rem;
  color: #999;
  white-space: nowrap;
  margin-left: 20px;
}
.loading-state, .error-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 8px;
  color: #888;
}
.skeleton-item {
  height: 95px;
  background: #f0f0f0;
  border-radius: 8px;
  margin-bottom: 15px;
  animation: pulse 1.5s infinite ease-in-out;
}
@keyframes pulse {
  0% { background-color: #f0f0f0; }
  50% { background-color: #e0e0e0; }
  100% { background-color: #f0f0f0; }
}
</style> 