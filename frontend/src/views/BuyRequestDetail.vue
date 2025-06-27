<template>
  <div class="container buy-request-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="buyRequest" class="detail-card">
      <div class="detail-main">
        <div class="detail-info">
          <h1 class="title">{{ buyRequest.title }}</h1>
          <div class="meta">
            <span class="budget">预算：¥{{ buyRequest.budget }}</span>
            <span class="user">
              <img v-if="buyRequest.user && buyRequest.user.avatar_url" :src="buyRequest.user.avatar_url" alt="头像" class="avatar">
              {{ buyRequest.user ? buyRequest.user.username : '未知用户' }}
            </span>
          </div>
          <div class="desc">{{ buyRequest.description }}</div>
          <div class="created">发布时间：{{ formatDateTime(buyRequest.created_at) }}</div>
        </div>
        <div class="detail-images" v-if="buyRequest.images && buyRequest.images.length">
          <img v-for="(img, idx) in buyRequest.images" :key="idx" :src="img" class="buy-request-image" />
        </div>
      </div>
      <div class="seller-info-card">
        <h3>发布者信息</h3>
        <div class="seller-card" v-if="publisher">
          <div class="seller-header">
            <img :src="publisher.avatar ? formatAvatar(publisher.avatar) : '/static/images/default_avatar.png'" class="seller-avatar" @error="handleAvatarError">
            <div class="seller-basic-info">
              <div class="seller-name">{{ publisher.username }}</div>
              <div class="seller-stats">
                <span class="stat-item">
                  <i class="fas fa-box"></i>
                  {{ publisher.items_count || 0 }} 件商品
                </span>
                <span class="stat-item">
                  <i class="fas fa-calendar-alt"></i>
                  {{ formatJoinDate(publisher.created_at) }} 加入
                </span>
              </div>
            </div>
            <button class="btn btn-outline" @click="startChat" :disabled="isSelf">
              <i class="fas fa-comment"></i> 联系发布者
            </button>
          </div>
          <div class="seller-details">
            <div v-if="publisher.bio" class="seller-bio">
              <h4>个人简介</h4>
              <p>{{ publisher.bio }}</p>
            </div>
            <div class="seller-contact-info">
              <div v-if="publisher.location" class="contact-item">
                <i class="fas fa-map-marker-alt"></i>
                <span>所在地：{{ publisher.location }}</span>
              </div>
              <div v-if="publisher.contact" class="contact-item">
                <i class="fas fa-envelope"></i>
                <span>联系方式：{{ publisher.contact }}</span>
              </div>
            </div>
            <div class="seller-activity">
              <div class="activity-item">
                <i class="fas fa-eye"></i>
                <span>最近活跃：{{ formatLastActive(publisher.last_login) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty">未找到该求购信息</div>
  </div>
</template>

<script>
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'
import { computed } from 'vue'

export default {
  name: 'BuyRequestDetail',
  data() {
    return {
      buyRequest: null,
      publisher: null,
      loading: true,
      error: null
    }
  },
  computed: {
    currentUser() {
      return useAuthStore().user;
    },
    isSelf() {
      return this.currentUser && this.publisher && this.currentUser.id === this.publisher.id;
    }
  },
  created() {
    this.fetchBuyRequest()
  },
  methods: {
    async fetchBuyRequest() {
      this.loading = true
      try {
        const id = this.$route.params.id
        const res = await api.getBuyRequest(id)
        this.buyRequest = res.data
        // 获取发布者详细信息
        if (this.buyRequest && this.buyRequest.user_id) {
          const userRes = await api.getUser(this.buyRequest.user_id)
          this.publisher = userRes.data
        }
      } catch (e) {
        this.error = '加载失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    formatDateTime(datetime) {
      if (!datetime) return '未知'
      const date = new Date(datetime)
      const y = date.getFullYear()
      const m = String(date.getMonth() + 1).padStart(2, '0')
      const d = String(date.getDate()).padStart(2, '0')
      const h = String(date.getHours()).padStart(2, '0')
      const min = String(date.getMinutes()).padStart(2, '0')
      return `${y}-${m}-${d} ${h}:${min}`
    },
    formatJoinDate(time) {
      if (!time) return '未知';
      return new Date(time).toLocaleDateString();
    },
    formatLastActive(time) {
      if (!time) return '未知';
      const lastLogin = new Date(time);
      const now = new Date();
      const diff = Math.floor((now - lastLogin) / (1000 * 60 * 60 * 24));
      if (diff === 0) return '今天';
      if (diff < 30) return `${diff}天前`;
      return '很久以前';
    },
    formatAvatar(avatar) {
      if (!avatar) return '/static/images/default_avatar.png';
      if (avatar.startsWith('/')) return avatar;
      return '/static/images/' + avatar.replace(/^.*[\\/]/, '');
    },
    handleAvatarError(event) {
      event.target.src = '/static/images/default_avatar.png';
      event.target.onerror = null;
    },
    startChat() {
      if (!this.publisher || this.isSelf) return;
      this.$router.push({ name: 'Chat', params: { id: this.buyRequest.id, other_user_id: this.publisher.id, type: 'buy_request' } })
    }
  }
}
</script>

<style scoped>
.buy-request-detail {
  max-width: 900px;
  margin: 40px auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 32px 24px;
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.detail-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-height: 60vh;
}
.detail-main {
  display: flex;
  flex-direction: row;
  gap: 40px;
  align-items: flex-start;
  min-height: 400px;
}
.detail-info {
  flex: 2;
  min-width: 0;
}
.detail-images {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-start;
  min-width: 400px;
}
.title {
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 8px;
}
.meta {
  display: flex;
  gap: 18px;
  align-items: center;
  color: #888;
}
.budget {
  color: #e74c3c;
  font-weight: bold;
}
.user {
  display: flex;
  align-items: center;
  gap: 6px;
}
.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}
.desc {
  font-size: 1.1rem;
  color: #333;
  margin: 12px 0;
}
.created {
  color: #aaa;
  font-size: 0.95rem;
}
.loading, .error, .empty {
  text-align: center;
  color: #888;
  margin: 40px 0;
}
.seller-info-card {
  width: 100%;
  background: #fafbfc;
  border-radius: 10px;
  padding: 32px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: stretch;
  margin-top: 0;
  min-height: 300px;
}
.seller-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.seller-header {
  display: flex;
  align-items: center;
  gap: 18px;
}
.seller-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
}
.seller-basic-info {
  flex: 1;
}
.seller-name {
  font-size: 1.2rem;
  font-weight: bold;
}
.seller-stats {
  display: flex;
  gap: 16px;
  color: #888;
  font-size: 0.98rem;
  margin-top: 4px;
}
.btn.btn-outline {
  border: 1px solid #3498db;
  color: #3498db;
  background: #fff;
  padding: 8px 18px;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
}
.btn.btn-outline:hover {
  background: #eaf6fd;
}
.seller-details {
  margin-top: 10px;
  padding-left: 82px;
}
.seller-bio {
  margin-bottom: 10px;
}
.seller-contact-info .contact-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #555;
  margin-bottom: 4px;
}
.seller-activity {
  margin-top: 8px;
  color: #888;
  font-size: 0.97rem;
}
.activity-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.buy-request-image {
  width: 400px;
  height: 400px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #eee;
  margin-bottom: 10px;
}
</style> 