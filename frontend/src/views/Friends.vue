<template>
  <div class="friends-page container">
    <div class="page-title"><i class="fas fa-user-friends"></i> 好友管理</div>
    <div class="friends-tabs">
      <button :class="{active: activeTab === 'friends'}" @click="activeTab = 'friends'">我的好友</button>
      <button :class="{active: activeTab === 'blacklist'}" @click="activeTab = 'blacklist'">黑名单</button>
    </div>
    <div v-if="activeTab === 'friends'">
      <div class="section-header">
        <div class="search-box">
          <input v-model="searchKeyword" @input="searchUsers" placeholder="搜索用户..." class="search-input">
          <i class="fas fa-search"></i>
        </div>
      </div>
      <div v-if="showSearchResults && searchResults.length > 0" class="search-results">
        <h4>搜索结果</h4>
        <div class="users-list">
          <div v-for="user in searchResults" :key="user.id" class="user-card">
            <img :src="getUserAvatar(user.avatar)" :alt="user.username" class="user-avatar" @click="goToUserProfile(user.id)" style="cursor: pointer;">
            <div class="user-info">
              <h5 @click="goToUserProfile(user.id)" style="cursor: pointer;">{{ user.username }}</h5>
              <p v-if="user.bio">{{ user.bio }}</p>
            </div>
            <div class="user-actions">
              <button v-if="!isFriend(user.id) && !isBlacklisted(user.id)" @click="addFriend(user.id)" class="btn btn-primary btn-sm">添加好友</button>
              <button v-if="!isBlacklisted(user.id)" @click="addToBlacklist(user.id)" class="btn btn-outline btn-sm">拉黑</button>
              <span v-if="isFriend(user.id)" class="status-badge">已是好友</span>
              <span v-if="isBlacklisted(user.id)" class="status-badge blacklisted">已拉黑</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="friendsList.length === 0" class="empty-state">
        <i class="fas fa-user-friends"></i>
        <p>暂无好友</p>
        <p class="hint">搜索用户并添加好友</p>
      </div>
      <div v-else class="users-list">
        <div v-for="friend in friendsList" :key="friend.id" class="user-card" @click="goToChat(friend.id)" style="cursor:pointer;">
          <img :src="getUserAvatar(friend.avatar)" :alt="friend.username" class="user-avatar" @click.stop="goToUserProfile(friend.id)" style="cursor: pointer;">
          <div class="user-info">
            <h5 @click.stop="goToUserProfile(friend.id)" style="cursor: pointer;">{{ friend.username }}</h5>
            <p v-if="friend.bio">{{ friend.bio }}</p>
          </div>
          <div class="user-actions" @click.stop>
            <button @click="removeFriend(friend.id)" class="btn btn-outline btn-sm">删除好友</button>
            <button @click="addToBlacklist(friend.id)" class="btn btn-outline btn-sm">拉黑</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="activeTab === 'blacklist'">
      <div class="section-header"><h3>黑名单</h3></div>
      <div v-if="blacklist.length === 0" class="empty-state">
        <i class="fas fa-ban"></i>
        <p>黑名单为空</p>
      </div>
      <div v-else class="users-list">
        <div v-for="user in blacklist" :key="user.id" class="user-card">
          <img :src="getUserAvatar(user.avatar)" :alt="user.username" class="user-avatar" @click="goToUserProfile(user.id)" style="cursor: pointer;">
          <div class="user-info">
            <h5 @click="goToUserProfile(user.id)" style="cursor: pointer;">{{ user.username }}</h5>
            <p v-if="user.bio">{{ user.bio }}</p>
          </div>
          <div class="user-actions">
            <button @click="removeFromBlacklist(user.id)" class="btn btn-primary btn-sm">移出黑名单</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const activeTab = ref('friends')
const friendsList = ref([])
const blacklist = ref([])
const searchKeyword = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const router = useRouter()

const loadFriends = async () => {
  try {
    const response = await api.getFriendsList()
    friendsList.value = response.data || []
  } catch (error) {
    console.error('获取好友列表失败:', error)
  }
}

