<template>
  <div class="system-message-detail-container">
    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <p>正在加载...</p>
    </div>
    <div v-else-if="error" class="error-message">
      <p>加载失败：{{ error }}</p>
      <button @click="fetchMessage">重试</button>
    </div>
    <div v-else-if="message" class="message-card">
      <div class="message-header">
        <h1>{{ message.title }}</h1>
        <p class="meta">发布于 {{ formatTime(message.created_at) }}</p>
      </div>
      <div class="message-content" v-html="message.content"></div>
      <div class="back-button-container">
        <button @click="$router.back()" class="back-button">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/api';

const route = useRoute();
const message = ref(null);
const loading = ref(true);
const error = ref('');

const messageId = route.params.id;

const fetchMessage = async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await api.getSystemMessage(messageId);
    message.value = response.data;
    
    // 自动标记系统消息为已读
    try {
      await api.markSystemMessageAsRead(messageId);
      // 触发全局未读消息计数更新
      window.dispatchEvent(new CustomEvent('updateUnreadCount'));
    } catch (markError) {
      console.warn('标记系统消息为已读失败:', markError);
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '无法连接到服务器';
    console.error('获取系统消息失败:', err);
  } finally {
    loading.value = false;
  }
};

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(fetchMessage);
</script>

<style scoped>
.system-message-detail-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
.message-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  padding: 30px 40px;
}
.message-header {
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 25px;
  padding-bottom: 20px;
  text-align: center;
}
.message-header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 10px;
}
.message-header .meta {
  font-size: 0.9rem;
  color: #888;
}
.message-content {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #333;
}
.back-button-container {
  text-align: center;
  margin-top: 40px;
}
.back-button {
  padding: 10px 30px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}
.back-button:hover {
  background-color: #0056b3;
}
.loading-spinner, .error-message {
  text-align: center;
  padding: 50px;
  color: #888;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 