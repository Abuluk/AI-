<template>
  <div class="messages-page">
    <div class="header">
      <h2><i class="fas fa-comments"></i> 消息中心</h2>
    </div>
    <div class="tabs">
      <button :class="{active: activeTab === 'all'}" @click="activeTab = 'all'">消息</button>
      <button :class="{active: activeTab === 'comment'}" @click="activeTab = 'comment'">评论互动</button>
      <button :class="{active: activeTab === 'like'}" @click="activeTab = 'like'">点赞消息</button>
    </div>
    <div v-if="activeTab === 'all'">
      <!-- 系统通知 -->
      <div class="system-notifications card">
        <div class="card-header">
          <h3><i class="fas fa-bullhorn"></i> 系统通知</h3>
          <button class="feedback-btn" @click="showFeedbackModal = true">意见反馈</button>
          <router-link to="/system-messages" class="see-all">查看全部</router-link>
        </div>
        <div v-if="loading.system" class="loading-state">
          <div class="skeleton-row small"></div>
        </div>
        <ul v-else-if="systemMessages.length > 0" class="notification-list">
          <li v-for="msg in systemMessages.slice(0, 3)" :key="msg.id">
            <router-link :to="`/system-messages/${msg.id}`" class="notification-link">
              <span class="notification-title">{{ msg.title || '系统消息' }}</span>
              <span class="notification-content">{{ msg.content }}</span>
              <span class="notification-time">{{ formatDateTime(msg.created_at) }}</span>
            </router-link>
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
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="filter-tabs">
              <button 
                v-for="tab in tabs" 
                :key="tab.id"
                :class="{ active: conversationFilter === tab.id }"
                @click="conversationFilter = tab.id"
              >
                {{ tab.label }}
              </button>
              <button 
                :class="{ active: false, 'all-read-btn': true }"
                @click="markAllAsRead"
              >全部已读</button>
            </div>
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
                <span class="item-title">
                  {{ conv.other_user_name }}
                  <span v-if="conv.type === 'item' && conv.item_title" style="margin-left: 16px; color: #888; font-size: 0.98em;">（{{ conv.item_title }}）</span>
                  <span v-else-if="conv.type === 'buy_request' && conv.buy_request_title" style="margin-left: 16px; color: #888; font-size: 0.98em;">（{{ conv.buy_request_title }}）</span>
                </span>
                <span class="time">{{ formatDateTime(conv.last_message_time) }}</span>
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
    <div v-else-if="activeTab === 'comment'">
      <div class="comment-interaction card comment-scroll-area">
        <h3><i class="fas fa-comment-dots"></i> 评论互动</h3>
        <div v-if="loading.comment" class="loading-state">加载中...</div>
        <ul v-else-if="commentList.length > 0" class="comment-list">
          <li v-for="c in commentList" :key="c.id" class="comment-item">
            <span class="user">{{ c.user_name }}</span>
            <span v-if="c.reply_to_user_name" class="at-highlight">@{{ c.reply_to_user_name }}</span>
            <span class="content">{{ c.content }}</span>
            <span class="time">{{ formatDateTime(c.created_at) }}</span>
            <button class="like-btn" :class="{ liked: c.liked_by_me }" @click="handleLike(c)">
              👍 {{ c.like_count || 0 }}
            </button>
          </li>
        </ul>
        <div v-else class="empty-state">暂无评论</div>
      </div>
    </div>
    <div v-else-if="activeTab === 'like'">
      <div class="like-messages card">
        <h3><i class="fas fa-thumbs-up"></i> 点赞消息</h3>
        <div v-if="loading.like" class="loading-state">加载中...</div>
        <ul v-else-if="likeMessages.length > 0" class="like-message-list">
          <li v-for="msg in likeMessages" :key="msg.id" class="like-message-item">
            <span class="like-title">{{ msg.title }}</span>
            <span class="like-content">{{ msg.content }}</span>
            <span class="like-time">{{ formatDateTime(msg.created_at) }}</span>
          </li>
        </ul>
        <div v-else class="empty-state">暂无点赞消息</div>
      </div>
    </div>
    <!-- 意见反馈弹窗 -->
    <div v-if="showFeedbackModal" class="modal-overlay" @click.self="showFeedbackModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>意见反馈</h3>
          <button class="close-btn" @click="showFeedbackModal = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <textarea v-model="feedbackContent" placeholder="请输入您的意见或建议..." rows="5" class="form-textarea"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="showFeedbackModal = false">取消</button>
          <button class="btn btn-primary" :disabled="feedbackLoading || !feedbackContent.trim()" @click="submitFeedback">
            {{ feedbackLoading ? '提交中...' : '提交反馈' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';

const router = useRouter();
const authStore = useAuthStore();

// Data
const systemMessages = ref([]);
const conversations = ref([]);
const commentList = ref([]);
const commentTree = ref([]);
const commentTargets = ref([]);
const selectedTarget = ref(null);
const expandedComments = ref({});
const loading = ref({ system: false, conversations: false, comment: false, like: false });
const activeTab = ref('all');
const conversationFilter = ref('all');
const tabs = [
  { id: 'all', label: '全部' },
  { id: 'unread', label: '未读' },
];
const allCommentTrees = ref([]);
const likeLoading = ref({});
const likeMessages = ref([]);
const showFeedbackModal = ref(false)
const feedbackContent = ref('')
const feedbackLoading = ref(false)

// Computed
const filteredConversations = computed(() => {
  if (conversationFilter.value === 'unread') {
    return conversations.value.filter(c => c.unread_count > 0);
  }
  return conversations.value;
});

function buildCommentTree(flatList) {
  const map = {};
  flatList.forEach(c => { map[c.id] = { ...c, children: [] }; });
  const roots = [];
  flatList.forEach(c => {
    if (c.parent_id && map[c.parent_id]) {
      map[c.parent_id].children.push(map[c.id]);
    } else if (!c.parent_id) {
      roots.push(map[c.id]);
    }
  });
  return roots;
}

const rootComments = computed(() => {
  return commentTree.value;
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

const fetchMyRelatedComments = async () => {
  loading.value.comment = true;
  try {
    const res = await api.getMyRelatedComments();
    const myId = authStore.user?.id;
    // 只保留不是我自己发的评论
    commentList.value = (res.data || []).filter(c => c.user_id !== myId);
  } catch (e) {
    commentList.value = [];
  } finally {
    loading.value.comment = false;
  }
};

const formatDateTime = (datetime) => {
  if (!datetime) return '未知';
  const date = new Date(datetime);
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  const h = String(date.getHours()).padStart(2, '0');
  const min = String(date.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${d} ${h}:${min}`;
};

const getUserAvatar = (avatar) => {
  if (!avatar || avatar.includes('default')) {
    return '/vite.svg'; // 默认头像
  }
  // 确保路径正确
  if (avatar.startsWith('http')) {
      return avatar;
  }
  return `http://8.138.47.159:8000/static/images/${avatar.replace(/^static[\\/]images[\\/]/, '')}`;
};

const selectConversation = (conv) => {
  // 判断类型，优先用 conv.type，否则根据 id 字段推断
  let type = conv.type;
  let id;
  if (type === 'user') {
    // 用户私聊，id用other_user_id
    id = conv.other_user_id;
  } else if (type === 'buy_request') {
    id = conv.buy_request_id;
  } else {
    id = conv.item_id;
  }
  
  // 触发全局未读消息计数更新
  window.dispatchEvent(new CustomEvent('updateUnreadCount'));
  
  router.push({ 
    name: 'Chat', 
    params: { 
      id, 
      other_user_id: conv.other_user_id,
      type
    } 
  });
};

const toggleExpand = (id) => {
  expandedComments.value[id] = !expandedComments.value[id];
};

const handleLike = async (comment) => {
  if (likeLoading.value[comment.id]) return;
  likeLoading.value[comment.id] = true;
  try {
    if (!comment.liked_by_me) {
      const res = await api.likeComment(comment.id);
      comment.like_count = res.data.like_count;
      comment.liked_by_me = true;
    } else {
      const res = await api.unlikeComment(comment.id);
      comment.like_count = res.data.like_count;
      comment.liked_by_me = false;
    }
  } catch (e) {}
  likeLoading.value[comment.id] = false;
};

const fetchLikeMessages = async () => {
  loading.value.like = true;
  try {
    const res = await api.getLikeMessages();
    // 只保留三类点赞消息
    likeMessages.value = (res.data || []).filter(
      m => ["商品被点赞", "求购被点赞", "评论被点赞"].includes(m.title)
    );
  } catch (e) {
    likeMessages.value = [];
  } finally {
    loading.value.like = false;
  }
};

const submitFeedback = async () => {
  if (!feedbackContent.value.trim()) return
  feedbackLoading.value = true
  try {
    await api.createFeedback(feedbackContent.value)
    alert('反馈提交成功，感谢您的宝贵意见！')
    showFeedbackModal.value = false
    feedbackContent.value = ''
  } catch (e) {
    alert('反馈提交失败，请稍后重试')
  } finally {
    feedbackLoading.value = false
  }
}

const markAllAsRead = async () => {
  try {
    await api.markAllMessagesAsRead();
    await fetchConversations();
    window.dispatchEvent(new CustomEvent('updateUnreadCount'));
    alert('全部消息已标记为已读！');
  } catch (e) {
    alert('操作失败，请稍后重试');
  }
}

// Lifecycle
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  fetchSystemMessages();
  fetchConversations();
  fetchMyRelatedComments();
  if (activeTab.value === 'like') fetchLikeMessages();
});

watch(activeTab, async (tab) => {
  if (tab === 'like') {
    // 先标记所有点赞消息为已读
    try {
      await api.markLikeMessagesAsRead();
      // 触发全局未读消息计数更新
      window.dispatchEvent(new CustomEvent('updateUnreadCount'));
    } catch (error) {
      console.warn('标记点赞消息为已读失败:', error);
    }
    // 然后获取点赞消息列表
    fetchLikeMessages();
  } else if (tab === 'comment') {
    fetchMyRelatedComments();
  }
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

.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
}
.tabs button {
  background: none;
  border: none;
  font-size: 1.1em;
  color: #888;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.tabs button.active {
  background: #007bff;
  color: #fff;
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
  max-height: 180px;
  overflow-y: auto;
  padding-right: 6px;
}

.notification-link {
  display: flex;
  flex-direction: column;
  padding: 12px 20px;
  border-bottom: 1px solid #f5f5f5;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}
.notification-link:hover {
  background: #f7faff;
}

.notification-title {
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 2px;
}

.notification-content {
  font-size: 0.98em;
  color: #555;
  margin-bottom: 2px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  max-width: 100%;
}

.notification-time {
  font-size: 0.85em;
  color: #999;
  align-self: flex-end;
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
  background: #fff;
  border-radius: 8px;
  margin-bottom: 10px;
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
  padding: 18px 0;
  color: #aaa;
  font-size: 0.98em;
  text-align: center;
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

.comment-interaction.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
  overflow: hidden;
  padding: 20px;
}
.comment-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 350px;
  overflow-y: auto;
}
.comment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 1em;
}
.comment-item .user {
  color: #1976d2;
  font-weight: 600;
}
.comment-item .content {
  flex: 1;
  color: #333;
}
.comment-item .time {
  color: #999;
  font-size: 0.95em;
  margin-left: 10px;
}
.at-highlight {
  color: #e67e22;
  font-weight: bold;
  margin: 0 2px;
}
.expand-btn {
  margin-left: 10px;
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.95em;
}
.child-comment-list {
  list-style: none;
  padding-left: 32px;
  margin: 6px 0 0 0;
}
.child-comment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.98em;
}
.child-comment-item .user {
  color: #1976d2;
  font-weight: 600;
}
.child-comment-item .content {
  color: #333;
}
.child-comment-item .time {
  color: #999;
  font-size: 0.92em;
  margin-left: 8px;
}
.comment-target-select {
  margin-bottom: 12px;
  font-size: 1em;
}
.comment-target-select select {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.comment-scroll-area {
  max-height: 500px;
  overflow-y: auto;
}
.comment-tree-block {
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}
.tree-title {
  font-weight: bold;
  color: #1976d2;
  margin-bottom: 8px;
}
.like-btn {
  margin-left: 10px;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 1em;
  transition: color 0.2s;
}
.like-btn.liked {
  color: #e67e22;
  font-weight: bold;
}
.comment-scroll {
  max-height: 180px;
  overflow-y: auto;
  border-top: 1px solid #f0f0f0;
  margin-top: 8px;
  padding-top: 8px;
}
.like-messages.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
  overflow: hidden;
  padding: 20px;
}
.like-message-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 350px;
  overflow-y: auto;
}
.like-message-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 1em;
}
.like-title {
  color: #e67e22;
  font-weight: 600;
  margin-right: 8px;
}
.like-content {
  flex: 1;
  color: #333;
}
.like-time {
  color: #999;
  font-size: 0.95em;
  margin-left: 10px;
}
.feedback-btn {
  margin-right: 16px;
  background: #fff;
  border: 1px solid #3498db;
  color: #3498db;
  border-radius: 6px;
  padding: 6px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.feedback-btn:hover {
  background: #eaf6fd;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  overflow: hidden;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}
.modal-body {
  padding: 20px;
}
.form-textarea {
  width: 100%;
  border-radius: 6px;
  border: 1px solid #ddd;
  padding: 10px;
  font-size: 15px;
  resize: vertical;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}
.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.close-btn:hover {
  color: #333;
}
.all-read-btn {
  background: none;
  border: 1.5px solid #27ae60;
  color: #27ae60;
  border-radius: 20px;
  padding: 6px 22px;
  font-size: 15px;
  margin-left: 8px;
  transition: background 0.2s, color 0.2s, border 0.2s;
  cursor: pointer;
}
.all-read-btn:hover {
  background: #eafaf1;
  color: #219150;
  border-color: #219150;
}
</style>