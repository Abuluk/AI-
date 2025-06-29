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
                <img :src="getUserAvatar(user)" :alt="user.username" class="user-avatar">
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

    <!-- 求购信息管理 -->
    <div v-if="activeTab === 'buy_requests'" class="tab-content">
      <div class="section-header">
        <h2>求购信息管理</h2>
        <div class="filters">
          <input 
            v-model="buyRequestFilters.search" 
            placeholder="搜索求购标题/描述"
            class="search-input"
          >
        </div>
      </div>

      <div v-if="loading.buy_requests" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>

      <div v-else class="buy-requests-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>描述</th>
              <th>预算</th>
              <th>发布者</th>
              <th>发布时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="buyRequest in buyRequests" :key="buyRequest.id">
              <td>{{ buyRequest.id }}</td>
              <td>{{ buyRequest.title }}</td>
              <td class="description-cell">{{ buyRequest.description || '无描述' }}</td>
              <td>¥{{ buyRequest.budget || '未设置' }}</td>
              <td>
                <div class="user-info">
                  <img :src="getUserAvatar(buyRequest.user)" :alt="buyRequest.user?.username" class="user-avatar">
                  <span>{{ buyRequest.user?.username || '未知用户' }}</span>
                </div>
              </td>
              <td>{{ formatTime(buyRequest.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="deleteBuyRequest(buyRequest)"
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

    <!-- 推广位管理 -->
    <div v-if="activeTab === 'promotions'" class="tab-content">
      <div class="section-header">
        <h2>推广位管理</h2>
        <div class="promotion-controls">
          <button @click="showPromotionModal = true" class="btn btn-primary">
            <i class="fas fa-plus"></i> 设置推广商品
          </button>
          <button @click="clearPromotions" class="btn btn-outline">
            <i class="fas fa-trash"></i> 清空推广位
          </button>
        </div>
      </div>

      <!-- 推广商品设置模态框 -->
      <div v-if="showPromotionModal" class="modal-overlay" @click="showPromotionModal = false">
        <div class="modal-content promotion-modal" @click.stop>
          <div class="modal-header">
            <h3>设置推广商品</h3>
            <button @click="showPromotionModal = false" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="promotion-info">
              <p>推广商品将显示在首页第一排，最多可设置6个商品</p>
            </div>
            <div class="form-group">
              <label>搜索商品</label>
              <input 
                v-model="promotionSearch" 
                @input="searchItemsForPromotion"
                placeholder="输入商品标题搜索"
                class="form-input"
              >
            </div>
            <div v-if="promotionSearchResults.length > 0" class="search-results">
              <h4>搜索结果</h4>
              <div class="item-grid">
                <div 
                  v-for="item in promotionSearchResults" 
                  :key="item.id"
                  class="item-card"
                  :class="{ selected: selectedPromotionItems.includes(item.id) }"
                  @click="togglePromotionItem(item.id)"
                >
                  <img :src="getFirstImage(item)" :alt="item.title" class="item-thumb">
                  <div class="item-info">
                    <h5>{{ item.title }}</h5>
                    <p class="price">¥{{ item.price }}</p>
                    <p class="status">{{ getItemDisplayStatus(item).text }}</p>
                  </div>
                  <div class="select-indicator">
                    <i class="fas fa-check"></i>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="selectedPromotionItems.length > 0" class="selected-items">
              <h4>已选择的推广商品 ({{ selectedPromotionItems.length }}/6)</h4>
              <div class="selected-grid">
                <div 
                  v-for="itemId in selectedPromotionItems" 
                  :key="itemId"
                  class="selected-item"
                >
                  <img :src="getFirstImage(getItemById(itemId))" :alt="getItemById(itemId)?.title" class="item-thumb">
                  <div class="item-info">
                    <h6>{{ getItemById(itemId)?.title }}</h6>
                    <p class="price">¥{{ getItemById(itemId)?.price }}</p>
                  </div>
                  <button @click="removePromotionItem(itemId)" class="remove-btn">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showPromotionModal = false" class="btn btn-outline">取消</button>
            <button @click="savePromotions" class="btn btn-primary" :disabled="savingPromotions">
              {{ savingPromotions ? '保存中...' : '保存推广位' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 当前推广商品展示 -->
      <div class="promotion-section">
        <h3>当前推广商品</h3>
        <div v-if="loading.promotions" class="loading-state">
          <div class="skeleton-row" v-for="n in 3" :key="n"></div>
        </div>
        <div v-else-if="promotedItems.length === 0" class="empty-state">
          <i class="fas fa-star"></i>
          <p>暂无推广商品</p>
          <p class="hint">系统将使用默认商品排序</p>
        </div>
        <div v-else class="promoted-items-grid">
          <div 
            v-for="(item, index) in promotedItems" 
            :key="item.id"
            class="promoted-item"
          >
            <div class="item-rank">{{ index + 1 }}</div>
            <img :src="getFirstImage(item)" :alt="item.title" class="item-image">
            <div class="item-details">
              <h4>{{ item.title }}</h4>
              <p class="price">¥{{ item.price }}</p>
              <p class="status">{{ getItemDisplayStatus(item).text }}</p>
              <p class="owner">发布者: {{ item.owner?.username || '未知' }}</p>
            </div>
            <div class="item-actions">
              <button @click="removePromotedItem(item.id)" class="btn btn-sm btn-danger">
                <i class="fas fa-times"></i> 移除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 商品推荐设置 -->
      <div class="recommendation-section">
        <h3>商品推荐设置</h3>
        <div class="recommendation-controls">
          <button @click="showRecommendationModal = true" class="btn btn-primary">
            <i class="fas fa-link"></i> 设置商品推荐
          </button>
        </div>

        <!-- 商品推荐设置模态框 -->
        <div v-if="showRecommendationModal" class="modal-overlay" @click="showRecommendationModal = false">
          <div class="modal-content recommendation-modal" @click.stop>
            <div class="modal-header">
              <h3>设置商品推荐</h3>
              <button @click="showRecommendationModal = false" class="close-btn">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>选择要设置推荐的商品</label>
                <input 
                  v-model="recommendationSearch" 
                  @input="searchItemsForRecommendation"
                  placeholder="输入商品标题搜索"
                  class="form-input"
                >
              </div>
              <div v-if="recommendationSearchResults.length > 0" class="search-results">
                <h4>搜索结果</h4>
                <div class="item-grid">
                  <div 
                    v-for="item in recommendationSearchResults" 
                    :key="item.id"
                    class="item-card"
                    @click="selectItemForRecommendation(item)"
                  >
                    <img :src="getFirstImage(item)" :alt="item.title" class="item-thumb">
                    <div class="item-info">
                      <h5>{{ item.title }}</h5>
                      <p class="price">¥{{ item.price }}</p>
                      <p class="status">{{ getItemDisplayStatus(item).text }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="selectedItemForRecommendation" class="selected-item-section">
                <h4>为商品 "{{ selectedItemForRecommendation.title }}" 设置推荐</h4>
                <div class="form-group">
                  <label>搜索推荐商品</label>
                  <input 
                    v-model="recommendedItemSearch" 
                    @input="searchRecommendedItems"
                    placeholder="输入推荐商品标题搜索"
                    class="form-input"
                  >
                </div>
                <div v-if="recommendedItemSearchResults.length > 0" class="search-results">
                  <h4>推荐商品搜索结果</h4>
                  <div class="item-grid">
                    <div 
                      v-for="item in recommendedItemSearchResults" 
                      :key="item.id"
                      class="item-card"
                      :class="{ selected: selectedRecommendedItems.includes(item.id) }"
                      @click="toggleRecommendedItem(item.id)"
                    >
                      <img :src="getFirstImage(item)" :alt="item.title" class="item-thumb">
                      <div class="item-info">
                        <h5>{{ item.title }}</h5>
                        <p class="price">¥{{ item.price }}</p>
                        <p class="status">{{ getItemDisplayStatus(item).text }}</p>
                      </div>
                      <div class="select-indicator">
                        <i class="fas fa-check"></i>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-if="selectedRecommendedItems.length > 0" class="selected-items">
                  <h4>已选择的推荐商品 ({{ selectedRecommendedItems.length }}/4)</h4>
                  <div class="selected-grid">
                    <div 
                      v-for="itemId in selectedRecommendedItems" 
                      :key="itemId"
                      class="selected-item"
                    >
                      <img :src="getFirstImage(getItemById(itemId))" :alt="getItemById(itemId)?.title" class="item-thumb">
                      <div class="item-info">
                        <h6>{{ getItemById(itemId)?.title }}</h6>
                        <p class="price">¥{{ getItemById(itemId)?.price }}</p>
                      </div>
                      <button @click="removeRecommendedItem(itemId)" class="remove-btn">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="showRecommendationModal = false" class="btn btn-outline">取消</button>
              <button 
                @click="saveRecommendations" 
                class="btn btn-primary" 
                :disabled="savingRecommendations || !selectedItemForRecommendation"
              >
                {{ savingRecommendations ? '保存中...' : '保存推荐' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息管理 -->
    <div v-if="activeTab === 'messages'" class="tab-content">
      <div class="section-header">
        <h2>消息管理</h2>
        <button @click="showSystemMessageModal = true" class="btn btn-primary">
          <i class="fas fa-bullhorn"></i> 发布系统消息
        </button>
      </div>

      <!-- 系统消息发布模态框 -->
      <div v-if="showSystemMessageModal" class="modal-overlay" @click="showSystemMessageModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>发布系统消息</h3>
            <button @click="showSystemMessageModal = false" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>消息标题</label>
              <input v-model="systemMessage.title" type="text" placeholder="请输入消息标题" class="form-input">
            </div>
            <div class="form-group">
              <label>消息内容</label>
              <textarea v-model="systemMessage.content" placeholder="请输入消息内容" class="form-textarea" rows="4"></textarea>
            </div>
            <div class="form-group">
              <label>目标用户</label>
              <select v-model="systemMessage.target_users" class="form-select">
                <option value="all">所有用户</option>
                <option value="buyers">买家</option>
                <option value="sellers">卖家</option>
                <option value="specific">指定用户</option>
              </select>
            </div>
            <div v-if="systemMessage.target_users === 'specific'" class="form-group">
              <label>用户ID列表（用逗号分隔）</label>
              <input v-model="systemMessage.specific_users" type="text" placeholder="1,2,3" class="form-input">
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showSystemMessageModal = false" class="btn btn-outline">取消</button>
            <button @click="publishSystemMessage" class="btn btn-primary" :disabled="publishing">
              {{ publishing ? '发布中...' : '发布消息' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-section">
        <h3>系统消息列表</h3>
        <div class="filters">
          <input 
            v-model="messageFilters.search" 
            placeholder="搜索消息内容"
            class="search-input"
          >
          <select v-model="messageFilters.target_users" class="filter-select">
            <option value="">全部目标</option>
            <option value="all">所有用户</option>
            <option value="buyers">买家</option>
            <option value="sellers">卖家</option>
          </select>
        </div>

        <div v-if="loading.messages" class="loading-state">
          <div class="skeleton-row" v-for="n in 3" :key="n"></div>
        </div>

        <div v-else class="messages-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>标题</th>
                <th>内容</th>
                <th>目标用户</th>
                <th>发布时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="message in systemMessages" :key="message.id">
                <td>{{ message.id }}</td>
                <td>{{ message.title || '无标题' }}</td>
                <td class="message-content">{{ message.content }}</td>
                <td>
                  <span class="target-badge">
                    {{ getTargetUsersText(message.target_users) }}
                  </span>
                </td>
                <td>{{ formatTime(message.created_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button 
                      @click="deleteMessage(message)"
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

    <!-- 活动页管理 -->
    <div v-if="activeTab === 'activity'" class="tab-content">
      <h2>活动页管理</h2>
      <div v-if="activityError" class="error">{{ activityError }}</div>
      <div v-if="loadingActivity">加载中...</div>
      <div v-else>
        <div class="banner-list">
          <div v-for="(banner, idx) in activityBanners" :key="idx" class="banner-item">
            <img :src="banner.img" alt="banner" style="max-width:120px;max-height:60px;">
            <input v-model="banner.img" placeholder="图片URL" style="width:200px;">
            <input v-model="banner.link" placeholder="跳转链接" style="width:200px;">
            <button @click="removeBanner(idx)">删除</button>
          </div>
        </div>
        <div class="add-banner">
          <input v-model="newBanner.img" placeholder="新图片URL" style="width:200px;">
          <input v-model="newBanner.link" placeholder="新跳转链接" style="width:200px;">
          <button @click="addBanner">添加</button>
        </div>
        <button @click="saveActivityBanners" style="margin-top:10px;">保存全部</button>
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
  items: false,
  messages: false,
  buy_requests: false,
  promotions: false
})

const stats = ref({})
const users = ref([])
const items = ref([])
const systemMessages = ref([])
const buyRequests = ref([])
const promotedItems = ref([])

// 添加缺失的分页变量
const systemMessagesPage = ref(1)
const systemMessagesLimit = ref(10)

const userFilters = reactive({
  search: '',
  is_active: '',
  is_admin: ''
})

const itemFilters = reactive({
  search: '',
  displayStatus: '', // 'online', 'sold', 'offline'
})

const messageFilters = reactive({
  search: '',
  target_users: ''
})

const buyRequestFilters = reactive({
  search: ''
})

// 系统消息相关
const showSystemMessageModal = ref(false)
const publishing = ref(false)
const systemMessage = reactive({
  title: '',
  content: '',
  target_users: 'all',
  specific_users: ''
})

// 计算属性
const user = computed(() => authStore.user || {})
const currentUserId = computed(() => user.value.id)

const tabs = [
  { id: 'users', label: '用户管理', icon: 'fas fa-users' },
  { id: 'items', label: '商品管理', icon: 'fas fa-box' },
  { id: 'buy_requests', label: '求购管理', icon: 'fas fa-shopping-cart' },
  { id: 'promotions', label: '推广位管理', icon: 'fas fa-star' },
  { id: 'messages', label: '消息管理', icon: 'fas fa-bullhorn' },
  { id: 'activity', label: '活动页管理', icon: 'fas fa-bullhorn' },
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
  // 如果是下架商品，显示确认对话框
  if (status === 'offline') {
    const confirmed = confirm(`确定要下架商品"${item.title}"吗？\n\n下架后系统将自动发送通知消息给商品所有者，告知商品因不合规内容被下架。`)
    if (!confirmed) {
      return
    }
  }
  
  try {
    await api.updateAdminItemStatus(item.id, status)
    item.status = status
    
    if (status === 'offline') {
      alert('商品已下架，系统消息已发送给商品所有者')
    } else {
      alert('操作成功')
    }
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
  } else if (tabId === 'messages') {
    loadSystemMessages()
  } else if (tabId === 'buy_requests') {
    loadBuyRequests()
  } else if (tabId === 'promotions') {
    loadPromotedItems()
  } else if (tabId === 'activity') {
    loadActivityBanners()
  }
}

const formatTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const getFirstImage = (item) => {
  if (!item.images) return '/static/images/default_product.png'
  const images = item.images.split(',')
  const img = images[0]
  if (!img) return '/static/images/default_product.png'
  if (img.startsWith('http')) return img
  if (img.startsWith('/static/images/')) return img
  if (img.startsWith('static/images/')) return `/${img}`
  return `/static/images/${img}`
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

// 获取系统消息
const loadSystemMessages = async () => {
  loading.messages = true
  try {
    // 使用正确的 API 函数
    const response = await api.getSystemMessages({
      skip: (systemMessagesPage.value - 1) * systemMessagesLimit.value,
      limit: systemMessagesLimit.value
    })
    systemMessages.value = response.data
    // 这里需要后端返回总数
    // systemMessagesTotal.value = response.data.total
  } catch (error) {
    console.error('获取系统消息失败:', error)
    alert('获取系统消息失败')
  } finally {
    loading.messages = false
  }
}

// 发布系统消息
const publishSystemMessage = async () => {
  if (!systemMessage.content.trim()) {
    alert('请输入消息内容')
    return
  }
  
  publishing.value = true
  try {
    // 使用正确的 API 函数
    await api.publishSystemMessage({
      title: systemMessage.title,
      content: systemMessage.content,
      target_users: systemMessage.target_users === 'specific' 
        ? systemMessage.specific_users 
        : systemMessage.target_users
    })
    
    alert('系统消息发布成功')
    showSystemMessageModal.value = false
    
    // 重置表单
    systemMessage.title = ''
    systemMessage.content = ''
    systemMessage.target_users = 'all'
    systemMessage.specific_users = ''
    
    // 重新加载消息列表
    loadSystemMessages()
  } catch (error) {
    console.error('发布系统消息失败:', error)
    alert('发布失败')
  } finally {
    publishing.value = false
  }
}

const deleteMessage = async (message) => {
  if (!confirm('确定要删除这条系统消息吗？')) {
    return
  }
  try {
    await api.deleteSystemMessage(message.id)
    alert('删除成功')
    loadSystemMessages()
  } catch (error) {
    console.error('删除消息失败:', error)
    alert('删除失败')
  }
}

const getTargetUsersText = (targetUsers) => {
  switch (targetUsers) {
    case 'all': return '所有用户'
    case 'buyers': return '买家'
    case 'sellers': return '卖家'
    default: return '指定用户'
  }
}

// 生命周期
onMounted(() => {
  loadStats()
  loadUsers()
  loadActivityBanners()
})

// 活动页管理相关
const activityBanners = ref([])
const loadingActivity = ref(false)
const activityError = ref('')
const newBanner = ref({ img: '', link: '' })

const loadActivityBanners = async () => {
  loadingActivity.value = true
  activityError.value = ''
  try {
    const res = await api.getAdminActivityBanners()
    console.log('管理员端活动页banner接口返回', res)
    activityBanners.value = res.data.value || []
  } catch (e) {
    console.error('管理员端获取活动页banner失败', e)
    activityError.value = '获取活动页配置失败'
  } finally {
    loadingActivity.value = false
  }
}

const saveActivityBanners = async () => {
  loadingActivity.value = true
  activityError.value = ''
  try {
    await api.saveActivityBanners(activityBanners.value)
    alert('保存成功')
  } catch (e) {
    activityError.value = '保存失败'
  } finally {
    loadingActivity.value = false
  }
}

const addBanner = () => {
  if (!newBanner.value.img || !newBanner.value.link) {
    alert('请填写图片和链接')
    return
  }
  activityBanners.value.push({ ...newBanner.value })
  newBanner.value = { img: '', link: '' }
}

const removeBanner = (idx) => {
  activityBanners.value.splice(idx, 1)
}

const getUserAvatar = (user) => {
  if (!user || !user.avatar) {
    return '/static/images/default_avatar.png'
  }
  if (user.avatar.startsWith('http')) {
    return user.avatar
  }
  if (user.avatar.startsWith('/static/images/')) {
    return user.avatar
  }
  if (user.avatar.startsWith('static/images/')) {
    return `/${user.avatar}`
  }
  return `/static/images/${user.avatar}`
}

const loadBuyRequests = async () => {
  loading.buy_requests = true
  try {
    const params = {}
    if (buyRequestFilters.search) params.search = buyRequestFilters.search
    
    const response = await api.getAdminBuyRequests(params)
    buyRequests.value = response.data
  } catch (error) {
    console.error('获取求购信息列表失败:', error)
    alert('获取求购信息列表失败')
  } finally {
    loading.buy_requests = false
  }
}

const deleteBuyRequest = async (buyRequest) => {
  const confirmed = confirm(`确定要删除求购信息"${buyRequest.title}"吗？\n\n删除后系统将自动发送通知消息给求购信息发布者，告知求购信息因不合规内容被删除。`)
  if (!confirmed) {
    return
  }
  
  try {
    await api.deleteAdminBuyRequest(buyRequest.id)
    buyRequests.value = buyRequests.value.filter(br => br.id !== buyRequest.id)
    alert('求购信息已删除，系统消息已发送给发布者')
  } catch (error) {
    console.error('删除求购信息失败:', error)
    alert('删除失败')
  }
}

// 监听求购信息过滤器变化
watch(buyRequestFilters, () => {
  if (activeTab.value === 'buy_requests') {
    loadBuyRequests();
  }
}, { deep: true });

// 推广位管理相关
const showPromotionModal = ref(false)
const promotionSearch = ref('')
const promotionSearchResults = ref([])
const selectedPromotionItems = ref([])
const savingPromotions = ref(false)

const searchItemsForPromotion = async () => {
  if (!promotionSearch.value.trim()) {
    promotionSearchResults.value = []
    return
  }
  
  try {
    const response = await api.searchItems(promotionSearch.value, { 
      limit: 20
    })
    promotionSearchResults.value = response.data.filter(item => 
      !promotedItems.value.some(promoted => promoted.id === item.id)
    )
  } catch (error) {
    console.error('搜索商品失败:', error)
    alert('搜索商品失败')
  }
}

const togglePromotionItem = (itemId) => {
  const index = selectedPromotionItems.value.indexOf(itemId)
  if (index > -1) {
    selectedPromotionItems.value.splice(index, 1)
  } else if (selectedPromotionItems.value.length < 6) {
    selectedPromotionItems.value.push(itemId)
  } else {
    alert('最多只能选择6个推广商品')
  }
}

const removePromotionItem = (itemId) => {
  const index = selectedPromotionItems.value.indexOf(itemId)
  if (index > -1) {
    selectedPromotionItems.value.splice(index, 1)
  }
}

const savePromotions = async () => {
  if (selectedPromotionItems.value.length === 0) {
    alert('请至少选择一个推广商品')
    return
  }
  
  savingPromotions.value = true
  try {
    await api.updatePromotedItems(selectedPromotionItems.value)
    alert('推广位设置成功')
    showPromotionModal.value = false
    
    // 重置表单
    promotionSearch.value = ''
    promotionSearchResults.value = []
    selectedPromotionItems.value = []
    
    // 重新加载推广商品列表
    await loadPromotedItems()
  } catch (error) {
    console.error('保存推广位失败:', error)
    alert('保存失败')
  } finally {
    savingPromotions.value = false
  }
}

const clearPromotions = async () => {
  if (!confirm('确定要清空所有推广商品吗？此操作不可恢复！')) {
    return
  }
  
  try {
    await api.updatePromotedItems([])
    promotedItems.value = []
    alert('推广位已清空')
  } catch (error) {
    console.error('清空推广位失败:', error)
    alert('清空失败')
  }
}

const removePromotedItem = async (itemId) => {
  if (!confirm('确定要移除这个推广商品吗？')) {
    return
  }
  
  try {
    const newPromotedItems = promotedItems.value
      .filter(item => item.id !== itemId)
      .map(item => item.id)
    
    await api.updatePromotedItems(newPromotedItems)
    promotedItems.value = promotedItems.value.filter(item => item.id !== itemId)
    alert('推广商品已移除')
  } catch (error) {
    console.error('移除推广商品失败:', error)
    alert('移除失败')
  }
}

const getItemById = (itemId) => {
  return promotionSearchResults.value.find(item => item.id === itemId) || 
         promotedItems.value.find(item => item.id === itemId) || 
         items.value.find(item => item.id === itemId) || {}
}

const loadPromotedItems = async () => {
  loading.promotions = true
  try {
    const response = await api.getPromotedItems()
    promotedItems.value = response.data
  } catch (error) {
    console.error('获取推广商品失败:', error)
    alert('获取推广商品失败')
  } finally {
    loading.promotions = false
  }
}

// 商品推荐设置相关
const showRecommendationModal = ref(false)
const recommendationSearch = ref('')
const recommendationSearchResults = ref([])
const selectedItemForRecommendation = ref(null)
const recommendedItemSearch = ref('')
const recommendedItemSearchResults = ref([])
const selectedRecommendedItems = ref([])
const savingRecommendations = ref(false)

const searchItemsForRecommendation = async () => {
  if (!recommendationSearch.value.trim()) {
    recommendationSearchResults.value = []
    return
  }
  
  try {
    const response = await api.searchItems(recommendedItemSearch.value, { 
      limit: 20
    })
    recommendedItemSearchResults.value = response.data.filter(item => 
      !selectedRecommendedItems.value.includes(item.id)
    )
  } catch (error) {
    console.error('搜索推荐商品失败:', error)
    alert('搜索推荐商品失败')
  }
}

const selectItemForRecommendation = (item) => {
  selectedItemForRecommendation.value = item
}

const toggleRecommendedItem = (itemId) => {
  const index = selectedRecommendedItems.value.indexOf(itemId)
  if (index > -1) {
    selectedRecommendedItems.value.splice(index, 1)
  } else if (selectedRecommendedItems.value.length < 4) {
    selectedRecommendedItems.value.push(itemId)
  } else {
    alert('最多只能选择4个推荐商品')
  }
}

const removeRecommendedItem = (itemId) => {
  const index = selectedRecommendedItems.value.indexOf(itemId)
  if (index > -1) {
    selectedRecommendedItems.value.splice(index, 1)
  }
}

const saveRecommendations = async () => {
  if (!selectedItemForRecommendation.value) {
    alert('请选择要设置推荐的商品')
    return
  }
  
  savingRecommendations.value = true
  try {
    await api.updateRecommendedItems(selectedItemForRecommendation.value.id, selectedRecommendedItems.value)
    alert('商品推荐设置成功')
    showRecommendationModal.value = false
    
    // 重置表单
    recommendationSearch.value = ''
    recommendationSearchResults.value = []
    selectedItemForRecommendation.value = null
    recommendedItemSearch.value = ''
    recommendedItemSearchResults.value = []
    selectedRecommendedItems.value = []
  } catch (error) {
    console.error('保存商品推荐失败:', error)
    alert('保存失败')
  } finally {
    savingRecommendations.value = false
  }
}
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

/* 消息管理样式 */
.messages-section {
  margin-top: 30px;
}

.messages-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.message-content {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.target-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #e3f2fd;
  color: #1976d2;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
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

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 20px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
}

/* 活动页管理样式 */
.banner-list {
  margin-bottom: 20px;
}

.banner-item {
  margin-bottom: 10px;
}

.add-banner {
  margin-bottom: 10px;
}

.error {
  color: red;
  margin-bottom: 10px;
}

/* 求购信息管理样式 */
.description-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info .user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.detail-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-main {
  display: flex;
  flex-direction: row;
  gap: 32px;
  align-items: flex-start;
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
  min-width: 320px;
}

.buy-request-image {
  width: 320px;
  height: 320px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #eee;
  margin-bottom: 10px;
}

.seller-info-card {
  width: 100%;
  background: #fafbfc;
  border-radius: 10px;
  padding: 32px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: stretch;
  margin-top: 0;
}

/* 推广位管理样式 */
.promotion-controls {
  display: flex;
  gap: 10px;
}

.promotion-modal {
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.promotion-info {
  margin-bottom: 20px;
}

.search-results {
  margin-bottom: 20px;
}

.item-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.item-card {
  width: calc(33.33% - 10px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  position: relative;
}

.item-card:hover {
  background-color: #f5f5f5;
}

.item-card.selected {
  border-color: #3498db;
  background-color: #e3f2fd;
}

.item-thumb {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}

.item-info {
  text-align: center;
}

.item-info h5 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.item-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.select-indicator {
  display: none;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  position: absolute;
  top: 5px;
  right: 5px;
}

.item-card.selected .select-indicator {
  display: flex;
}

.selected-items {
  margin-top: 20px;
}

.selected-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.selected-item {
  width: calc(33.33% - 10px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  position: relative;
}

.selected-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}

.selected-item .item-info {
  text-align: center;
}

.selected-item .item-info h6 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.selected-item .item-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.selected-item .remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #999;
}

.selected-item .remove-btn:hover {
  color: #333;
}

.promotion-section {
  margin-top: 30px;
}

.promotion-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.empty-state {
  text-align: center;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.empty-state i {
  font-size: 24px;
  color: #999;
  margin-bottom: 10px;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
  color: #666;
}

.hint {
  font-size: 14px;
  color: #999;
}

.promoted-items-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.promoted-item {
  width: calc(33.33% - 10px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  position: relative;
}

.promoted-item .item-rank {
  position: absolute;
  top: 5px;
  left: 5px;
  background: #3498db;
  color: white;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 12px;
}

.promoted-item .item-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}

.promoted-item .item-details {
  text-align: center;
}

.promoted-item .item-details h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.promoted-item .item-details p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.promoted-item .item-details .price {
  font-size: 14px;
  font-weight: 500;
}

.promoted-item .item-details .status {
  font-size: 12px;
  color: #999;
}

.promoted-item .item-details .owner {
  font-size: 12px;
  color: #999;
}

.promoted-item .item-actions {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.promoted-item .item-actions button {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #999;
}

.promoted-item .item-actions button:hover {
  color: #333;
}

/* 商品推荐设置样式 */
.recommendation-section {
  margin-top: 30px;
}

.recommendation-controls {
  margin-bottom: 20px;
}

.recommendation-modal {
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.selected-item-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style> 