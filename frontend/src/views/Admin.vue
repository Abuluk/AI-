<template>
  <div class="admin-container">
    <!-- 管理员头部 -->
    <div class="admin-header">
      <h1>管理员控制台</h1>
      <div class="admin-info">
        <span>欢迎，{{ user.username }}</span>
        <button class="btn btn-outline" @click="logout">
          <i class="fas fa-sign-out-alt"></i> 退出
        </button>
      </div>
    </div>

    <!-- 统计信息卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_users || 0 }}</h3>
          <p>总用户数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-box"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_items || 0 }}</h3>
          <p>总商品数</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.active_users || 0 }}</h3>
          <p>活跃用户</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-shopping-cart"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.online_items || 0 }}</h3>
          <p>在售商品</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.sold_items || 0 }}</h3>
          <p>已售商品</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-heart"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_favorites || 0 }}</h3>
          <p>总收藏数</p>
        </div>
      </div>
    </div>

    <!-- 标签页导航 -->
    <div class="admin-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="changeTab(tab.id)"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- 用户管理 -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="section-header">
        <h2>用户管理</h2>
        <div class="filters">
          <input 
            v-model="userFilters.search" 
            placeholder="搜索用户名/邮箱/手机"
            class="search-input"
          >
          <select v-model="userFilters.is_active" class="filter-select">
            <option value="">全部状态</option>
            <option value="true">已激活</option>
            <option value="false">已禁用</option>
          </select>
          <select v-model="userFilters.is_admin" class="filter-select">
            <option value="">全部用户</option>
            <option value="true">管理员</option>
            <option value="false">普通用户</option>
          </select>
        </div>
      </div>

      <div v-if="loading.users" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>

      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>头像</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>手机</th>
              <th>状态</th>
              <th>角色</th>
              <th>商品数</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>
                <img :src="user.avatar" :alt="user.username" class="user-avatar">
              </td>
              <td>{{ user.username || '未设置' }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.phone || '未设置' }}</td>
              <td>
                <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? '已激活' : '已禁用' }}
                </span>
              </td>
              <td>
                <span :class="['role-badge', user.is_admin ? 'admin' : 'user']">
                  {{ user.is_admin ? '管理员' : '用户' }}
                </span>
              </td>
              <td>{{ user.items_count }}</td>
              <td>{{ formatTime(user.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="user.id !== currentUserId"
                    @click="toggleUserStatus(user)"
                    :class="['btn', 'btn-sm', user.is_active ? 'btn-danger' : 'btn-success']"
                  >
                    {{ user.is_active ? '禁用' : '激活' }}
                  </button>
                  <button 
                    v-if="user.id !== currentUserId"
                    @click="toggleAdminStatus(user)"
                    :class="['btn', 'btn-sm', user.is_admin ? 'btn-warning' : 'btn-primary']"
                  >
                    {{ user.is_admin ? '取消管理员' : '设为管理员' }}
                  </button>
                  <button 
                    v-if="user.id !== currentUserId"
                    @click="deleteUser(user)"
                    class="btn btn-sm btn-danger"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 商品管理 -->
    <div v-if="activeTab === 'items'" class="tab-content">
      <div class="section-header">
        <h2>商品管理</h2>
        <div class="filters">
          <input 
            v-model="itemFilters.search" 
            placeholder="搜索商品标题/描述"
            class="search-input"
            @input="debouncedLoadItems"
          >
          <select v-model="itemFilters.displayStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="online">在售</option>
            <option value="sold">已售出</option>
            <option value="offline">已下架</option>
          </select>
        </div>
      </div>

      <div v-if="loading.items" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>

      <div v-else class="items-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>图片</th>
              <th>标题</th>
              <th>价格</th>
              <th>分类</th>
              <th>状态</th>
              <th>浏览量</th>
              <th>收藏数</th>
              <th>发布时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td>
                <img :src="getFirstImage(item)" :alt="item.title" class="item-image">
              </td>
              <td>{{ item.title }}</td>
              <td>¥{{ item.price }}</td>
              <td>{{ item.category || '未分类' }}</td>
              <td>
                <span :class="['status-badge', getItemDisplayStatus(item).class]">
                  {{ getItemDisplayStatus(item).text }}
                </span>
              </td>
              <td>{{ item.views }}</td>
              <td>{{ item.favorited_count }}</td>
              <td>{{ formatTime(item.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="item.status === 'online'"
                    @click="updateItemStatus(item, 'offline')"
                    class="btn btn-sm btn-warning"
                  >
                    下架
                  </button>
                  <button 
                    v-if="item.status === 'offline'"
                    @click="updateItemStatus(item, 'online')"
                    class="btn btn-sm btn-success"
                  >
                    上架
                  </button>
                  <button 
                    @click="deleteItem(item)"
                    class="btn btn-sm btn-danger"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const activeTab = ref('users')
const loading = reactive({
  users: false,
  items: false
})

const stats = ref({})
const users = ref([])
const items = ref([])

const userFilters = reactive({
  search: '',
  is_active: '',
  is_admin: ''
})

const itemFilters = reactive({
  search: '',
  displayStatus: '', // 'online', 'sold', 'offline'
})

// 计算属性
const user = computed(() => authStore.user || {})
const currentUserId = computed(() => user.value.id)

const tabs = [
  { id: 'users', label: '用户管理', icon: 'fas fa-users' },
  { id: 'items', label: '商品管理', icon: 'fas fa-box' }
]

// 方法
const loadStats = async () => {
  try {
    const response = await api.getAdminStats()
    stats.value = response.data
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const loadUsers = async () => {
  loading.users = true
  try {
    const params = {}
    if (userFilters.search) params.search = userFilters.search
    if (userFilters.is_active !== '') params.is_active = userFilters.is_active === 'true'
    if (userFilters.is_admin !== '') params.is_admin = userFilters.is_admin === 'true'
    
    const response = await api.getAdminUsers(params)
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    alert('获取用户列表失败')
  } finally {
    loading.users = false
  }
}

const loadItems = async () => {
  loading.items = true
  try {
    const params = {
      search: itemFilters.search || undefined,
    }
    
    // 根据统一的状态进行参数转换
    switch (itemFilters.displayStatus) {
      case 'online':
        params.status = 'online'
        params.sold = false
        break
      case 'sold':
        params.sold = true
        break
      case 'offline':
        params.status = 'offline'
        params.sold = false // 逻辑上，已下架的商品不应该是已售
        break
    }
    
    const response = await api.getAdminItems(params)
    items.value = response.data
  } catch (error) {
    console.error('获取商品列表失败:', error)
    alert('获取商品列表失败')
  } finally {
    loading.items = false
  }
}

const toggleUserStatus = async (user) => {
  if (!confirm(`确定要${user.is_active ? '禁用' : '激活'}用户 ${user.username || user.email} 吗？`)) {
    return
  }
  
  try {
    await api.updateUserStatus(user.id, !user.is_active)
    user.is_active = !user.is_active
    alert('操作成功')
  } catch (error) {
    console.error('更新用户状态失败:', error)
    alert('操作失败')
  }
}

const toggleAdminStatus = async (user) => {
  if (!confirm(`确定要${user.is_admin ? '取消' : '设置'}用户 ${user.username || user.email} 的管理员权限吗？`)) {
    return
  }
  
  try {
    await api.updateUserAdminStatus(user.id, !user.is_admin)
    user.is_admin = !user.is_admin
    alert('操作成功')
  } catch (error) {
    console.error('更新管理员状态失败:', error)
    alert('操作失败')
  }
}

const deleteUser = async (user) => {
  if (!confirm(`确定要删除用户 ${user.username || user.email} 吗？此操作不可恢复！`)) {
    return
  }
  
  try {
    await api.deleteAdminUser(user.id)
    users.value = users.value.filter(u => u.id !== user.id)
    alert('用户已删除')
  } catch (error) {
    console.error('删除用户失败:', error)
    alert('删除失败')
  }
}

const updateItemStatus = async (item, status) => {
  try {
    await api.updateAdminItemStatus(item.id, status)
    item.status = status
    alert('操作成功')
  } catch (error) {
    console.error('更新商品状态失败:', error)
    alert('操作失败')
  }
}

const deleteItem = async (item) => {
  if (!confirm(`确定要删除商品 "${item.title}" 吗？此操作不可恢复！`)) {
    return
  }
  
  try {
    await api.deleteAdminItem(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    alert('商品已删除')
  } catch (error) {
    console.error('删除商品失败:', error)
    alert('删除失败')
  }
}

const changeTab = (tabId) => {
  activeTab.value = tabId
  if (tabId === 'users' && users.value.length === 0) {
    loadUsers()
  } else if (tabId === 'items' && items.value.length === 0) {
    loadItems()
  }
}

const formatTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const getFirstImage = (item) => {
  if (!item.images) return 'default_product.png'
  const images = item.images.split(',')
  return images[0] || 'default_product.png'
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

// 监听用户过滤器变化
watch(userFilters, () => {
  if (activeTab.value === 'users') {
    loadUsers();
  }
}, { deep: true });

// 监听商品过滤器变化
watch(itemFilters, () => {
  if (activeTab.value === 'items') {
    loadItems();
  }
}, { deep: true });

// 新增：计算商品最终状态的函数
const getItemDisplayStatus = (item) => {
  if (item.sold) {
    return { text: '已售出', class: 'sold' }
  }
  if (item.status === 'online') {
    return { text: '在售', class: 'online' }
  }
  return { text: '已下架', class: 'offline' }
};

// 生命周期
onMounted(() => {
  loadStats()
  loadUsers()
})
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.admin-header h1 {
  margin: 0;
  color: #333;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-content h3 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.stat-content p {
  margin: 5px 0 0 0;
  color: #666;
}

.admin-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.admin-tabs button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-tabs button.active {
  border-bottom-color: #3498db;
  color: #3498db;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 10px;
}

.search-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  width: 200px;
}

.loading-state {
  padding: 20px;
}

.skeleton-row {
  height: 50px;
  background: #f5f5f5;
  margin-bottom: 10px;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.user-avatar,
.item-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.item-image {
  border-radius: 4px;
}

.status-badge,
.role-badge,
.sold-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.online {
  background: #d4edda;
  color: #155724;
}

.status-badge.offline {
  background: #f8d7da;
  color: #721c24;
}

.role-badge.admin {
  background: #d1ecf1;
  color: #0c5460;
}

.role-badge.user {
  background: #e2e3e5;
  color: #383d41;
}

.sold-badge.sold {
  background: #d4edda;
  color: #155724;
}

.sold-badge.unsold {
  background: #fff3cd;
  color: #856404;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-outline {
  background: transparent;
  border: 1px solid #ddd;
  color: #666;
}

@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
  }
  
  .filters {
    flex-direction: column;
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
  
  table {
    font-size: 12px;
  }
  
  th, td {
    padding: 8px 6px;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style> 