const loadBlacklist = async () => {
  try {
    const response = await api.getBlacklist()
    blacklist.value = response.data || []
  } catch (error) {
    console.error('获取黑名单失败:', error)
  }
}

const searchUsers = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  try {
    const response = await api.searchUsers(searchKeyword.value.trim())
    searchResults.value = response.data || []
    showSearchResults.value = true
  } catch (error) {
    console.error('搜索用户失败:', error)
    searchResults.value = []
  }
}

const addFriend = async (friendId) => {
  try {
    await api.addFriend(friendId)
    alert('添加好友成功')
    await loadFriends()
    searchResults.value = searchResults.value.filter(user => user.id !== friendId)
  } catch (error) {
    console.error('添加好友失败:', error)
    alert('添加好友失败')
  }
}

const removeFriend = async (friendId) => {
  if (!confirm('确定要删除该好友吗？')) return
  try {
    await api.removeFriend(friendId)
    alert('删除好友成功')
    await loadFriends()
  } catch (error) {
    console.error('删除好友失败:', error)
    alert('删除好友失败')
  }
}

const addToBlacklist = async (userId) => {
  try {
    await api.addToBlacklist(userId)
    alert('已添加到黑名单')
    await loadBlacklist()
    friendsList.value = friendsList.value.filter(friend => friend.id !== userId)
  } catch (error) {
    console.error('添加到黑名单失败:', error)
    alert('添加到黑名单失败')
  }
}

const removeFromBlacklist = async (userId) => {
  try {
    await api.removeFromBlacklist(userId)
    alert('已从黑名单移除')
    await loadBlacklist()
  } catch (error) {
    console.error('从黑名单移除失败:', error)
    alert('从黑名单移除失败')
  }
}

const isFriend = (userId) => {
  return friendsList.value.some(friend => friend.id === userId)
}

const isBlacklisted = (userId) => {
  return blacklist.value.some(user => user.id === userId)
}

const getUserAvatar = (avatar) => {
  if (!avatar || avatar.includes('default')) {
    return '/static/images/default_avatar.png'
  }
  if (avatar.startsWith('http')) {
    return avatar
  }
  return `http://8.138.47.159:8000/static/images/${avatar.replace(/^static[\\/]images[\\/]/, '')}`
}

const goToChat = (friendId) => {
  router.push({ name: 'Chat', params: { id: friendId, other_user_id: friendId, type: 'user' } })
}

const goToUserProfile = (userId) => {
  router.push({ name: 'UserProfile', params: { id: userId } })
}

onMounted(async () => {
  await loadFriends()
  await loadBlacklist()
})
</script>

<style scoped>
.friends-page {
  max-width: 700px;
  margin: 30px auto 0 auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 30px 24px 24px 24px;
}
.page-title {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.friends-tabs {
  display: flex;
  gap: 16px;
  margin-bottom: 18px;
}
.friends-tabs button {
  background: none;
  border: none;
  font-size: 1.1em;
  color: #888;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.friends-tabs button.active {
  background: #007bff;
  color: #fff;
}
.section-header {
  margin-bottom: 12px;
}
.search-box {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input {
  padding: 8px 12px 8px 35px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}
.search-box i {
  position: absolute;
  left: 12px;
  color: #999;
  font-size: 14px;
}
.search-results {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}
.search-results h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}
.users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  background: #f0f0f0;
}
.user-info {
  flex: 1;
  min-width: 0;
}
.user-info h5 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.user-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.user-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary {
  background: #007bff;
  color: white;
}
.btn-primary:hover {
  background: #0056b3;
}
.btn-outline {
  background: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}
.btn-outline:hover {
  background: #007bff;
  color: white;
}
.status-badge {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 12px;
  background: #e9ecef;
  color: #6c757d;
}
.status-badge.blacklisted {
  background: #f8d7da;
  color: #721c24;
}
.hint {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}
.empty-state {
  text-align: center;
  color: #999;
  margin: 32px 0 0 0;
}
.empty-state i {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #e0e0e0;
}
@media (max-width: 768px) {
  .friends-page {
    padding: 10px 2px;
  }
  .search-input {
    width: 120px;
  }
  .user-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .user-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style> 