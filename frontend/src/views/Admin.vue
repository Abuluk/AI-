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
        <div class="header-actions">
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
          <div class="action-buttons">
            <button @click="loadUsers(true)" class="btn btn-primary" :disabled="loading.users">
              <i class="fas fa-sync" v-if="!loading.users"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ loading.users ? '加载中...' : '刷新数据' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading.users" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>

      <div v-else class="users-table" @scroll="onTableScroll($event, 'users')">
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
        <div v-if="loadingMoreUsers" style="text-align:center;padding:8px;">加载中...</div>
        <div v-if="!hasMoreUsers && users.length > 0" style="text-align:center;padding:8px;">已加载全部</div>
      </div>
    </div>

    <!-- 商家管理 -->
    <div v-if="activeTab === 'merchants'" class="tab-content">
      <div class="section-header">
        <h2>商家管理</h2>
        <!-- 商家展示频率设置 -->
        <div class="merchant-frequency-settings">
          <label>展示频率：</label>
          <input 
            v-model.number="defaultDisplayFrequency" 
            type="number" 
            min="1" 
            max="20" 
            class="form-input frequency-input"
          >
          <span>每 {{ defaultDisplayFrequency }} 个普通商品展示1个商家商品</span>
          <button @click="updateDefaultDisplayFrequency" class="btn btn-primary btn-sm">
            保存
          </button>
        </div>
        
      </div>

      <!-- 商家管理子标签页 -->
      <div class="merchant-sub-tabs">
        <div class="sub-tab-nav">
          <button 
            :class="['sub-tab-btn', { active: merchantSubTab === 'certified' }]"
            @click="changeMerchantSubTab('certified')"
          >
            <i class="fas fa-check-circle"></i> 认证商家
          </button>
          <button 
            :class="['sub-tab-btn', { active: merchantSubTab === 'pending_verification' }]"
            @click="changeMerchantSubTab('pending_verification')"
          >
            <i class="fas fa-exclamation-triangle"></i> 待认证商家
          </button>
          <button 
            :class="['sub-tab-btn', { active: merchantSubTab === 'applications' }]"
            @click="changeMerchantSubTab('applications')"
          >
            <i class="fas fa-file-alt"></i> 商家认证申请
          </button>
        </div>

        <!-- 认证商家内容 -->
        <div v-if="merchantSubTab === 'certified'" class="sub-tab-content">
          <div class="filters">
            <input 
              v-model="merchantFilters.search" 
              placeholder="搜索商家名称/联系人"
              class="search-input"
            >
            <button @click="loadCertifiedMerchants(true)" class="btn btn-outline">刷新</button>
          </div>

          <!-- 商家列表 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户信息</th>
                  <th>店铺名称</th>
                  <th>联系人</th>
                  <th>联系电话</th>
                  <th>状态</th>
                  <th>申请时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading.merchants">
                  <td colspan="8" class="text-center">加载中...</td>
                </tr>
                <tr v-else-if="merchants.length === 0">
                  <td colspan="8" class="text-center">暂无商家数据</td>
                </tr>
                <tr v-else v-for="merchant in merchants" :key="merchant.id">
                  <td>{{ merchant.id }}</td>
                  <td>
                    <div class="user-info">
                      <img :src="getUserAvatar(merchant.user)" :alt="merchant.user?.username" class="user-avatar">
                      <div>
                        <div>{{ merchant.user?.username || '未知用户' }}</div>
                        <div class="user-id">ID: {{ merchant.user_id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>{{ merchant.business_name }}</td>
                  <td>{{ merchant.contact_person }}</td>
                  <td>{{ merchant.contact_phone }}</td>
                  <td>
                    <span class="status-badge" :class="getMerchantStatusClass(merchant.status)">
                      {{ getMerchantStatusText(merchant.status) }}
                    </span>
                  </td>
                  <td>{{ formatTime(merchant.created_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button @click="showMerchantDetails(merchant)" class="btn btn-sm btn-outline">
                        详情
                      </button>
                      <button 
                        v-if="merchant.status === 'pending'"
                        @click="approveMerchant(merchant)"
                        class="btn btn-sm btn-success"
                      >
                        通过
                      </button>
                      <button 
                        v-if="merchant.status === 'pending'"
                        @click="showRejectModal(merchant)"
                        class="btn btn-sm btn-danger"
                      >
                        拒绝
                      </button>
                      <button 
                        v-if="merchant.status === 'approved'"
                        @click="setPendingVerification(merchant)"
                        class="btn btn-sm btn-warning"
                      >
                        设为待认证
                      </button>
                      <button @click="openDeleteMerchantModal(merchant)" class="btn btn-sm btn-danger">
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 待认证商家内容 -->
        <div v-if="merchantSubTab === 'pending_verification'" class="sub-tab-content">
          <div class="filters">
            <input 
              v-model="pendingVerificationFilters.search" 
              placeholder="搜索用户名/邮箱/手机号"
              class="search-input"
            >
            <button @click="loadPendingVerificationUsers(true)" class="btn btn-outline">刷新</button>
          </div>

          <!-- 商家识别区域 -->
          <div class="merchant-identification-section">
            <h3>商家识别</h3>
            <div class="identification-controls">
              <div class="search-user">
                <label>搜索用户：</label>
                <input 
                  v-model="userSearchQuery" 
                  placeholder="输入用户名、邮箱或手机号"
                  class="form-input"
                  @keyup.enter="searchUser"
                >
                <button @click="searchUser" class="btn btn-primary">
                  <i class="fas fa-search"></i> 搜索
                </button>
              </div>
              
              <div v-if="searchedUsers.length > 0" class="search-results">
                <div class="search-results-header">
                  <h4>搜索结果 ({{ searchedUsers.length }}个用户)</h4>
                </div>
                <div class="search-results-list">
                  <div v-for="user in searchedUsers" :key="user.id" class="user-result">
                    <div class="user-info">
                      <div class="user-avatar">
                        <img :src="getUserAvatar(user)" :alt="user.username">
                      </div>
                      <div class="user-details">
                        <h4>{{ user.username }}</h4>
                        <p>ID: {{ user.id }}</p>
                        <p>邮箱: {{ user.email }}</p>
                        <p>手机: {{ user.phone }}</p>
                        <div class="user-status">
                          <span class="status-badge" :class="getUserStatusClass(user)">
                            {{ getUserStatusText(user) }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="user-actions">
                      <button 
                        v-if="!user.is_pending_verification"
                        @click="setUserPendingVerification(user)"
                        class="btn btn-danger"
                      >
                        <i class="fas fa-exclamation-triangle"></i> 设为待认证
                      </button>
                      <button 
                        v-else
                        @click="removeUserPendingVerification(user)"
                        class="btn btn-success"
                      >
                        <i class="fas fa-check"></i> 解除待认证
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 待认证用户列表 -->
          <div v-if="loading.pendingVerificationUsers" class="loading-state">
            <div class="skeleton-row" v-for="n in 5" :key="n"></div>
          </div>

          <div v-else class="pending-verification-table" @scroll="onScroll($event, 'pendingVerificationUsers')">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户信息</th>
                  <th>联系方式</th>
                  <th>状态</th>
                  <th>设置时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in pendingVerificationUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>
                    <div class="user-cell">
                      <img :src="getUserAvatar(user)" :alt="user.username" class="user-avatar-small">
                      <div>
                        <div class="user-name">{{ user.username }}</div>
                        <div class="user-id">ID: {{ user.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="contact-info">
                      <div v-if="user.email">{{ user.email }}</div>
                      <div v-if="user.phone">{{ user.phone }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="status-badge danger">待认证</span>
                  </td>
                  <td>{{ formatTime(user.updated_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button 
                        @click="showPendingUserMerchantDetails(user)"
                        class="btn btn-sm btn-info"
                      >
                        详情
                      </button>
                      <button 
                        @click="removeUserPendingVerification(user)"
                        class="btn btn-sm btn-warning"
                      >
                        解除待认证
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 商家认证申请内容 -->
        <div v-if="merchantSubTab === 'applications'" class="sub-tab-content">
          <div class="filters">
            <input 
              v-model="merchantApplicationFilters.search" 
              placeholder="搜索商家名称/联系人"
              class="search-input"
            >
            <select v-model="merchantApplicationFilters.status" class="filter-select">
              <option value="">全部状态</option>
              <option value="pending">待审核</option>
              <option value="rejected">已拒绝</option>
            </select>
            <button @click="loadMerchantApplications(true)" class="btn btn-outline">刷新</button>
          </div>

          <!-- 商家认证申请列表 -->
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户信息</th>
                  <th>店铺名称</th>
                  <th>联系人</th>
                  <th>联系电话</th>
                  <th>状态</th>
                  <th>申请时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading.merchantApplications">
                  <td colspan="8" class="loading-cell">
                    <div class="loading-spinner"></div>
                    加载中...
                  </td>
                </tr>
                <tr v-else-if="merchantApplications.length === 0">
                  <td colspan="8" class="empty-cell">暂无商家认证申请</td>
                </tr>
                <tr v-else v-for="application in merchantApplications" :key="application.id">
                  <td>{{ application.id }}</td>
                  <td>
                    <div class="user-cell">
                      <img :src="getUserAvatar(application.user)" :alt="application.user.username" class="user-avatar-small">
                      <div>
                        <div class="user-name">{{ application.user.username }}</div>
                        <div class="user-id">ID: {{ application.user.id }}</div>
                      </div>
                    </div>
                  </td>
                  <td>{{ application.business_name }}</td>
                  <td>{{ application.contact_person }}</td>
                  <td>{{ application.contact_phone }}</td>
                  <td>
                    <span :class="['status-badge', getMerchantStatusClass(application.status)]">
                      {{ getMerchantStatusText(application.status) }}
                    </span>
                  </td>
                  <td>{{ formatTime(application.created_at) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button @click="showMerchantApplicationDetails(application)" class="btn btn-sm btn-outline">
                        详情
                      </button>
                      <button 
                        v-if="application.status === 'pending'"
                        @click="approveMerchantApplication(application)"
                        class="btn btn-sm btn-success"
                      >
                        通过
                      </button>
                      <button 
                        v-if="application.status === 'pending'"
                        @click="showRejectMerchantApplicationModal(application)"
                        class="btn btn-sm btn-danger"
                      >
                        拒绝
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>



    </div>

    <!-- 商品管理 -->
    <div v-if="activeTab === 'items'" class="tab-content">
      <div class="section-header">
        <h2>商品管理</h2>
        <div class="header-actions">
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
          <div class="action-buttons">
            <button @click="loadItems(true)" class="btn btn-primary" :disabled="loading.items">
              <i class="fas fa-sync" v-if="!loading.items"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ loading.items ? '加载中...' : '刷新数据' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading.items" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>

      <div v-else class="items-table" @scroll="onTableScroll($event, 'items')">
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
        <div v-if="loadingMoreItems" style="text-align:center;padding:8px;">加载中...</div>
        <div v-if="!hasMoreItems && items.length > 0" style="text-align:center;padding:8px;">已加载全部</div>
      </div>

    </div>

    <!-- AI智能排序 -->
    <div v-if="activeTab === 'item_sorting'" class="tab-content">
      <div class="section-header">
        <h2>AI智能排序</h2>
        <div class="header-actions">
          <button @click="runSortingAlgorithm" class="btn btn-primary" :disabled="loading.sorting">
            <i class="fas fa-play" v-if="!loading.sorting"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ loading.sorting ? '运行中...' : '运行排序算法' }}
          </button>
          <button @click="loadSortingConfig" class="btn btn-secondary">
            <i class="fas fa-sync"></i>
            刷新配置
          </button>
          <button @click="loadSortingStatus(); loadSortingHistory();" class="btn btn-outline">
            <i class="fas fa-sync"></i>
            刷新状态/历史
          </button>
        </div>
      </div>

      <!-- 排序配置 -->
      <div class="sorting-settings-section">
        <div class="sorting-config-grid">
          <!-- 时间窗口配置 -->
          <div class="config-card">
            <h4>时间窗口配置</h4>
            <div class="config-item">
              <label>排序算法运行间隔（分钟）</label>
              <input 
                v-model.number="sortingConfig.time_window_minutes.default" 
                type="number" 
                min="5" 
                max="1440"
                class="form-input"
                @change="updateSortingConfig('time_window_minutes', sortingConfig.time_window_minutes)"
              >
              <small>建议值：30分钟</small>
            </div>
          </div>

          <!-- 权重因子配置 -->
          <div class="config-card">
            <h4>权重因子配置</h4>
            <div class="config-item">
              <label>基础权重占比</label>
              <input 
                v-model.number="sortingConfig.weight_factors.base_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('weight_factors', sortingConfig.weight_factors)"
              >
            </div>
            <div class="config-item">
              <label>趋势权重占比</label>
              <input 
                v-model.number="sortingConfig.weight_factors.trend_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('weight_factors', sortingConfig.weight_factors)"
              >
            </div>
            <div class="config-item">
              <label>位置权重占比</label>
              <input 
                v-model.number="sortingConfig.weight_factors.position_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('weight_factors', sortingConfig.weight_factors)"
              >
            </div>
          </div>

          <!-- 趋势计算配置 -->
          <div class="config-card">
            <h4>趋势计算配置</h4>
            <div class="config-item">
              <label>浏览量权重</label>
              <input 
                v-model.number="sortingConfig.trend_calculation.views_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('trend_calculation', sortingConfig.trend_calculation)"
              >
            </div>
            <div class="config-item">
              <label>点赞权重</label>
              <input 
                v-model.number="sortingConfig.trend_calculation.likes_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('trend_calculation', sortingConfig.trend_calculation)"
              >
            </div>
            <div class="config-item">
              <label>收藏权重</label>
              <input 
                v-model.number="sortingConfig.trend_calculation.favorites_weight" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('trend_calculation', sortingConfig.trend_calculation)"
              >
            </div>
          </div>

          <!-- 对抗曲线算法配置 -->
          <div class="config-card">
            <h4>对抗曲线算法配置</h4>
            <div class="config-item">
              <label>位置调整系数</label>
              <input 
                v-model.number="sortingConfig.position_algorithm.position_adjustment" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('position_algorithm', sortingConfig.position_algorithm)"
              >
            </div>
            <div class="config-item">
              <label>下降调整系数</label>
              <input 
                v-model.number="sortingConfig.position_algorithm.decline_adjustment" 
                type="number" 
                min="0" 
                max="1" 
                step="0.05"
                class="form-input"
                @change="updateSortingConfig('position_algorithm', sortingConfig.position_algorithm)"
              >
            </div>
            <div class="config-item">
              <label>最大位置权重</label>
              <input 
                v-model.number="sortingConfig.position_algorithm.max_position_weight" 
                type="number" 
                min="1" 
                max="2" 
                step="0.1"
                class="form-input"
                @change="updateSortingConfig('position_algorithm', sortingConfig.position_algorithm)"
              >
            </div>
          </div>
        </div>

        <!-- 排序状态和统计 -->
        <div class="sorting-status-section">
          <h4>排序状态</h4>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-label">当前时间周期：</span>
              <span class="status-value">{{ currentTimePeriod || '未运行' }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">最后运行时间：</span>
              <span class="status-value">{{ lastRunTime || '未运行' }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">处理商品数量：</span>
              <span class="status-value">{{ processedItemsCount || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">算法状态：</span>
              <span class="status-value" :class="{ 'status-running': loading.sorting }">
                {{ loading.sorting ? '运行中' : '待机' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 排序历史记录 -->
        <div class="sorting-history-section">
          <h4>排序历史记录</h4>
          <div class="history-controls">
            <button @click="loadSortingHistory" class="btn btn-outline btn-sm" :disabled="loading.history">
              <i class="fas fa-sync" v-if="!loading.history"></i>
              <i class="fas fa-spinner fa-spin" v-else></i>
              {{ loading.history ? '加载中...' : '刷新历史' }}
            </button>
            <select v-model="sortingHistoryFilter" @change="loadSortingHistory" class="form-select">
              <option value="7">最近7天</option>
              <option value="30">最近30天</option>
              <option value="90">最近90天</option>
            </select>
          </div>
          
          <div v-if="sortingHistory.length > 0" class="history-table">
            <table>
              <thead>
                <tr>
                  <th>运行时间</th>
                  <th>时间周期</th>
                  <th>处理商品数</th>
                  <th>运行时长</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in sortingHistory" :key="record.id">
                  <td>{{ formatTime(record.created_at) }}</td>
                  <td>{{ record.time_period }}</td>
                  <td>{{ record.items_processed }}</td>
                  <td>{{ record.duration }}秒</td>
                  <td>
                    <span class="status-badge" :class="record.status">
                      {{ record.status === 'success' ? '成功' : '失败' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="empty-state">
            <i class="fas fa-history"></i>
            <p>暂无排序历史记录</p>
          </div>
        </div>
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

      <div v-else class="buy-requests-table" @scroll="onScroll($event, 'buy_requests')">
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
        <div v-if="loadingMoreBuyRequests" style="text-align:center;padding:8px;">加载中...</div>
        <div v-if="!hasMoreBuyRequests && buyRequests.length > 0" style="text-align:center;padding:8px;">已加载全部</div>
      </div>
    </div>

    <!-- 商贩检测 -->
    <div v-if="activeTab === 'merchant_detection'" class="tab-content">
      <div class="section-header">
        <h2>商贩检测</h2>
        <div class="detection-status">
          <span class="status-indicator" :class="{ active: detectionStats?.schedule_enabled }">
            {{ detectionStats?.schedule_enabled ? '定时检测已启用' : '定时检测已禁用' }}
          </span>
        </div>
      </div>

      <!-- 检测配置 -->
      <div class="merchant-detection-settings">
        <h3>检测配置</h3>
        <div class="detection-controls">
          <div class="control-group">
            <label>监控商品数量：</label>
            <input 
              v-model.number="detectionConfig.monitor_top_n" 
              type="number" 
              min="10" 
              max="200" 
              class="form-input"
            >
            <span>每个分类和首页排序前N个商品</span>
          </div>
          
          <div class="control-group">
            <label>商品数阈值：</label>
            <input 
              v-model.number="detectionConfig.threshold_items" 
              type="number" 
              min="5" 
              max="50" 
              class="form-input"
            >
            <span>在售商品数超过此数量将进行AI分析</span>
          </div>
          
          <div class="control-group">
            <label>分析天数：</label>
            <input 
              v-model.number="detectionConfig.analysis_days" 
              type="number" 
              min="7" 
              max="90" 
              class="form-input"
            >
            <span>分析用户最近N天的行为数据</span>
          </div>
          
          <div class="control-group">
            <label>AI置信度阈值：</label>
            <input 
              v-model.number="detectionConfig.ai_confidence_threshold" 
              type="number" 
              min="0.1" 
              max="1.0" 
              step="0.1" 
              class="form-input"
            >
            <span>AI判断为商贩的置信度阈值</span>
          </div>
          
          <div class="control-group">
            <label>
              <input 
                v-model="detectionConfig.auto_set_pending" 
                type="checkbox"
              >
              自动设为待认证
            </label>
            <span>识别出商贩后自动设为待认证状态</span>
          </div>
          
          
          <div class="control-group">
            <label>超时自动处理天数：</label>
            <input 
              v-model.number="detectionConfig.auto_timeout_days" 
              type="number" 
              min="1" 
              max="30" 
              class="form-input"
            >
            <span>疑似商家超过此天数未确认将自动设为待认证</span>
          </div>
          
          <div class="control-group">
            <label>
              <input 
                v-model="detectionConfig.detection_schedule_enabled" 
                type="checkbox"
              >
              启用定时检测
            </label>
            <span>启用定时自动检测功能</span>
          </div>
          
          <div v-if="detectionConfig.detection_schedule_enabled" class="control-group">
            <label>检测时间：</label>
            <input 
              v-model="detectionConfig.detection_schedule_time" 
              type="time" 
              class="form-input"
            >
            <span>每天执行检测的时间（24小时制）</span>
          </div>
          
          <div class="control-actions">
            <button @click="saveDetectionConfig" class="btn btn-primary">
              保存配置
            </button>
            <button @click="runManualDetection" class="btn btn-warning" :disabled="runningDetection">
              {{ runningDetection ? '检测中...' : '手动检测' }}
            </button>
            <button @click="loadDetectionStats" class="btn btn-outline">
              刷新统计
            </button>
          </div>
        </div>
      </div>

      <!-- 检测统计信息 -->
      <div v-if="detectionStats" class="detection-stats">
        <h3>检测统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">高活跃用户：</span>
            <span class="stat-value">{{ detectionStats.high_activity_users }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">检测状态：</span>
            <span class="stat-value" :class="{ active: detectionStats.detection_enabled }">
              {{ detectionStats.detection_enabled ? '已启用' : '已禁用' }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">监控商品数：</span>
            <span class="stat-value">{{ detectionConfig.monitor_top_n }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">商品数阈值：</span>
            <span class="stat-value">{{ detectionConfig.threshold_items }}</span>
          </div>
        </div>
      </div>

      <!-- 检测结果 -->
      <div v-if="detectionResults.length > 0" class="detection-results">
        <h3>检测结果</h3>
        <div class="results-table">
          <table>
            <thead>
              <tr>
                <th>用户ID</th>
                <th>用户名</th>
                <th>在售商品数</th>
                <th>AI判断</th>
                <th>置信度</th>
                <th>检测时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in detectionResults" :key="result.user_id">
                <td>{{ result.user_id }}</td>
                <td>
                  <div class="user-info">
                    <img v-if="result.behavior_data?.avatar" 
                         :src="getAvatarUrl(result.behavior_data.avatar)" 
                         class="user-avatar" 
                         :alt="result.behavior_data?.username"
                         @error="handleAvatarError">
                    <div class="user-details">
                      <div class="username">{{ result.behavior_data?.username || '未知用户' }}</div>
                      <div class="user-email">{{ result.behavior_data?.email || '未知邮箱' }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="item-count">{{ result.active_items_count }}</span>
                  <div class="item-stats">
                    <small>总发布: {{ result.behavior_data?.total_items || 0 }}</small>
                    <small>已售: {{ result.behavior_data?.sold_items || 0 }}</small>
                  </div>
                </td>
                <td>
                  <span class="ai-judgment" :class="{ 
                    merchant: result.ai_analysis?.is_merchant, 
                    normal: !result.ai_analysis?.is_merchant 
                  }">
                    {{ result.ai_analysis?.is_merchant ? '商贩' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <div class="confidence-display">
                    <div class="confidence-value">{{ (result.ai_analysis?.confidence * 100 || 0).toFixed(1) }}%</div>
                    <div class="confidence-bar-small">
                      <div class="confidence-fill-small" 
                           :style="{ width: (result.ai_analysis?.confidence * 100 || 0) + '%' }"></div>
                    </div>
                  </div>
                </td>
                <td>{{ formatTime(result.detected_at) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="analyzeUser(result.user_id)" 
                            class="btn btn-sm btn-outline" 
                            :disabled="analyzingUser">
                      {{ analyzingUser ? '分析中...' : '详细分析' }}
                    </button>
                    <div v-if="result.history_id && !result.processed" class="merchant-actions">
                      <button @click="confirmMerchant(result.history_id)" class="btn btn-sm btn-success">
                        加入待认证
                      </button>
                      <button @click="rejectDetectionMerchant(result.history_id)" class="btn btn-sm btn-danger">
                        拒绝
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 用户分析详情 -->
      <div v-if="showUserAnalysis" class="user-analysis-modal">
        <div class="modal-overlay" @click="showUserAnalysis = false">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>用户行为分析</h3>
              <button @click="showUserAnalysis = false" class="close-btn">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body" v-if="userAnalysisData">
              <div class="analysis-sections">
                <div class="analysis-section">
                  <h4>基本信息</h4>
                  <div class="info-grid">
                    <div class="info-item">
                      <label>用户名：</label>
                      <span>{{ userAnalysisData.behavior_data?.username }}</span>
                    </div>
                    <div class="info-item">
                      <label>邮箱：</label>
                      <span>{{ userAnalysisData.behavior_data?.email }}</span>
                    </div>
                    <div class="info-item">
                      <label>分析周期：</label>
                      <span>{{ userAnalysisData.behavior_data?.analysis_period_days }}天</span>
                    </div>
                  </div>
                </div>

                <div class="analysis-section">
                  <h4>商品统计</h4>
                  <div class="stats-grid">
                    <div class="stat-card">
                      <div class="stat-number">{{ userAnalysisData.behavior_data?.total_items || 0 }}</div>
                      <div class="stat-label">总发布数</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number">{{ userAnalysisData.behavior_data?.active_items || 0 }}</div>
                      <div class="stat-label">在售商品</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number">{{ userAnalysisData.behavior_data?.sold_items || 0 }}</div>
                      <div class="stat-label">已售商品</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-number">{{ userAnalysisData.behavior_data?.daily_publish_rate || 0 }}</div>
                      <div class="stat-label">日均发布率</div>
                    </div>
                  </div>
                </div>

                <div class="analysis-section">
                  <h4>AI分析结果</h4>
                  <div class="ai-result">
                    <div class="ai-judgment-large" :class="{ 
                      merchant: userAnalysisData.ai_analysis?.is_merchant, 
                      normal: !userAnalysisData.ai_analysis?.is_merchant 
                    }">
                      {{ userAnalysisData.ai_analysis?.is_merchant ? '判定为商贩' : '判定为普通用户' }}
                    </div>
                    <div class="confidence-bar">
                      <div class="confidence-label">置信度：{{ (userAnalysisData.ai_analysis?.confidence * 100 || 0).toFixed(1) }}%</div>
                      <div class="confidence-progress">
                        <div class="confidence-fill" :style="{ width: (userAnalysisData.ai_analysis?.confidence * 100 || 0) + '%' }"></div>
                      </div>
                    </div>
                    <div class="ai-reason">
                      <strong>分析理由：</strong>
                      <p>{{ userAnalysisData.ai_analysis?.reason || '无' }}</p>
                    </div>
                    <div v-if="userAnalysisData.ai_analysis?.evidence?.length" class="ai-evidence">
                      <strong>证据：</strong>
                      <ul>
                        <li v-for="evidence in userAnalysisData.ai_analysis.evidence" :key="evidence">
                          {{ evidence }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 检测历史 -->
      <div class="detection-history">
        <div class="history-header">
          <h3>检测历史</h3>
          <div class="history-controls">
            <button @click="loadDetectionHistories(true)" class="btn btn-outline btn-sm" :disabled="detectionHistoryPagination.loading">
              {{ detectionHistoryPagination.loading ? '加载中...' : '刷新历史' }}
            </button>
            <button @click="autoProcessTimeout" class="btn btn-warning btn-sm">
              处理超时
            </button>
            <select v-model="historyFilter" @change="loadDetectionHistories(true)" class="form-select">
              <option value="">全部类型</option>
              <option value="manual">手动检测</option>
              <option value="auto">自动检测</option>
            </select>
          </div>
        </div>
        
        <div v-if="detectionHistories.length > 0" class="history-table">
          <table>
            <thead>
              <tr>
                <th>检测时间</th>
                <th>用户</th>
                <th>在售商品</th>
                <th>AI判断</th>
                <th>置信度</th>
                <th>类型</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="history in detectionHistories" :key="history.id">
                <td>{{ formatTime(history.created_at) }}</td>
                <td>
                  <div class="user-info-small">
                    <img v-if="history.behavior_data?.avatar" 
                         :src="getAvatarUrl(history.behavior_data.avatar)" 
                         class="user-avatar-small" 
                         :alt="history.behavior_data?.username"
                         @error="handleAvatarError">
                    <!-- 无头像时通过用户ID获取头像 -->
                    <img v-else 
                         :src="userAvatarUrls[history.user_id] || 'http://127.0.0.1:8000/static/images/default_avatar.png'" 
                         class="user-avatar-small" 
                         :alt="history.behavior_data?.username || '未知用户'"
                         @error="handleAvatarError"
                         @load="loadUserAvatar(history.user_id)">
                    <div class="user-details-small">
                      <div class="username-small">{{ history.behavior_data?.username || '未知用户' }}</div>
                      <div class="user-id-small">ID: {{ history.user_id }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ history.active_items_count }}</td>
                <td>
                  <span class="ai-judgment-small" :class="{ 
                    merchant: history.is_merchant, 
                    normal: !history.is_merchant 
                  }">
                    {{ history.is_merchant ? '商贩' : '普通用户' }}
                  </span>
                </td>
                <td>{{ (history.confidence * 100).toFixed(1) }}%</td>
                <td>
                  <span class="detection-type" :class="history.detection_type">
                    {{ history.detection_type === 'manual' ? '手动' : '自动' }}
                  </span>
                </td>
                <td>
                  <span class="processed-status" :class="{ processed: history.processed }">
                    {{ history.processed ? '已处理' : '待处理' }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button @click="viewHistoryDetail(history)" class="btn btn-sm btn-outline">
                      查看详情
                    </button>
                    <div v-if="!history.processed" class="merchant-actions">
                      <button @click="confirmMerchant(history.id)" class="btn btn-sm btn-success">
                        加入待认证
                      </button>
                      <button @click="rejectDetectionMerchant(history.id)" class="btn btn-sm btn-danger">
                        拒绝
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- 加载更多按钮 -->
          <div v-if="detectionHistoryPagination.hasMore" class="load-more-container">
            <button 
              @click="loadMoreDetectionHistories" 
              class="btn btn-outline btn-sm"
              :disabled="detectionHistoryPagination.loading"
            >
              {{ detectionHistoryPagination.loading ? '加载中...' : '加载更多' }}
            </button>
          </div>
          
          <!-- 无更多数据提示 -->
          <div v-else-if="detectionHistories.length > 0" class="no-more-data">
            <span>已显示全部检测记录</span>
          </div>
        </div>
        
        <div v-else class="no-history">
          <p>暂无检测历史记录</p>
        </div>
        
        <div class="history-info">
          <h4>检测说明</h4>
          <p>• 系统每天凌晨2点自动执行商贩检测</p>
          <p>• 检测结果会自动将识别出的商贩设为待认证状态</p>
          <p>• 管理员可在商家管理页面查看和管理待认证用户</p>
          <p>• 点击"详细分析"可查看AI分析的详细过程</p>
        </div>
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

      <!-- 推广间隔设置 -->
      <div class="promotion-settings">
        <h3>推广设置</h3>
        <div class="form-group">
          <label>推广商品间隔</label>
          <div class="interval-controls">
            <input 
              v-model.number="promotionInterval" 
              type="number" 
              min="1" 
              max="20" 
              class="form-input"
              style="width: 100px; margin-right: 10px;"
            >
            <span>每 {{ promotionInterval }} 个商品显示一个推广商品</span>
            <button @click="updatePromotionInterval" class="btn btn-sm btn-primary" style="margin-left: 10px;">
              保存设置
            </button>
          </div>
          <p class="help-text">设置推广商品在商品列表中的显示间隔，范围：1-20</p>
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

        <div v-else class="messages-table" @scroll="onScroll($event, 'messages')">
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
          <div v-if="loadingMoreMessages" style="text-align:center;padding:8px;">加载中...</div>
          <div v-if="!hasMoreMessages && systemMessages.length > 0" style="text-align:center;padding:8px;">已加载全部</div>
        </div>
      </div>
    </div>

    <!-- 留言管理 -->
    <div v-if="activeTab === 'feedbacks'" class="tab-content">
      <div class="section-header">
        <h2>留言管理</h2>
        <button class="btn btn-outline" @click="loadFeedbacks" :disabled="loading.feedbacks">刷新</button>
      </div>
      <div v-if="loading.feedbacks" class="loading-state">
        <div class="skeleton-row" v-for="n in 5" :key="n"></div>
      </div>
      <div v-else>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户ID</th>
              <th>内容</th>
              <th>状态</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="fb in feedbacks" :key="fb.id">
              <td>{{ fb.id }}</td>
              <td>{{ fb.user_id }}</td>
              <td style="max-width:300px;word-break:break-all;">{{ fb.content }}</td>
              <td>
                <span :class="['status-badge', fb.status === 'solved' ? 'active' : 'inactive']">
                  {{ fb.status === 'solved' ? '已解决' : '待处理' }}
                </span>
              </td>
              <td>{{ formatTime(fb.created_at) }}</td>
              <td>
                <div class="action-buttons">
                  <button v-if="fb.status !== 'solved'" class="btn btn-sm btn-success" @click="solveFeedback(fb)">已解决</button>
                  <button class="btn btn-sm btn-danger" @click="deleteFeedback(fb)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="feedbacks.length === 0" class="empty-state">暂无留言</div>
      </div>
    </div>

    <!-- AI策略 -->
    <div v-if="activeTab === 'ai_strategy'" class="tab-content">
      <div class="section-header">
        <h2>AI策略报告</h2>
        <button class="btn btn-primary" @click="getAIStrategy" :disabled="aiLoading">{{ aiLoading ? '生成中...' : '生成AI报告' }}</button>
      </div>
      <div v-if="aiLoading" class="loading-state">AI报告生成中...</div>
      <div v-else-if="aiReport">
        <div class="ai-report-card">
          <h3>AI分析报告</h3>
          <pre style="white-space:pre-wrap;word-break:break-all;">{{ aiReport }}</pre>
        </div>
      </div>
      <div v-else class="empty-state">点击上方按钮生成AI策略报告</div>
    </div>

    <!-- AI推荐管理 -->
    <div v-if="activeTab === 'ai_recommendation'" class="tab-content">
      <div class="section-header">
        <h2>AI推荐管理</h2>
        <div class="header-actions">
          <button class="btn btn-outline" @click="loadAIRecommendationStats">
            <i class="fas fa-sync-alt"></i> 刷新统计
          </button>
          <button class="btn btn-secondary" @click="showItemSelectionConfig = true">
            <i class="fas fa-filter"></i> 商品选择范围
          </button>
          <button class="btn btn-primary" @click="showAIRecommendationConfig = true">
            <i class="fas fa-cog"></i> 配置设置
          </button>
        </div>
      </div>


      <!-- 用户行为记录 -->
      <div class="section">
        <h3>用户行为记录</h3>
        <div class="table-controls">
          <div class="filter-group">
            <input 
              v-model="aiUserSearchQuery" 
              placeholder="搜索用户名/邮箱/手机"
              class="search-input"
              @input="searchUsers"
            >
            <select v-model="behaviorFilter.behavior_type" @change="loadUserBehaviors">
              <option value="">所有行为</option>
              <option value="view">浏览</option>
              <option value="click">点击</option>
              <option value="favorite">收藏</option>
              <option value="like">点赞</option>
              <option value="search">搜索</option>
            </select>
          </div>
          <button class="btn btn-outline" @click="loadUserBehaviors">
            <i class="fas fa-search"></i> 搜索
          </button>
        </div>
        
        <!-- 用户搜索结果 -->
        <div v-if="userSearchResults.length > 0" class="user-search-results">
          <h4>搜索结果</h4>
          <div class="user-list">
            <div v-for="user in userSearchResults" :key="user.id" class="user-item">
              <div class="user-info">
                <img :src="getUserAvatar(user)" :alt="user.username" class="user-avatar-small">
                <div class="user-details">
                  <div class="user-name">{{ user.username || '未设置' }}</div>
                  <div class="user-email">{{ user.email || '未设置' }}</div>
                </div>
              </div>
              <button 
                @click="addUserToSelection(user)" 
                class="btn btn-sm btn-primary"
                :disabled="isUserSelected(user.id)"
              >
                <i class="fas fa-plus"></i> 加入
              </button>
            </div>
          </div>
        </div>
        
        
        <div class="behavior-content">
          <div class="table-container behavior-table-container" v-if="activeSelectedUserId">
            <table class="data-table">
              <thead>
                <tr>
                  <th>用户</th>
                  <th>商品</th>
                  <th>行为类型</th>
                  <th>行为数据</th>
                  <th>时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="behavior in filteredUserBehaviors" :key="behavior.id">
                  <td>{{ behavior.username }}</td>
                  <td>{{ behavior.item_title || '无' }}</td>
                  <td>
                    <span class="behavior-badge" :class="behavior.behavior_type">
                      {{ getBehaviorTypeLabel(behavior.behavior_type) }}
                    </span>
                  </td>
                  <td>
                    <div v-if="behavior.behavior_data" class="behavior-data">
                      {{ JSON.stringify(behavior.behavior_data) }}
                    </div>
                    <span v-else>-</span>
                  </td>
                  <td>{{ formatDateTime(behavior.created_at) }}</td>
                  <td>
                    <button @click="deleteUserBehavior(behavior.id)" class="btn btn-sm btn-danger">
                      <i class="fas fa-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- 已选择用户队列 -->
          <div class="selected-users-sidebar">
            <h4>已选择用户 ({{ selectedUsers.length }})</h4>
            <div v-if="selectedUsers.length === 0" class="no-selected-users">
              <p>请先搜索并选择用户</p>
            </div>
            <div v-else class="selected-user-list">
              <div 
                v-for="user in selectedUsers" 
                :key="user.id" 
                class="selected-user-item"
                :class="{ active: user.id === activeSelectedUserId }"
                @click="activeSelectedUserId = user.id"
              >
                <div class="user-info">
                  <img :src="getUserAvatar(user)" :alt="user.username" class="user-avatar-small">
                  <div class="user-details">
                    <div class="user-name">{{ user.username || '未设置' }}</div>
                    <div class="user-email">{{ user.email || '未设置' }}</div>
                  </div>
                </div>
                <button @click.stop="removeUserFromSelection(user.id)" class="btn btn-sm btn-danger">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="!activeSelectedUserId || filteredUserBehaviors.length === 0" class="empty-state">
          <span v-if="selectedUsers.length === 0">请先搜索并选择用户查看行为记录</span>
          <span v-else-if="!activeSelectedUserId">请在右侧点击某个用户以查看其行为</span>
          <span v-else>所选用户暂无行为记录</span>
        </div>
      </div>

      <!-- 测试功能 -->
      <div class="section">
        <h3>AI推荐测试</h3>
        <div class="test-controls">
          <div class="form-group">
            <label>测试用户</label>
            <div class="test-user-info">
              <span v-if="selectedUsers.length === 0" class="no-users">请先在上方搜索并选择用户</span>
              <div v-else class="test-user-list">
                <div v-for="user in selectedUsers" :key="user.id" class="test-user-item">
                  <img :src="getUserAvatar(user)" :alt="user.username" class="user-avatar-small">
                  <span>{{ user.username || '未设置' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>推荐数量</label>
            <input type="number" v-model.number="testLimit" min="1" max="10" class="form-input">
          </div>
          <button @click="testAIRecommendation" class="btn btn-primary" :disabled="selectedUsers.length === 0">
            <i class="fas fa-play"></i> 测试推荐 ({{ selectedUsers.length }}个用户)
          </button>
        </div>
        
        <div v-if="testResult" class="test-result">
          <h4>推荐商品</h4>
          <div class="recommendations-grid">
            <div v-for="(userResult, index) in testResult" :key="index">
              <div v-if="userResult.result.success && userResult.result.recommendations && userResult.result.recommendations.length > 0">
                <div v-for="(item, itemIndex) in userResult.result.recommendations" :key="itemIndex" class="recommendation-card">
                  <div class="item-image">
                    <img :src="getItemImageUrl(item.images)" :alt="item.title" class="item-thumbnail">
                  </div>
                  <div class="item-details">
                    <h6 class="item-title">{{ item.title }}</h6>
                    <p class="item-category">{{ item.category }}</p>
                    <p class="item-price">¥{{ item.price }}</p>
                    <p class="item-condition">{{ getConditionLabel(item.condition) }}</p>
                  </div>
                  <div class="item-actions">
                    <button @click="viewItem(item.id)" class="btn btn-sm btn-primary">
                      <i class="fas fa-eye"></i> 查看
                    </button>
                  </div>
                </div>
              </div>
              <div v-else-if="!userResult.result.success" class="no-recommendations">
                <p>{{ userResult.result.message }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- AI推荐配置模态框 -->
    <div v-if="showAIRecommendationConfig" class="modal-overlay" @click="showAIRecommendationConfig = false">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>AI推荐配置</h3>
          <button @click="showAIRecommendationConfig = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="config-form">
            <div class="form-row">
              <div class="form-group">
                <label>行为序列长度</label>
                <input type="number" v-model.number="aiConfig.sequence_length" min="5" max="50" class="form-input">
                <small>分析用户最近N个商品浏览行为</small>
              </div>
              <div class="form-group">
                <label>推荐商品数量</label>
                <input type="number" v-model.number="aiConfig.recommendation_count" min="5" max="20" class="form-input">
                <small>每次推荐的商品数量</small>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>分类权重</label>
                <input type="number" v-model.number="aiConfig.category_weight" min="0" max="1" step="0.1" class="form-input">
                <small>商品分类在推荐中的权重</small>
              </div>
              <div class="form-group">
                <label>价格权重</label>
                <input type="number" v-model.number="aiConfig.price_weight" min="0" max="1" step="0.1" class="form-input">
                <small>商品价格在推荐中的权重</small>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>成色权重</label>
                <input type="number" v-model.number="aiConfig.condition_weight" min="0" max="1" step="0.1" class="form-input">
                <small>商品成色在推荐中的权重</small>
              </div>
              <div class="form-group">
                <label>地区权重</label>
                <input type="number" v-model.number="aiConfig.location_weight" min="0" max="1" step="0.1" class="form-input">
                <small>商品地区在推荐中的权重</small>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>最少行为记录数</label>
                <input type="number" v-model.number="aiConfig.min_behavior_count" min="1" max="20" class="form-input">
                <small>进行AI推荐所需的最少行为记录数</small>
              </div>
              <div class="form-group">
                <label>行为记录天数</label>
                <input type="number" v-model.number="aiConfig.behavior_days" min="7" max="365" class="form-input">
                <small>统计用户行为的天数范围</small>
              </div>
            </div>
            
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="aiConfig.enable_ai_analysis">
                <span class="checkmark"></span>
                启用AI分析
              </label>
              <small>是否启用AI智能分析功能</small>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAIRecommendationConfig = false" class="btn btn-outline">取消</button>
          <button @click="saveAIRecommendationConfig" class="btn btn-primary" :disabled="savingConfig">
            {{ savingConfig ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 拒绝商家模态框 -->
    <div v-if="showRejectMerchantModal" class="modal-overlay" @click="showRejectMerchantModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>拒绝商家认证</h3>
          <button @click="showRejectMerchantModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>拒绝原因</label>
            <textarea 
              v-model="rejectReason" 
              placeholder="请输入拒绝原因"
              class="form-textarea" 
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showRejectMerchantModal = false" class="btn btn-outline">取消</button>
          <button @click="rejectMerchant" class="btn btn-danger" :disabled="!rejectReason.trim()">
            确认拒绝
          </button>
        </div>
      </div>
    </div>

    <!-- 删除商家模态框 -->
    <div v-if="showDeleteMerchantModal" class="modal-overlay" @click="showDeleteMerchantModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>删除商家认证</h3>
          <button @click="showDeleteMerchantModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>删除原因</label>
            <textarea 
              v-model="deleteReason" 
              placeholder="请输入删除原因"
              class="form-textarea" 
              rows="4"
            ></textarea>
          </div>
          <div class="warning-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>删除后该用户的商家资格将被取消，用户可以重新申请商家认证。</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteMerchantModal = false" class="btn btn-outline">取消</button>
          <button @click="deleteMerchant" class="btn btn-danger" :disabled="!deleteReason.trim()">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- 商品选择范围配置弹窗 -->
    <div v-if="showItemSelectionConfig" class="modal-overlay" @click="showItemSelectionConfig = false">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>商品选择范围配置</h3>
          <button @click="showItemSelectionConfig = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="config-content">
            <div class="config-tabs">
              <button 
                :class="['tab-btn', { active: itemSelectionTab === 'sort' }]"
                @click="itemSelectionTab = 'sort'"
              >
                排序配置
              </button>
              <button 
                :class="['tab-btn', { active: itemSelectionTab === 'category' }]"
                @click="itemSelectionTab = 'category'"
              >
                分类配置
              </button>
              <button 
                :class="['tab-btn', { active: itemSelectionTab === 'general' }]"
                @click="itemSelectionTab = 'general'"
              >
                通用设置
              </button>
            </div>

            <!-- 排序配置 -->
            <div v-if="itemSelectionTab === 'sort'" class="tab-content">
              <div class="config-header">
                <h4>排序方式配置</h4>
                <p>配置AI推荐时按不同排序方式选择的商品数量</p>
              </div>
              <div class="sort-configs">
                <div v-for="(sortConfig, index) in itemSelectionConfig.sort_orders" :key="index" class="sort-config-item">
                  <div class="config-row">
                    <div class="config-field">
                      <label>
                        <input 
                          type="checkbox" 
                          v-model="sortConfig.enabled"
                          @change="updateItemSelectionConfig"
                        >
                        {{ sortConfig.name }}
                      </label>
                    </div>
                    <div class="config-field">
                      <label>数量限制</label>
                      <input 
                        type="number" 
                        v-model.number="sortConfig.limit" 
                        min="1" 
                        max="100"
                        @change="updateItemSelectionConfig"
                        class="form-input"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分类配置 -->
            <div v-if="itemSelectionTab === 'category'" class="tab-content">
              <div class="config-header">
                <h4>分类限制配置</h4>
                <p>配置每个分类最多选择的商品数量</p>
              </div>
              <div class="category-configs">
                <div v-for="(category, index) in availableCategories" :key="index" class="category-config-item">
                  <div class="config-row">
                    <div class="config-field">
                      <label>
                        <input 
                          type="checkbox" 
                          v-model="itemSelectionConfig.category_limits[category.id].enabled"
                          @change="updateItemSelectionConfig"
                        >
                        {{ category.name }} ({{ category.count }}个商品)
                      </label>
                    </div>
                    <div class="config-field">
                      <label>数量限制</label>
                      <input 
                        type="number" 
                        v-model.number="itemSelectionConfig.category_limits[category.id].limit" 
                        min="1" 
                        :max="category.count"
                        @change="updateItemSelectionConfig"
                        class="form-input"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 通用设置 -->
            <div v-if="itemSelectionTab === 'general'" class="tab-content">
              <div class="config-header">
                <h4>通用设置</h4>
                <p>配置商品选择的基本参数</p>
              </div>
              <div class="general-configs">
                <div class="config-row">
                  <div class="config-field">
                    <label>
                      <input 
                        type="checkbox" 
                        v-model="itemSelectionConfig.enable_sort_filter"
                        @change="updateItemSelectionConfig"
                      >
                      启用排序过滤
                    </label>
                  </div>
                  <div class="config-field">
                    <label>
                      <input 
                        type="checkbox" 
                        v-model="itemSelectionConfig.enable_category_filter"
                        @change="updateItemSelectionConfig"
                      >
                      启用分类过滤
                    </label>
                  </div>
                </div>
                <div class="config-row">
                  <div class="config-field">
                    <label>最大总商品数</label>
                    <input 
                      type="number" 
                      v-model.number="itemSelectionConfig.max_total_items" 
                      min="10" 
                      max="1000"
                      @change="updateItemSelectionConfig"
                      class="form-input"
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showItemSelectionConfig = false" class="btn btn-outline">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 商家详情模态框 -->
    <div v-if="showMerchantDetailModal" class="modal-overlay" @click="showMerchantDetailModal = false">
      <div class="modal-content merchant-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>商家详情</h3>
          <button @click="showMerchantDetailModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="selectedMerchant">
          <div class="merchant-detail">
            <div class="detail-row">
              <label>店铺名称：</label>
              <span>{{ selectedMerchant.business_name }}</span>
            </div>
            <div class="detail-row">
              <label>联系人：</label>
              <span>{{ selectedMerchant.contact_person }}</span>
            </div>
            <div class="detail-row">
              <label>联系电话：</label>
              <span>{{ selectedMerchant.contact_phone }}</span>
            </div>
            <div class="detail-row">
              <label>营业地址：</label>
              <span>{{ selectedMerchant.business_address }}</span>
            </div>
            <div class="detail-row" v-if="selectedMerchant.business_license">
              <label>营业执照号：</label>
              <span>{{ selectedMerchant.business_license }}</span>
            </div>
            <div class="detail-row" v-if="selectedMerchant.business_description">
              <label>商家描述：</label>
              <span>{{ selectedMerchant.business_description }}</span>
            </div>
            <div class="detail-row">
              <label>申请时间：</label>
              <span>{{ formatTime(selectedMerchant.created_at) }}</span>
            </div>
            <div class="detail-row">
              <label>当前状态：</label>
              <span :class="['status-badge', getMerchantStatusClass(selectedMerchant.status)]">
                {{ getMerchantStatusText(selectedMerchant.status) }}
              </span>
            </div>
            <div class="detail-row" v-if="selectedMerchant.reject_reason">
              <label>拒绝原因：</label>
              <span class="reject-reason">{{ selectedMerchant.reject_reason }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showMerchantDetailModal = false" class="btn btn-outline">关闭</button>
        </div>
      </div>
    </div>

    <!-- 待认证用户商家详情模态框 -->
    <div v-if="showPendingUserMerchantDetailModal" class="modal-overlay" @click="showPendingUserMerchantDetailModal = false">
      <div class="modal-content merchant-detail-modal" @click.stop>
        <div class="modal-header">
          <h3>待认证用户商家详情</h3>
          <button @click="showPendingUserMerchantDetailModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body" v-if="selectedPendingUserMerchant">
          <div class="merchant-detail">
            <div class="detail-row">
              <label>用户信息：</label>
              <span>{{ selectedPendingUserMerchant.user?.username }} (ID: {{ selectedPendingUserMerchant.user?.id }})</span>
            </div>
            <div class="detail-row">
              <label>店铺名称：</label>
              <span>{{ selectedPendingUserMerchant.business_name }}</span>
            </div>
            <div class="detail-row">
              <label>联系人：</label>
              <span>{{ selectedPendingUserMerchant.contact_person }}</span>
            </div>
            <div class="detail-row">
              <label>联系电话：</label>
              <span>{{ selectedPendingUserMerchant.contact_phone }}</span>
            </div>
            <div class="detail-row">
              <label>营业地址：</label>
              <span>{{ selectedPendingUserMerchant.business_address }}</span>
            </div>
            <div class="detail-row" v-if="selectedPendingUserMerchant.business_license">
              <label>营业执照号：</label>
              <span>{{ selectedPendingUserMerchant.business_license }}</span>
            </div>
            <div class="detail-row" v-if="selectedPendingUserMerchant.business_description">
              <label>商家描述：</label>
              <span>{{ selectedPendingUserMerchant.business_description }}</span>
            </div>
            <div class="detail-row">
              <label>申请时间：</label>
              <span>{{ formatTime(selectedPendingUserMerchant.created_at) }}</span>
            </div>
            <div class="detail-row">
              <label>当前状态：</label>
              <span class="status-badge danger">待认证</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="removeUserPendingVerification(selectedPendingUser)" class="btn btn-warning">解除待认证</button>
          <button @click="showPendingUserMerchantDetailModal = false" class="btn btn-outline">关闭</button>
        </div>
      </div>
    </div>

    <!-- 拒绝待认证用户模态框 -->
    <div v-if="showRejectPendingUserModal" class="modal-overlay" @click="showRejectPendingUserModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>拒绝待认证用户</h3>
          <button @click="showRejectPendingUserModal = false" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>拒绝原因：</label>
            <textarea 
              v-model="rejectReason" 
              placeholder="请输入拒绝原因（可选）"
              rows="4"
              class="form-control"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="rejectPendingVerificationUser" class="btn btn-danger">确认拒绝</button>
          <button @click="showRejectPendingUserModal = false" class="btn btn-outline">取消</button>
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
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
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
  merchants: false,
  messages: false,
  buy_requests: false,
  promotions: false,
  feedbacks: false,
  pendingVerificationUsers: false,
  merchantApplications: false,
  sorting: false,
  history: false
})

const stats = ref({})
const users = ref([])
const items = ref([])
const merchants = ref([])
const systemMessages = ref([])
const buyRequests = ref([])
const promotedItems = ref([])
const feedbacks = ref([])

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

// 待认证用户相关变量
const showPendingUserMerchantDetailModal = ref(false)
const showRejectPendingUserModal = ref(false)
const selectedPendingUser = ref(null)
const selectedPendingUserMerchant = ref(null)
const rejectReason = ref('')

const merchantFilters = reactive({
  search: '',
  status: ''
})

// 商家管理相关
const defaultDisplayFrequency = ref(5)
const showRejectMerchantModal = ref(false)
const showDeleteMerchantModal = ref(false)
const showMerchantDetailModal = ref(false)
const selectedMerchant = ref(null)
const deleteReason = ref('')

// 商家识别相关
const userSearchQuery = ref('')
const searchedUsers = ref([])
const searchingUser = ref(false)

// 商家管理子标签页
const merchantSubTab = ref('certified')
const pendingVerificationUsers = ref([])
const pendingVerificationFilters = reactive({
  search: ''
})
const pendingVerificationPage = ref(1)
const pendingVerificationLimit = ref(50)

// 商家认证申请相关
const merchantApplications = ref([])
const merchantApplicationFilters = reactive({
  search: '',
  status: ''
})
const merchantApplicationPage = ref(1)
const merchantApplicationLimit = ref(50)
const hasMoreMerchantApplications = ref(true)
const loadingMerchantApplications = ref(false)
const loadingMoreMerchantApplications = ref(false)

// 商贩检测相关
const detectionConfig = reactive({
  monitor_top_n: 50,
  threshold_items: 3,  // 降低阈值
  analysis_days: 30,
  ai_confidence_threshold: 0.7,
  auto_set_pending: true,
  auto_timeout_days: 7,
  detection_schedule_enabled: false,
  detection_schedule_time: '02:00'
})

// 商品排序相关
const sortingConfig = reactive({
  time_window_minutes: {
    default: 30,
    min: 5,
    max: 1440
  },
  weight_factors: {
    base_weight: 0.4,
    trend_weight: 0.35,
    position_weight: 0.25
  },
  trend_calculation: {
    views_weight: 0.3,
    likes_weight: 0.25,
    favorites_weight: 0.2,
    messages_weight: 0.15,
    activity_weight: 0.1,
    max_trend_weight: 1.5,
    min_trend_weight: 0.5
  },
  position_algorithm: {
    log_base: 1.0,
    position_adjustment: 0.2,
    decline_adjustment: 0.15,
    position_factor_max: 0.3,
    max_position_weight: 1.3,
    min_position_weight: 0.7
  },
  seller_activity: {
    items_published_weight: 0.4,
    messages_replied_weight: 0.3,
    login_activity_weight: 0.3,
    max_activity_score: 10.0,
    login_score_days: {
      "1": 1.0,
      "7": 0.7,
      "30": 0.3,
      "default": 0.1
    }
  }
})

const currentTimePeriod = ref('')
const lastRunTime = ref('')
const processedItemsCount = ref(0)

// 排序历史记录相关
const sortingHistory = ref([])
const sortingHistoryFilter = ref('7')
const detectionStats = ref(null)
const runningDetection = ref(false)
const detectionResults = ref([])
const showUserAnalysis = ref(false)
const userAnalysisData = ref(null)
const detectionHistories = ref([])
const historyFilter = ref('')
const detectionHistoryPagination = ref({
  skip: 0,
  limit: 50,
  hasMore: true,
  loading: false
})
const hasMorePendingVerificationUsers = ref(true)
const loadingMorePendingVerificationUsers = ref(false)

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

// 调试认证状态
console.log('管理员页面 - 认证状态:', {
  isAuthenticated: authStore.isAuthenticated,
  hasToken: !!authStore.token,
  user: authStore.user,
  isAdmin: authStore.user?.is_admin
})

const tabs = [
  { id: 'users', label: '用户管理', icon: 'fas fa-users' },
  { id: 'items', label: '商品管理', icon: 'fas fa-box' },
  { id: 'merchants', label: '商家管理', icon: 'fas fa-store' },
  { id: 'buy_requests', label: '求购管理', icon: 'fas fa-shopping-cart' },
  { id: 'merchant_detection', label: '商贩检测', icon: 'fas fa-search' },
  { id: 'item_sorting', label: 'AI智能排序', icon: 'fas fa-sort-amount-down' },
  { id: 'promotions', label: '推广位管理', icon: 'fas fa-star' },
  { id: 'messages', label: '消息管理', icon: 'fas fa-bullhorn' },
  { id: 'feedbacks', label: '留言管理', icon: 'fas fa-comment-dots' },
  { id: 'ai_strategy', label: 'AI策略', icon: 'fas fa-robot' },
  { id: 'ai_recommendation', label: 'AI推荐管理', icon: 'fas fa-brain' },
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

// 分页与自动加载相关变量
const userPage = ref(1)
const userLimit = 50
const hasMoreUsers = ref(true)
const loadingMoreUsers = ref(false)

const itemPage = ref(1)
const itemLimit = 50
const hasMoreItems = ref(true)
const loadingMoreItems = ref(false)

const buyRequestPage = ref(1)
const buyRequestLimit = 50
const hasMoreBuyRequests = ref(true)
const loadingMoreBuyRequests = ref(false)

const messagePage = ref(1)
const messageLimit = ref(50)
const hasMoreMessages = ref(true)
const loadingMoreMessages = ref(false)

const merchantPage = ref(1)
const merchantLimit = 50
const hasMoreMerchants = ref(true)
const loadingMoreMerchants = ref(false)

// 用户管理自动加载
const loadUsers = async (reset = false) => {
  if (loading.users || loadingMoreUsers.value) return
  if (reset) {
    userPage.value = 1
    hasMoreUsers.value = true
    users.value = []
  }
  if (!hasMoreUsers.value) return
  loading.users = userPage.value === 1
  loadingMoreUsers.value = userPage.value > 1
  try {
    const params = {
      skip: (userPage.value - 1) * userLimit,
      limit: userLimit
    }
    if (userFilters.search) params.search = userFilters.search
    if (userFilters.is_active !== '') params.is_active = userFilters.is_active === 'true'
    if (userFilters.is_admin !== '') params.is_admin = userFilters.is_admin === 'true'
    
    console.log('加载用户数据，参数:', params)
    const response = await api.getAdminUsers(params)
    console.log('用户数据响应:', response.data)
    
    if (userPage.value === 1) {
      users.value = response.data
    } else {
      users.value.push(...response.data)
    }
    if (response.data.length < userLimit) {
      hasMoreUsers.value = false
    } else {
      userPage.value++
    }
    console.log('用户分页状态:', {
      currentPage: userPage.value,
      hasMore: hasMoreUsers.value,
      dataLength: response.data.length,
      limit: userLimit
    })
  } catch (error) {
    console.error('获取用户列表失败:', error)
    alert('获取用户列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.users = false
    loadingMoreUsers.value = false
  }
}

// 商品管理自动加载
const loadItems = async (reset = false) => {
  if (loading.items || loadingMoreItems.value) return
  if (reset) {
    itemPage.value = 1
    hasMoreItems.value = true
    items.value = []
  }
  if (!hasMoreItems.value) return
  loading.items = itemPage.value === 1
  loadingMoreItems.value = itemPage.value > 1
  try {
    const params = {
      skip: (itemPage.value - 1) * itemLimit,
      limit: itemLimit,
      search: itemFilters.search || undefined,
    }
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
        params.sold = false
        break
    }
    console.log('加载商品数据，参数:', params)
    const response = await api.getAdminItems(params)
    console.log('商品数据响应:', response.data)
    
    if (itemPage.value === 1) {
      items.value = response.data
    } else {
      items.value.push(...response.data)
    }
    if (response.data.length < itemLimit) {
      hasMoreItems.value = false
    } else {
      itemPage.value++
    }
    console.log('商品分页状态:', {
      currentPage: itemPage.value,
      hasMore: hasMoreItems.value,
      dataLength: response.data.length,
      limit: itemLimit
    })
  } catch (error) {
    console.error('获取商品列表失败:', error)
    alert('获取商品列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.items = false
    loadingMoreItems.value = false
  }
}

// 商家管理自动加载（加载所有商家，用于其他地方的调用）
const loadMerchants = async (reset = false) => {
  if (loading.merchants || loadingMoreMerchants.value) return
  if (reset) {
    merchantPage.value = 1
    hasMoreMerchants.value = true
    merchants.value = []
  }
  if (!hasMoreMerchants.value) return
  loading.merchants = merchantPage.value === 1
  loadingMoreMerchants.value = merchantPage.value > 1
  try {
    const params = {
      skip: (merchantPage.value - 1) * merchantLimit,
      limit: merchantLimit
    }
    if (merchantFilters.search) params.search = merchantFilters.search
    if (merchantFilters.status) params.status = merchantFilters.status
    const response = await api.getAllMerchants(params)
    const merchantsData = response.data.data || response.data || []
    if (merchantPage.value === 1) {
      merchants.value = merchantsData
    } else {
      merchants.value.push(...merchantsData)
    }
    // 使用后端返回的has_more字段判断是否还有更多数据
    if (response.data.has_more === false || merchantsData.length < merchantLimit) {
      hasMoreMerchants.value = false
    } else {
      merchantPage.value++
    }
  } catch (error) {
    console.error('获取商家列表失败:', error)
    alert('获取商家列表失败')
  } finally {
    loading.merchants = false
    loadingMoreMerchants.value = false
  }
}

// 求购管理自动加载
const loadBuyRequests = async (reset = false) => {
  if (loading.buy_requests || loadingMoreBuyRequests.value) return
  if (reset) {
    buyRequestPage.value = 1
    hasMoreBuyRequests.value = true
    buyRequests.value = []
  }
  if (!hasMoreBuyRequests.value) return
  loading.buy_requests = buyRequestPage.value === 1
  loadingMoreBuyRequests.value = buyRequestPage.value > 1
  try {
    const params = {
      skip: (buyRequestPage.value - 1) * buyRequestLimit,
      limit: buyRequestLimit
    }
    if (buyRequestFilters.search) params.search = buyRequestFilters.search
    const response = await api.getAdminBuyRequests(params)
    if (buyRequestPage.value === 1) {
      buyRequests.value = response.data
    } else {
      buyRequests.value.push(...response.data)
    }
    if (response.data.length < buyRequestLimit) {
      hasMoreBuyRequests.value = false
    } else {
      buyRequestPage.value++
    }
  } catch (error) {
    alert('获取求购信息列表失败')
  } finally {
    loading.buy_requests = false
    loadingMoreBuyRequests.value = false
  }
}

// 消息管理自动加载
const loadSystemMessages = async (reset = false) => {
  if (loading.messages || loadingMoreMessages.value) return
  if (reset) {
    messagePage.value = 1
    hasMoreMessages.value = true
    systemMessages.value = []
  }
  if (!hasMoreMessages.value) return
  loading.messages = messagePage.value === 1
  loadingMoreMessages.value = messagePage.value > 1
  try {
    const response = await api.getSystemMessages({
      skip: (messagePage.value - 1) * messageLimit.value,
      limit: messageLimit.value
    })
    if (messagePage.value === 1) {
      systemMessages.value = response.data
    } else {
      systemMessages.value.push(...response.data)
    }
    if (response.data.length < messageLimit.value) {
      hasMoreMessages.value = false
    } else {
      messagePage.value++
    }
  } catch (error) {
    alert('获取系统消息失败')
  } finally {
    loading.messages = false
    loadingMoreMessages.value = false
  }
}

// 简单防抖函数
const debounce = (fn, delay = 150) => {
  let timerId = null
  return (...args) => {
    if (timerId) clearTimeout(timerId)
    timerId = setTimeout(() => fn(...args), delay)
  }
}

// 页面滚动监听（防抖 + 仅在接近底部/触发加载时打印日志）
const onPageScrollHandler = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  const threshold = 100

  const isNearBottom = scrollTop + windowHeight >= documentHeight - threshold

  if (!isNearBottom) return

  console.log(`页面滚动到底部，当前标签: ${activeTab.value}`)
  if (activeTab.value === 'users' && hasMoreUsers.value && !loading.users && !loadingMoreUsers.value) {
    console.log('触发用户数据加载')
    loadUsers(false)
  } else if (activeTab.value === 'items' && hasMoreItems.value && !loading.items && !loadingMoreItems.value) {
    console.log('触发商品数据加载')
    loadItems(false)
  } else if (activeTab.value === 'merchants' && merchantSubTab.value === 'certified' && hasMoreMerchants.value && !loading.merchants && !loadingMoreMerchants.value) {
    console.log('触发认证商家数据加载')
    loadCertifiedMerchants(false)
  } else if (activeTab.value === 'buy_requests' && hasMoreBuyRequests.value && !loading.buy_requests && !loadingMoreBuyRequests.value) {
    console.log('触发求购数据加载')
    loadBuyRequests(false)
  } else if (activeTab.value === 'messages' && hasMoreMessages.value && !loading.messages && !loadingMoreMessages.value) {
    console.log('触发消息数据加载')
    loadSystemMessages(false)
  } else if (activeTab.value === 'merchants' && merchantSubTab.value === 'pending_verification' && hasMorePendingVerificationUsers.value && !loading.pendingVerificationUsers && !loadingMorePendingVerificationUsers.value) {
    console.log('触发待认证用户数据加载')
    loadPendingVerificationUsers(false)
  } else if (activeTab.value === 'merchants' && merchantSubTab.value === 'applications' && hasMoreMerchantApplications.value && !loading.merchantApplications && !loadingMoreMerchantApplications.value) {
    console.log('触发商家认证申请数据加载')
    loadMerchantApplications(false)
  }
}

const onPageScroll = debounce(onPageScrollHandler, 150)

// 表格容器滚动监听（保留用于其他功能）
const onTableScroll = (e, type) => {
  const el = e.target
  const scrollTop = el.scrollTop
  const clientHeight = el.clientHeight
  const scrollHeight = el.scrollHeight
  const threshold = 10
  
  console.log(`${type} 表格滚动事件:`, {
    scrollTop,
    clientHeight,
    scrollHeight,
    isNearBottom: scrollTop + clientHeight >= scrollHeight - threshold,
    hasMore: type === 'users' ? hasMoreUsers.value : hasMoreItems.value
  })
  
  if (scrollTop + clientHeight >= scrollHeight - threshold) {
    console.log(`触发${type}数据加载`)
    if (type === 'users') loadUsers(false)
    if (type === 'items') loadItems(false)
    if (type === 'merchants') loadMerchants(false)
    if (type === 'buy_requests') loadBuyRequests(false)
    if (type === 'messages') loadSystemMessages(false)
    if (type === 'pendingVerificationUsers') loadPendingVerificationUsers(false)
  }
}

// 过滤器变化时重置分页
watch(userFilters, () => {
  if (activeTab.value === 'users') loadUsers(true)
}, { deep: true })
watch(itemFilters, () => {
  if (activeTab.value === 'items') loadItems(true)
}, { deep: true })
watch(buyRequestFilters, () => {
  if (activeTab.value === 'buy_requests') loadBuyRequests(true)
}, { deep: true })

watch(merchantFilters, () => {
  if (activeTab.value === 'merchants' && merchantSubTab.value === 'certified') loadCertifiedMerchants(true)
}, { deep: true })

watch(pendingVerificationFilters, () => {
  if (activeTab.value === 'merchants' && merchantSubTab.value === 'pending_verification') loadPendingVerificationUsers(true)
}, { deep: true })

watch(merchantApplicationFilters, () => {
  if (activeTab.value === 'merchants' && merchantSubTab.value === 'applications') loadMerchantApplications(true)
}, { deep: true })

// tab切换时重置分页
const changeTab = (tabId) => {
  activeTab.value = tabId
  if (tabId === 'users') loadUsers(true)
  else if (tabId === 'items') loadItems(true)
  else if (tabId === 'item_sorting') { loadSortingStatus(); loadSortingHistory(); }
  else if (tabId === 'merchants') loadCertifiedMerchants(true)
  else if (tabId === 'messages') loadSystemMessages(true)
  else if (tabId === 'buy_requests') loadBuyRequests(true)
  else if (tabId === 'promotions') loadPromotedItems()
  else if (tabId === 'activity') loadActivityBanners()
  else if (tabId === 'feedbacks') loadFeedbacks()
}

const getImageUrl = (imagePath) => {
  if (!imagePath) return ''
  
  // 强制使用HTTP协议避免SSL错误
  if (imagePath.startsWith('http://')) {
    return imagePath
  }
  
  if (imagePath.startsWith('https://')) {
    // 将HTTPS转换为HTTP
    return imagePath.replace('https://', 'http://')
  }
  
  if (imagePath.startsWith('/static/')) {
    return 'http://127.0.0.1:8000' + imagePath
  }
  
  return 'http://127.0.0.1:8000/static/images/' + imagePath
}

const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) {
    return 'http://127.0.0.1:8000/static/images/default_avatar.png'
  }
  
  // 强制使用HTTP协议避免SSL错误
  if (avatarPath.startsWith('http://')) {
    return avatarPath
  }
  
  if (avatarPath.startsWith('https://')) {
    // 将HTTPS转换为HTTP
    return avatarPath.replace('https://', 'http://')
  }
  
  if (avatarPath.startsWith('/static/')) {
    return 'http://127.0.0.1:8000' + avatarPath
  }
  
  if (avatarPath.startsWith('static/')) {
    return 'http://127.0.0.1:8000/' + avatarPath
  }
  
  // 默认情况：假设是文件名，添加到静态路径
  return 'http://127.0.0.1:8000/static/images/' + avatarPath
}

// 存储用户头像URL的响应式对象
const userAvatarUrls = reactive({})

const getUserAvatarUrl = (userId) => {
  // 如果已经缓存了头像URL，直接返回
  if (userAvatarUrls[userId]) {
    return userAvatarUrls[userId]
  }
  
  // 否则返回默认头像，并异步获取真实头像
  loadUserAvatar(userId)
  return 'http://127.0.0.1:8000/static/images/default_avatar.png'
}

const loadUserAvatar = async (userId) => {
  try {
    const response = await api.getUser(userId)
    if (response.data && response.data.avatar) {
      // 使用getAvatarUrl函数来处理头像URL
      userAvatarUrls[userId] = getAvatarUrl(response.data.avatar)
    }
  } catch (error) {
    console.log(`获取用户 ${userId} 头像失败:`, error)
  }
}

const handleAvatarError = (event) => {
  // 头像加载失败时显示默认头像
  event.target.src = 'http://127.0.0.1:8000/static/images/default_avatar.png'
  event.target.onerror = null // 防止无限循环
}

const formatTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const loadDetectionHistories = async (reset = false) => {
  if (detectionHistoryPagination.value.loading) return
  
  try {
    detectionHistoryPagination.value.loading = true
    
    if (reset) {
      detectionHistoryPagination.value.skip = 0
      detectionHistories.value = []
    }
    
    const params = {
      skip: detectionHistoryPagination.value.skip,
      limit: detectionHistoryPagination.value.limit
    }
    if (historyFilter.value) {
      params.detection_type = historyFilter.value
    }
    
    const response = await api.getDetectionHistories(params)
    const newHistories = response.data.histories || response.histories || []
    
    if (reset) {
      detectionHistories.value = newHistories
    } else {
      detectionHistories.value.push(...newHistories)
    }
    
    // 检查是否还有更多数据
    detectionHistoryPagination.value.hasMore = newHistories.length === detectionHistoryPagination.value.limit
    
    // 预加载所有需要的用户头像
    for (const history of newHistories) {
      if (!history.behavior_data?.avatar && history.user_id) {
        loadUserAvatar(history.user_id)
      }
    }
  } catch (error) {
    console.error('加载检测历史失败:', error)
  } finally {
    detectionHistoryPagination.value.loading = false
  }
}

const loadMoreDetectionHistories = async () => {
  if (!detectionHistoryPagination.value.hasMore || detectionHistoryPagination.value.loading) return
  
  detectionHistoryPagination.value.skip += detectionHistoryPagination.value.limit
  await loadDetectionHistories(false)
}

const viewHistoryDetail = (history) => {
  // 使用历史记录中的数据进行详细分析
  userAnalysisData.value = {
    behavior_data: history.behavior_data,
    ai_analysis: history.ai_analysis
  }
  showUserAnalysis.value = true
}

// 管理员确认疑似商家
const confirmMerchant = async (historyId) => {
  if (!confirm('确定要将该用户设为待认证状态吗？')) {
    return
  }
  
  try {
    await api.confirmMerchant(historyId)
    alert('用户已设为待认证状态')
    // 刷新历史
    await loadDetectionHistories(true)
    // 如果来源于“检测结果”区域，顺便本地标记已处理
    if (Array.isArray(detectionResults.value) && detectionResults.value.length > 0) {
      detectionResults.value = detectionResults.value.map(r => {
        if (r && r.history_id === historyId) {
          return { ...r, processed: true }
        }
        return r
      })
    }
  } catch (error) {
    console.error('确认商家失败:', error)
    alert('操作失败，请重试')
  }
}

// 管理员拒绝疑似商家
const rejectDetectionMerchant = async (historyId) => {
  if (!confirm('确定要拒绝该用户为商家吗？')) {
    return
  }
  
  try {
    await api.rejectMerchant(historyId)
    alert('已拒绝该用户为商家')
    // 刷新历史
    await loadDetectionHistories(true)
    // 本地标记为已处理
    if (Array.isArray(detectionResults.value) && detectionResults.value.length > 0) {
      detectionResults.value = detectionResults.value.map(r => {
        if (r && r.history_id === historyId) {
          return { ...r, processed: true }
        }
        return r
      })
    }
  } catch (error) {
    console.error('拒绝商家失败:', error)
    alert('操作失败，请重试')
  }
}

// 自动处理超时的疑似商家
const autoProcessTimeout = async () => {
  if (!confirm('确定要处理所有超时的疑似商家吗？\n\n这将自动将超时的疑似商家设为待认证状态。')) {
    return
  }
  
  try {
    const response = await api.autoProcessTimeout()
    alert(response.data.message || '处理完成')
    await loadDetectionHistories(true)
  } catch (error) {
    console.error('处理超时失败:', error)
    alert('操作失败，请重试')
  }
}

const getFirstImage = (item) => {
  if (!item.images) return 'http://127.0.0.1:8000/static/images/default_product.jpg'
  const images = item.images.split(',')
  const img = images[0]
  if (!img) return 'http://127.0.0.1:8000/static/images/default_product.jpg'
  if (img.startsWith('http')) return img
  if (img.startsWith('/static/images/')) return `http://127.0.0.1:8000${img}`
  if (img.startsWith('static/images/')) return `http://127.0.0.1:8000/${img}`
  return `http://127.0.0.1:8000/static/images/${img}`
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

// 商品排序相关方法
const loadSortingConfig = async () => {
  try {
    const response = await api.getSortingConfig()
    const configs = response.data.configs || {}
    
    // 更新配置数据
    if (configs.time_window_minutes) {
      Object.assign(sortingConfig.time_window_minutes, configs.time_window_minutes)
    }
    if (configs.weight_factors) {
      Object.assign(sortingConfig.weight_factors, configs.weight_factors)
    }
    if (configs.trend_calculation) {
      Object.assign(sortingConfig.trend_calculation, configs.trend_calculation)
    }
    if (configs.position_algorithm) {
      Object.assign(sortingConfig.position_algorithm, configs.position_algorithm)
    }
    if (configs.seller_activity) {
      Object.assign(sortingConfig.seller_activity, configs.seller_activity)
    }
    
    console.log('排序配置加载成功')
  } catch (error) {
    console.error('加载排序配置失败:', error)
    alert('加载排序配置失败')
  }
}


const updateSortingConfig = async (configKey, configValue) => {
  try {
    await api.updateSortingConfig({
      config_key: configKey,
      config_value: configValue,
      description: `更新${configKey}配置`
    })
    console.log(`${configKey}配置更新成功`)
  } catch (error) {
    console.error(`更新${configKey}配置失败:`, error)
    alert(`更新${configKey}配置失败`)
  }
}

const runSortingAlgorithm = async () => {
  if (!confirm('确定要运行商品排序算法吗？\n\n这将重新计算所有商品的排序权重。')) {
    return
  }
  
  loading.sorting = true
  try {
    const response = await api.runSortingAlgorithm(sortingConfig.time_window_minutes.default)
    
    const result = response.data.result
    currentTimePeriod.value = result.time_period
    processedItemsCount.value = result.weights_created
    lastRunTime.value = new Date().toLocaleString('zh-CN')
    
    alert(`排序算法运行成功！\n处理商品数量: ${result.weights_created}\n时间周期: ${result.time_period}`)
  } catch (error) {
    console.error('运行排序算法失败:', error)
    alert('运行排序算法失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.sorting = false
  }
}

// 加载排序历史记录
const loadSortingHistory = async () => {
  loading.history = true
  try {
    const days = Number(sortingHistoryFilter.value || 7)
    const res = await api.getSortingHistory(days)
    sortingHistory.value = res.data?.records || []
  } catch (error) {
    console.error('加载排序历史失败:', error)
  } finally {
    loading.history = false
  }
}

// 加载排序状态
const loadSortingStatus = async () => {
  try {
    const res = await api.getSortingStatus()
    const data = res.data || {}
    currentTimePeriod.value = data.current_time_period || '未运行'
    processedItemsCount.value = data.items_processed || 0
    lastRunTime.value = data.last_run_time ? new Date(data.last_run_time).toLocaleString('zh-CN') : '未运行'
  } catch (error) {
    console.error('加载排序状态失败:', error)
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
onMounted(async () => {
  console.log('管理员页面初始化开始')
  console.log('当前用户:', user.value)
  console.log('认证token:', localStorage.getItem('access_token'))
  
  try {
    await loadStats()
    console.log('统计信息加载完成')
    
    await loadUsers(true)
    console.log('用户数据加载完成，用户数量:', users.value.length)
    
    await loadActivityBanners()
    loadDefaultDisplayFrequency()
    loadDetectionConfig()
    loadDetectionStats()
    loadDetectionHistories()
    loadAIRecommendationConfig()
    loadAIRecommendationStats()
    loadUserBehaviors()
    loadSortingConfig()
    loadItemSelectionConfig()
    loadAvailableCategories()
    // 初次进入也加载一次排序状态与历史
    loadSortingStatus()
    loadSortingHistory()

    // 添加页面滚动事件监听
    window.addEventListener('scroll', onPageScroll)
    
    console.log('管理员页面初始化完成')
  } catch (error) {
    console.error('管理员页面初始化失败:', error)
  }
})

// 组件卸载时移除滚动监听
// 注意：在Vue 3中，onUnmounted需要在setup函数内部调用
// 这里我们使用beforeUnmount作为替代

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
    return 'http://127.0.0.1:8000/static/images/default_avatar.png'
  }
  
  // 强制使用HTTP协议避免SSL错误
  if (user.avatar.startsWith('http://')) {
    return user.avatar
  }
  
  if (user.avatar.startsWith('https://')) {
    // 将HTTPS转换为HTTP
    return user.avatar.replace('https://', 'http://')
  }
  
  if (user.avatar.startsWith('/static/images/')) {
    return `http://127.0.0.1:8000${user.avatar}`
  }
  
  if (user.avatar.startsWith('static/images/')) {
    return `http://127.0.0.1:8000/${user.avatar}`
  }
  
  return `http://127.0.0.1:8000/static/images/${user.avatar}`
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

// 留言管理相关
const loadingFeedbacks = ref(false)
const aiReport = ref('')
const aiLoading = ref(false)

// AI推荐管理相关变量
const aiRecommendationStats = ref({})
const userBehaviors = ref([])
const behaviorFilter = ref({
  user_id: '',
  behavior_type: ''
})
const showAIRecommendationConfig = ref(false)
const aiConfig = ref({
  sequence_length: 10,
  recommendation_count: 10,
  category_weight: 0.4,
  price_weight: 0.3,
  condition_weight: 0.2,
  location_weight: 0.1,
  enable_ai_analysis: true,
  min_behavior_count: 3,
  behavior_days: 30
})
const savingConfig = ref(false)
const testUserId = ref('')
const testLimit = ref(5)
const testResult = ref(null)

// AI推荐管理用户搜索相关变量
const aiUserSearchQuery = ref('')
const userSearchResults = ref([])
const selectedUsers = ref([])
const activeSelectedUserId = ref(null)

// 商品选择范围配置相关
const showItemSelectionConfig = ref(false)
const itemSelectionTab = ref('sort')

const itemSelectionConfig = ref({
  sort_orders: [
    { name: "按价格升序", field: "price", order: "asc", limit: 20, enabled: true },
    { name: "按价格降序", field: "price", order: "desc", limit: 20, enabled: true },
    { name: "按浏览量", field: "views", order: "desc", limit: 20, enabled: true },
    { name: "按点赞数", field: "like_count", order: "desc", limit: 20, enabled: true },
    { name: "按发布时间", field: "created_at", order: "desc", limit: 20, enabled: true }
  ],
  category_limits: {},
  max_total_items: 100,
  enable_category_filter: true,
  enable_sort_filter: true
})
const availableCategories = ref([])

const loadFeedbacks = async () => {
  loading.feedbacks = true
  try {
    const res = await api.getAllFeedbacks()
    feedbacks.value = res.data
  } catch (e) {
    alert('获取留言失败')
  } finally {
    loading.feedbacks = false
  }
}

const solveFeedback = async (fb) => {
  if (!confirm('确定将此留言标记为已解决？')) return
  try {
    await api.solveFeedback(fb.id)
    fb.status = 'solved'
    alert('已标记为已解决')
  } catch (e) {
    alert('操作失败')
  }
}

const deleteFeedback = async (fb) => {
  if (!confirm('确定要删除此留言？')) return
  try {
    await api.deleteFeedback(fb.id)
    feedbacks.value = feedbacks.value.filter(f => f.id !== fb.id)
    alert('已删除')
  } catch (e) {
    alert('删除失败')
  }
}

const getAIStrategy = async () => {
  aiLoading.value = true
  aiReport.value = ''
  try {
    const res = await api.getAIStrategyReport()
    aiReport.value = res.data.report || res.data.msg || JSON.stringify(res.data, null, 2)
  } catch (e) {
    aiReport.value = 'AI报告获取失败'
  } finally {
    aiLoading.value = false
  }
}

// AI推荐管理相关方法
const loadAIRecommendationStats = async () => {
  try {
    const response = await api.getAIRecommendationStats(30)
    if (response.data.success) {
      aiRecommendationStats.value = response.data.stats
    }
  } catch (error) {
    console.error('获取AI推荐统计失败:', error)
    alert('获取统计信息失败')
  }
}

const loadUserBehaviors = async () => {
  try {
    const params = {
      limit: 50,
      offset: 0
    }
    if (behaviorFilter.value.user_id) {
      params.user_id = behaviorFilter.value.user_id
    }
    if (behaviorFilter.value.behavior_type) {
      params.behavior_type = behaviorFilter.value.behavior_type
    }
    
    const response = await api.getUserBehaviors(params)
    if (response.data.success) {
      userBehaviors.value = response.data.behaviors
    }
  } catch (error) {
    console.error('获取用户行为记录失败:', error)
    alert('获取行为记录失败')
  }
}

const deleteUserBehavior = async (behaviorId) => {
  if (!confirm('确定要删除这条行为记录吗？')) return
  
  try {
    await api.deleteUserBehavior(behaviorId)
    alert('删除成功')
    await loadUserBehaviors()
  } catch (error) {
    console.error('删除行为记录失败:', error)
    alert('删除失败')
  }
}

const loadAIRecommendationConfig = async () => {
  try {
    const response = await api.getAIRecommendationConfig()
    if (response.data.success) {
      aiConfig.value = { ...aiConfig.value, ...response.data.config }
    }
  } catch (error) {
    console.error('获取AI推荐配置失败:', error)
  }
}

const saveAIRecommendationConfig = async () => {
  savingConfig.value = true
  try {
    await api.updateAIRecommendationConfig(aiConfig.value)
    alert('配置保存成功')
    showAIRecommendationConfig.value = false
  } catch (error) {
    console.error('保存AI推荐配置失败:', error)
    alert('保存配置失败')
  } finally {
    savingConfig.value = false
  }
}

const testAIRecommendation = async () => {
  if (selectedUsers.value.length === 0) {
    alert('请先搜索并选择测试用户')
    return
  }
  
  try {
    // 为每个选中的用户测试AI推荐
    const testPromises = selectedUsers.value.map(user => 
      api.testAIRecommendation(user.id, testLimit.value)
    )
    const responses = await Promise.all(testPromises)
    testResult.value = responses.map((response, index) => ({
      user: selectedUsers.value[index],
      result: response.data
    }))
  } catch (error) {
    console.error('测试AI推荐失败:', error)
    alert('测试失败')
  }
}

// AI推荐管理用户搜索方法
const searchUsers = async () => {
  if (!aiUserSearchQuery.value.trim()) {
    userSearchResults.value = []
    return
  }
  
  try {
    const response = await api.getAdminUsers({
      search: aiUserSearchQuery.value,
      skip: 0,
      limit: 50  // 增加搜索结果显示数量
    })
    userSearchResults.value = response.data || []
  } catch (error) {
    console.error('搜索用户失败:', error)
    userSearchResults.value = []
  }
}

// 添加用户到选择队列
const addUserToSelection = (user) => {
  if (!isUserSelected(user.id)) {
    selectedUsers.value.push(user)
    // 第一次添加时默认选中该用户
    if (!activeSelectedUserId.value) {
      activeSelectedUserId.value = user.id
    }
  }
}

// 从选择队列移除用户
const removeUserFromSelection = (userId) => {
  selectedUsers.value = selectedUsers.value.filter(user => user.id !== userId)
  if (activeSelectedUserId.value === userId) {
    // 若移除的是当前选中用户，则清空或切换到剩余第一个
    activeSelectedUserId.value = selectedUsers.value.length > 0 ? selectedUsers.value[0].id : null
  }
}

// 检查用户是否已被选择
const isUserSelected = (userId) => {
  return selectedUsers.value.some(user => user.id === userId)
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 获取推荐类型标签
const getRecommendationTypeLabel = (type) => {
  const typeMap = {
    'ai': 'AI智能推荐',
    'basic': '热门推荐',
    'fallback': '基础推荐'
  }
  return typeMap[type] || type || '未知类型'
}

// 获取商品图片URL
const getItemImageUrl = (images) => {
  if (!images) return '/static/images/default-item.png'
  const imageList = images.split(',').filter(img => img.trim())
  if (imageList.length > 0) {
    return imageList[0].startsWith('http') ? imageList[0] : `http://127.0.0.1:8000/static/uploads/items/${imageList[0]}`
  }
  return '/static/images/default-item.png'
}

// 获取商品成色标签
const getConditionLabel = (condition) => {
  const conditionMap = {
    'new': '全新',
    'like_new': '几乎全新',
    'good': '轻微使用痕迹',
    'fair': '使用痕迹明显',
    'poor': '使用痕迹严重'
  }
  return conditionMap[condition] || condition || '未知状态'
}

// 查看商品详情
const viewItem = (itemId) => {
  window.open(`/item/${itemId}`, '_blank')
}

// 商品选择范围配置相关方法
const loadItemSelectionConfig = async () => {
  try {
    const response = await api.getItemSelectionConfig()
    if (response.data && response.data.config) {
      itemSelectionConfig.value = response.data.config
    }
  } catch (error) {
    console.error('获取商品选择配置失败:', error)
  }
}

const loadAvailableCategories = async () => {
  try {
    const response = await api.getAvailableCategories()
    if (response.data && response.data.categories) {
      availableCategories.value = response.data.categories
      
      // 初始化分类限制配置
      if (Object.keys(itemSelectionConfig.value.category_limits).length === 0) {
        const categoryLimits = {}
        response.data.categories.forEach(category => {
          categoryLimits[category.id] = {
            limit: 10,
            enabled: true,
            name: category.name
          }
        })
        itemSelectionConfig.value.category_limits = categoryLimits
      }
    }
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

const updateItemSelectionConfig = async () => {
  try {
    await api.updateItemSelectionConfig(itemSelectionConfig.value)
    console.log('商品选择配置更新成功')
  } catch (error) {
    console.error('更新商品选择配置失败:', error)
    alert('更新配置失败，请重试')
  }
}

// 过滤后的用户行为记录（只显示已选择用户的行为）
const filteredUserBehaviors = computed(() => {
  if (!activeSelectedUserId.value) return []
  return userBehaviors.value.filter(behavior => behavior.user_id === activeSelectedUserId.value)
})

const getBehaviorCount = (type) => {
  if (!aiRecommendationStats.value.behavior_stats) return 0
  const behavior = aiRecommendationStats.value.behavior_stats.find(b => b.type === type)
  return behavior ? behavior.count : 0
}

const getBehaviorTypeLabel = (type) => {
  const labels = {
    'view': '浏览',
    'click': '点击',
    'favorite': '收藏',
    'like': '点赞',
    'search': '搜索'
  }
  return labels[type] || type
}

// 商家管理相关方法
const getMerchantStatusText = (status) => {
  switch (status) {
    case 'pending': return '待审核'
    case 'pending_verification': return '待认证'
    case 'approved': return '已通过'
    case 'rejected': return '已拒绝'
    default: return '未知'
  }
}

const getMerchantStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'pending_verification': return 'danger'
    case 'approved': return 'active'
    case 'rejected': return 'inactive'
    default: return 'inactive'
  }
}

const approveMerchant = async (merchant) => {
  if (!confirm(`确定要通过商家"${merchant.business_name}"的认证申请吗？`)) {
    return
  }
  
  try {
    await api.approveMerchant(merchant.id)
    merchant.status = 'approved'
    alert('商家认证已通过')
    loadCertifiedMerchants(true)
  } catch (error) {
    console.error('通过商家认证失败:', error)
    alert('操作失败')
  }
}

const showMerchantDetails = (merchant) => {
  selectedMerchant.value = merchant
  showMerchantDetailModal.value = true
}

const showRejectModal = (merchant) => {
  selectedMerchant.value = merchant
  rejectReason.value = ''
  showRejectMerchantModal.value = true
}

const rejectMerchant = async () => {
  if (!rejectReason.value.trim()) {
    alert('请输入拒绝原因')
    return
  }
  
  try {
    await api.rejectMerchant(selectedMerchant.value.id, rejectReason.value)
    selectedMerchant.value.status = 'rejected'
    selectedMerchant.value.reject_reason = rejectReason.value
    alert('商家认证已拒绝')
    showRejectMerchantModal.value = false
    loadCertifiedMerchants(true)
  } catch (error) {
    console.error('拒绝商家认证失败:', error)
    alert('操作失败')
  }
}

const setPendingVerification = async (merchant) => {
  if (!confirm(`确定要将商家"${merchant.business_name}"设为待认证状态吗？\n\n设为待认证后：\n- 该用户的所有商品将被下架\n- 用户无法发布新商品\n- 用户需要完成认证才能恢复正常状态`)) {
    return
  }
  
  try {
    await api.setPendingMerchant(merchant.user_id, {
      business_name: merchant.business_name,
      contact_person: merchant.contact_person,
      contact_phone: merchant.contact_phone,
      business_address: merchant.business_address,
      business_description: merchant.business_description
    })
    alert('已设为待认证状态')
    loadCertifiedMerchants(true)
  } catch (error) {
    console.error('设为待认证失败:', error)
    alert('操作失败，请重试')
  }
}

const openDeleteMerchantModal = (merchant) => {
  selectedMerchant.value = merchant
  deleteReason.value = ''
  showDeleteMerchantModal.value = true
}

const deleteMerchant = async () => {
  if (!deleteReason.value.trim()) {
    alert('请输入删除原因')
    return
  }
  
  if (!selectedMerchant.value) return
  
  try {
    await api.deleteMerchant(selectedMerchant.value.id, deleteReason.value)
    merchants.value = merchants.value.filter(m => m.id !== selectedMerchant.value.id)
    alert('商家已删除，系统消息已发送给用户')
    showDeleteMerchantModal.value = false
  } catch (error) {
    console.error('删除商家失败:', error)
    alert('删除失败')
  }
}

const viewMerchantDetail = (merchant) => {
  selectedMerchant.value = merchant
  showMerchantDetailModal.value = true
}

// 商家识别相关方法
const searchUser = async () => {
  if (!userSearchQuery.value.trim()) {
    alert('请输入搜索关键词')
    return
  }
  
  searchingUser.value = true
  try {
    const response = await api.searchUser(userSearchQuery.value)
    const users = response.data || response
    if (users && users.length > 0) {
      searchedUsers.value = users
    } else {
      searchedUsers.value = []
      alert('未找到用户')
    }
  } catch (error) {
    console.error('搜索用户失败:', error)
    alert('搜索用户失败，请重试')
    searchedUsers.value = []
  } finally {
    searchingUser.value = false
  }
}


const getUserStatusText = (user) => {
  if (user.is_pending_verification) return '待认证'
  if (user.is_merchant) return '已认证商家'
  if (user.is_pending_merchant) return '申请中'
  if (user.merchant) {
    // 如果有商家信息但用户状态不是商家，显示商家状态
    switch (user.merchant.status) {
      case 'pending':
        return '商家申请中'
      case 'approved':
        return '已认证商家'
      case 'rejected':
        return '商家申请被拒'
      case 'cancelled':
        return '商家已取消'
      default:
        return '商家状态未知'
    }
  }
  return '普通用户'
}

const getUserStatusClass = (user) => {
  if (user.is_pending_verification) return 'danger'
  if (user.is_merchant) return 'active'
  if (user.is_pending_merchant) return 'warning'
  if (user.merchant) {
    // 如果有商家信息，根据商家状态返回样式
    switch (user.merchant.status) {
      case 'pending':
        return 'warning'
      case 'approved':
        return 'active'
      case 'rejected':
        return 'danger'
      case 'cancelled':
        return 'inactive'
      default:
        return 'inactive'
    }
  }
  return 'inactive'
}

const setUserPendingVerification = async (user) => {
  if (!confirm(`确定要将用户"${user.username}"设为待认证状态吗？\n\n设为待认证后：\n- 该用户的所有商品将被下架\n- 用户无法发布新商品\n- 用户需要完成认证才能恢复正常状态`)) {
    return
  }
  
  try {
    await api.setPendingMerchant(user.id, {
      business_name: `${user.username}的店铺`,
      contact_person: user.username,
      contact_phone: user.phone || '13800000000',
      business_address: '待填写',
      business_description: '待填写商家信息'
    })
    alert('已设为待认证状态')
    // 更新搜索结果中用户状态
    const userIndex = searchedUsers.value.findIndex(u => u.id === user.id)
    if (userIndex !== -1) {
      searchedUsers.value[userIndex].is_pending_verification = true
      searchedUsers.value[userIndex].is_merchant = false
      searchedUsers.value[userIndex].is_pending_merchant = false
    }
  } catch (error) {
    console.error('设为待认证失败:', error)
    alert('操作失败，请重试')
  }
}

const removeUserPendingVerification = async (user) => {
  if (!confirm(`确定要解除用户"${user.username}"的待认证状态吗？`)) {
    return
  }
  
  try {
    await api.removePendingVerification(user.id)
    alert('已解除待认证状态')
    // 更新搜索结果中用户状态
    const userIndex = searchedUsers.value.findIndex(u => u.id === user.id)
    if (userIndex !== -1) {
      searchedUsers.value[userIndex].is_pending_verification = false
    }
    // 从待认证用户列表中移除
    pendingVerificationUsers.value = pendingVerificationUsers.value.filter(u => u.id !== user.id)
  } catch (error) {
    console.error('解除待认证失败:', error)
    alert('操作失败，请重试')
  }
}

// 商贩检测相关方法
const loadDetectionConfig = async () => {
  try {
    const response = await api.getDetectionConfigs()
    const configs = response.data || response
    
    // 更新配置
    configs.forEach(config => {
      if (config.key in detectionConfig) {
        if (config.key === 'auto_set_pending' || config.key === 'detection_schedule_enabled') {
          detectionConfig[config.key] = config.value === 'true'
        } else {
          detectionConfig[config.key] = parseFloat(config.value) || parseInt(config.value) || config.value
        }
      }
    })
  } catch (error) {
    console.error('加载检测配置失败:', error)
  }
}

const saveDetectionConfig = async () => {
  try {
    const configs = [
      { key: 'monitor_top_n', value: detectionConfig.monitor_top_n },
      { key: 'threshold_items', value: detectionConfig.threshold_items },
      { key: 'analysis_days', value: detectionConfig.analysis_days },
      { key: 'ai_confidence_threshold', value: detectionConfig.ai_confidence_threshold },
      { key: 'auto_set_pending', value: detectionConfig.auto_set_pending },
      { key: 'auto_timeout_days', value: detectionConfig.auto_timeout_days },
      { key: 'detection_schedule_enabled', value: detectionConfig.detection_schedule_enabled },
      { key: 'detection_schedule_time', value: detectionConfig.detection_schedule_time }
    ]
    
    for (const config of configs) {
      await api.updateDetectionConfig(config.key, { value: config.value })
    }
    
    alert('配置保存成功')
    await loadDetectionStats()
  } catch (error) {
    console.error('保存检测配置失败:', error)
    alert('保存失败，请重试')
  }
}

const runManualDetection = async () => {
  // 防止重复点击
  if (runningDetection.value) {
    return
  }
  
  if (!confirm('确定要执行手动商贩检测吗？\n\n这将分析所有高活跃用户，可能需要几分钟时间。')) {
    return
  }
  
  runningDetection.value = true
  try {
    const response = await api.runManualDetection({
      top_n: detectionConfig.monitor_top_n,
      threshold_items: detectionConfig.threshold_items,
      analysis_days: detectionConfig.analysis_days
    })
    
    const result = response.data || response
    detectionResults.value = result.results || []
    
    alert(`检测完成！\n\n分析用户：${result.total_analyzed}个\n检测到商贩：${result.detected_merchants}个`)
    
    // 刷新统计信息
    await loadDetectionStats()
    // 刷新检测历史，确保新结果具备“加入/拒绝”操作
    await loadDetectionHistories(true)
  } catch (error) {
    console.error('手动检测失败:', error)
    if (error.code === 'ECONNABORTED') {
      alert('检测请求超时，请稍后重试')
    } else {
      alert('检测失败，请重试')
    }
  } finally {
    runningDetection.value = false
  }
}

const loadDetectionStats = async () => {
  try {
    const response = await api.getDetectionStats()
    detectionStats.value = response.data || response
  } catch (error) {
    console.error('加载检测统计失败:', error)
  }
}

const analyzingUser = ref(false)

const analyzeUser = async (userId) => {
  // 防止重复点击
  if (analyzingUser.value) {
    return
  }
  
  analyzingUser.value = true
  try {
    const response = await api.analyzeUser(userId, detectionConfig.analysis_days)
    userAnalysisData.value = response.data || response
    showUserAnalysis.value = true
  } catch (error) {
    console.error('分析用户失败:', error)
    if (error.code === 'ECONNABORTED') {
      alert('分析请求超时，请稍后重试')
    } else {
      alert('分析用户失败，请重试')
    }
  } finally {
    analyzingUser.value = false
  }
}


// 显示待认证用户商家详情
const showPendingUserMerchantDetails = async (user) => {
  try {
    selectedPendingUser.value = user
    const response = await api.getUserMerchantInfo(user.id)
    selectedPendingUserMerchant.value = response.data || response
    showPendingUserMerchantDetailModal.value = true
  } catch (error) {
    console.error('获取商家信息失败:', error)
    alert('获取商家信息失败，请重试')
  }
}

// 通过待认证用户
const approvePendingVerificationUser = async (user) => {
  if (!confirm(`确定要通过用户"${user.username}"的认证吗？`)) {
    return
  }
  
  try {
    await api.approvePendingVerificationUser(user.id)
    alert('用户已通过认证')
    // 从待认证用户列表中移除
    pendingVerificationUsers.value = pendingVerificationUsers.value.filter(u => u.id !== user.id)
    // 关闭模态框
    showPendingUserMerchantDetailModal.value = false
  } catch (error) {
    console.error('通过认证失败:', error)
    alert('操作失败，请重试')
  }
}

// 显示拒绝待认证用户模态框
const showRejectPendingUserModalFunc = (user) => {
  selectedPendingUser.value = user
  rejectReason.value = ''
  showRejectPendingUserModal.value = true
}

// 拒绝待认证用户
const rejectPendingVerificationUser = async () => {
  if (!selectedPendingUser.value) return
  
  try {
    await api.rejectPendingVerificationUser(selectedPendingUser.value.id, rejectReason.value)
    alert('用户已被拒绝')
    // 从待认证用户列表中移除
    pendingVerificationUsers.value = pendingVerificationUsers.value.filter(u => u.id !== selectedPendingUser.value.id)
    // 关闭模态框
    showRejectPendingUserModal.value = false
    showPendingUserMerchantDetailModal.value = false
  } catch (error) {
    console.error('拒绝认证失败:', error)
    alert('操作失败，请重试')
  }
}

// 商家管理子标签页相关方法
const changeMerchantSubTab = (tab) => {
  merchantSubTab.value = tab
  if (tab === 'certified') {
    loadCertifiedMerchants(true)
  } else if (tab === 'pending_verification') {
    loadPendingVerificationUsers(true)
  } else if (tab === 'applications') {
    loadMerchantApplications(true)
  }
}

const loadCertifiedMerchants = async (reset = false) => {
  if (loading.merchants || loadingMoreMerchants.value) return
  if (reset) {
    merchantPage.value = 1
    hasMoreMerchants.value = true
    merchants.value = []
  }
  if (!hasMoreMerchants.value) return
  loading.merchants = merchantPage.value === 1
  loadingMoreMerchants.value = merchantPage.value > 1
  try {
    const params = {
      skip: (merchantPage.value - 1) * merchantLimit,
      limit: merchantLimit
    }
    if (merchantFilters.search) params.search = merchantFilters.search
    // 只显示已认证的商家
    params.status = 'approved'
    const response = await api.getAllMerchants(params)
    const merchantsData = response.data.data || response.data || []
    if (merchantPage.value === 1) {
      merchants.value = merchantsData
    } else {
      merchants.value.push(...merchantsData)
    }
    // 使用后端返回的has_more字段判断是否还有更多数据
    if (response.data.has_more === false || merchantsData.length < merchantLimit) {
      hasMoreMerchants.value = false
    } else {
      merchantPage.value++
    }
  } catch (error) {
    console.error('获取认证商家列表失败:', error)
    alert('获取认证商家列表失败')
  } finally {
    loading.merchants = false
    loadingMoreMerchants.value = false
  }
}

const loadPendingVerificationUsers = async (reset = false) => {
  if (loading.pendingVerificationUsers || loadingMorePendingVerificationUsers.value) return
  if (reset) {
    pendingVerificationPage.value = 1
    hasMorePendingVerificationUsers.value = true
    pendingVerificationUsers.value = []
  }
  if (!hasMorePendingVerificationUsers.value) return
  loading.pendingVerificationUsers = pendingVerificationPage.value === 1
  loadingMorePendingVerificationUsers.value = pendingVerificationPage.value > 1
  
  try {
    const response = await api.getPendingVerificationUsers({
      skip: (pendingVerificationPage.value - 1) * pendingVerificationLimit.value,
      limit: pendingVerificationLimit.value,
      search: pendingVerificationFilters.search
    })
    
    const usersData = response.data.data || []
    
    // 判断是否还有更多数据
    if (usersData.length < pendingVerificationLimit.value) {
      hasMorePendingVerificationUsers.value = false
    }
    
    if (reset) {
      pendingVerificationUsers.value = usersData
    } else {
      pendingVerificationUsers.value = [...pendingVerificationUsers.value, ...usersData]
    }
    
    // 只有在有更多数据时才增加页码
    if (hasMorePendingVerificationUsers.value) {
      pendingVerificationPage.value += 1
    }
  } catch (error) {
    console.error('加载待认证用户失败:', error)
    alert('加载失败，请重试')
  } finally {
    loading.pendingVerificationUsers = false
    loadingMorePendingVerificationUsers.value = false
  }
}

const updateDefaultDisplayFrequency = async () => {
  if (defaultDisplayFrequency.value < 1 || defaultDisplayFrequency.value > 20) {
    alert('展示频率必须在1-20之间')
    return
  }
  
  try {
    await api.updateDefaultDisplayFrequency(defaultDisplayFrequency.value)
    alert('默认展示频率已更新')
  } catch (error) {
    console.error('更新默认展示频率失败:', error)
    alert('更新失败')
  }
}

// 加载默认展示频率
const loadDefaultDisplayFrequency = async () => {
  try {
    const response = await api.getDefaultDisplayFrequency()
    defaultDisplayFrequency.value = response.data.frequency || 5
  } catch (error) {
    console.error('获取默认展示频率失败:', error)
  }
}

// 商家认证申请相关方法
const loadMerchantApplications = async (reset = false) => {
  if (loading.merchantApplications || loadingMoreMerchantApplications.value) return
  if (reset) {
    merchantApplicationPage.value = 1
    hasMoreMerchantApplications.value = true
    merchantApplications.value = []
  }
  if (!hasMoreMerchantApplications.value) return
  loading.merchantApplications = merchantApplicationPage.value === 1
  loadingMoreMerchantApplications.value = merchantApplicationPage.value > 1
  
  try {
    const params = {
      skip: (merchantApplicationPage.value - 1) * merchantApplicationLimit.value,
      limit: merchantApplicationLimit.value
    }
    if (merchantApplicationFilters.search) params.search = merchantApplicationFilters.search
    // 显示申请中的商家（用户提交的认证申请）和已拒绝的申请
    if (merchantApplicationFilters.status) {
      params.status = merchantApplicationFilters.status
    } else {
      // 如果没有选择特定状态，显示pending和rejected状态
      // 这里我们需要修改API调用逻辑，暂时只显示pending
      params.status = 'pending'
    }
    
    const response = await api.getAllMerchants(params)
    const applicationsData = response.data.data || response.data || []
    
    if (merchantApplicationPage.value === 1) {
      merchantApplications.value = applicationsData
    } else {
      merchantApplications.value.push(...applicationsData)
    }
    
    // 使用后端返回的has_more字段判断是否还有更多数据
    if (response.data.has_more === false || applicationsData.length < merchantApplicationLimit.value) {
      hasMoreMerchantApplications.value = false
    } else {
      merchantApplicationPage.value++
    }
  } catch (error) {
    console.error('获取商家认证申请失败:', error)
    alert('获取商家认证申请失败')
  } finally {
    loading.merchantApplications = false
    loadingMoreMerchantApplications.value = false
  }
}

const showMerchantApplicationDetails = (application) => {
  selectedMerchant.value = application
  showMerchantDetailModal.value = true
}

const approveMerchantApplication = async (application) => {
  if (!confirm(`确定要通过商家"${application.business_name}"的认证申请吗？`)) {
    return
  }
  
  try {
    await api.approveMerchant(application.id)
    application.status = 'approved'
    alert('商家认证已通过')
    loadMerchantApplications(true)
  } catch (error) {
    console.error('通过商家认证失败:', error)
    alert('操作失败')
  }
}

const showRejectMerchantApplicationModal = (application) => {
  selectedMerchant.value = application
  rejectReason.value = ''
  showRejectMerchantModal.value = true
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


.admin-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.admin-tabs button {
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 100px;
  justify-content: center;
  font-size: 13px;
  white-space: nowrap;
}

.admin-tabs button:hover {
  background: #f8f9fa;
  border-radius: 4px;
}

.admin-tabs button.active {
  border-bottom-color: #3498db;
  color: #3498db;
  background: #f0f8ff;
  border-radius: 4px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.merchant-frequency-settings {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.merchant-frequency-settings label {
  font-weight: 500;
  color: #495057;
  margin: 0;
}

.frequency-input {
  width: 60px !important;
  margin: 0 !important;
  text-align: center;
}

.merchant-frequency-settings span {
  color: #6c757d;
  font-size: 14px;
  white-space: nowrap;
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

.btn-secondary {
  background: #6c757d;
  color: white;
  border: 1px solid #6c757d;
}

.btn-secondary:hover {
  background: #5a6268;
  border-color: #545b62;
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
  
  .merchant-frequency-settings {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .merchant-frequency-settings span {
    font-size: 13px;
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

/* AI策略样式 */
.ai-report-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* 商家管理样式 */
.merchant-settings-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
}

.merchant-settings-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.setting-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* 商家识别样式 */
.merchant-identification-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
}

/* 商贩检测设置样式 */
.merchant-detection-settings {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.merchant-detection-settings h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.detection-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group label {
  font-weight: 600;
  color: #555;
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group input[type="number"] {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 100px;
}

.control-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 8px;
}

.control-group span {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.control-actions {
  grid-column: 1 / -1;
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  margin-top: 10px;
}

.detection-stats {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  margin-top: 20px;
}

.detection-stats h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}


.stat-value {
  font-weight: 600;
  color: #333;
}

.stat-value.active {
  color: #28a745;
}

.stat-value.inactive {
  color: #dc3545;
}

/* 商贩检测页面样式 */
.detection-status {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-indicator {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: #dc3545;
  color: white;
}

.status-indicator.active {
  background: #28a745;
}

.detection-history {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #e9ecef;
}

.detection-history h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.history-info {
  color: #666;
  line-height: 1.6;
}

.history-info p {
  margin: 8px 0;
}

/* 检测结果样式 */
.detection-results {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  max-height: 420px;
  overflow: auto;
}

.detection-results h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.results-table {
  overflow-x: auto;
}

.results-table table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.results-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.ai-judgment {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.ai-judgment.merchant {
  background: #ffebee;
  color: #c62828;
}

.ai-judgment.normal {
  background: #e8f5e8;
  color: #2e7d32;
}

/* 用户分析模态框样式 */
.user-analysis-modal .modal-content {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.analysis-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.analysis-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item label {
  font-weight: 600;
  color: #666;
  min-width: 80px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border: 1px solid #e9ecef;
}


.ai-result {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.ai-judgment-large {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.ai-judgment-large.merchant {
  background: #ffebee;
  color: #c62828;
  border: 2px solid #ffcdd2;
}

.ai-judgment-large.normal {
  background: #e8f5e8;
  color: #2e7d32;
  border: 2px solid #c8e6c9;
}

.confidence-bar {
  margin-bottom: 15px;
}

.confidence-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.confidence-progress {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ffa500, #32cd32);
  transition: width 0.3s ease;
}

.ai-reason,
.ai-evidence {
  margin-top: 15px;
}

.ai-reason strong,
.ai-evidence strong {
  color: #333;
  display: block;
  margin-bottom: 8px;
}

.ai-reason p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.ai-evidence ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.ai-evidence li {
  margin-bottom: 5px;
}

/* 检测历史样式 */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.history-table {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  max-height: 420px;
  overflow: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.history-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.load-more-container {
  text-align: center;
  padding: 20px;
  border-top: 1px solid #eee;
}

.no-more-data {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 14px;
}

.user-info-small {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e9ecef;
}

.user-details-small {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.username-small {
  font-weight: 600;
  color: #333;
  font-size: 13px;
}

.user-id-small {
  font-size: 11px;
  color: #666;
}

.ai-judgment-small {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.ai-judgment-small.merchant {
  background: #ffebee;
  color: #c62828;
}

.ai-judgment-small.normal {
  background: #e8f5e8;
  color: #2e7d32;
}

.detection-type {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.detection-type.manual {
  background: #e3f2fd;
  color: #1976d2;
}

.detection-type.auto {
  background: #f3e5f5;
  color: #7b1fa2;
}

.processed-status {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  background: #fff3e0;
  color: #f57c00;
}

.processed-status.processed {
  background: #e8f5e8;
  color: #2e7d32;
}

.no-history {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

/* 检测结果表格增强样式 */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e9ecef;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.user-email {
  font-size: 12px;
  color: #666;
}

.item-count {
  font-size: 16px;
  font-weight: bold;
  color: #007bff;
}

.item-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}

.item-stats small {
  color: #666;
  font-size: 11px;
}

.confidence-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 80px;
}

.confidence-value {
  font-weight: 600;
  color: #333;
  font-size: 13px;
}

.confidence-bar-small {
  width: 100%;
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.confidence-fill-small {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ffa500, #32cd32);
  transition: width 0.3s ease;
  border-radius: 2px;
}

.merchant-identification-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.identification-controls {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-user {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-user label {
  font-weight: 500;
  color: #555;
  min-width: 80px;
}

.search-user input {
  flex: 1;
  min-width: 200px;
}

.search-results {
  margin-top: 16px;
}

.search-results-header {
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.search-results-header h4 {
  margin: 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
}

.search-results-list {
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  scrollbar-width: thin;
  scrollbar-color: #ccc #f5f5f5;
}

.search-results-list::-webkit-scrollbar {
  width: 6px;
}

.search-results-list::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.search-results-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.search-results-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.user-result {
  background: white;
  border-bottom: 1px solid #eee;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  min-height: 100px;
}

.user-result:last-child {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 16px;
}

.user-details p {
  margin: 2px 0;
  color: #666;
  font-size: 14px;
}

.user-status {
  margin-top: 8px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.danger {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.active {
  background: #d4edda;
  color: #155724;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.inactive {
  background: #e2e3e5;
  color: #6c757d;
}

.user-actions {
  flex-shrink: 0;
}

/* 商家管理子标签页样式 */
.merchant-sub-tabs {
  margin-bottom: 20px;
}

.sub-tab-nav {
  display: flex;
  border-bottom: 2px solid #e9ecef;
  margin-bottom: 20px;
}

.sub-tab-btn {
  background: none;
  border: none;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6c757d;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sub-tab-btn:hover {
  color: #495057;
  background-color: #f8f9fa;
}

.sub-tab-btn.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background-color: #f8f9fa;
}

.sub-tab-content {
  min-height: 400px;
}

/* 待认证用户表格样式 */
.pending-verification-table {
  border: 1px solid #ddd;
  border-radius: 8px;
}

.pending-verification-table table {
  width: 100%;
  border-collapse: collapse;
}

.pending-verification-table th,
.pending-verification-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.pending-verification-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  position: sticky;
  top: 0;
  z-index: 10;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.user-id {
  font-size: 12px;
  color: #6c757d;
}

.contact-info {
  font-size: 14px;
  color: #666;
}

.contact-info div {
  margin-bottom: 2px;
}

.setting-controls label {
  font-weight: 500;
  color: #333;
  margin: 0;
}

.merchants-table {
  overflow-x: auto;
}

.merchants-table table {
  min-width: 900px;
}

.user-id {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.merchant-detail-modal {
  max-width: 600px;
}

.merchant-detail {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-row label {
  font-weight: 500;
  color: #333;
  min-width: 100px;
  margin: 0;
}

.detail-row span {
  color: #666;
  flex: 1;
  word-break: break-word;
}

.reject-reason {
  color: #e74c3c !important;
  font-style: italic;
}

.warning-message {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 12px;
  margin-top: 15px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.warning-message i {
  color: #f39c12;
  margin-top: 2px;
  flex-shrink: 0;
}

.warning-message p {
  margin: 0;
  color: #856404;
  font-size: 14px;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .setting-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 5px;
  }
  
  .detail-row label {
    min-width: auto;
  }
}
.tab-content {
  padding-bottom: 20px;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.merchant-actions {
  display: flex;
  gap: 5px;
  margin-top: 5px;
}

.merchant-actions .btn {
  font-size: 12px;
  padding: 4px 8px;
}
.users-table,
.items-table,
.merchants-table,
.buy-requests-table,
.messages-table {
  overflow-x: auto;
}
.users-table table,
.items-table table,
.merchants-table table,
.buy-requests-table table,
.messages-table table {
  min-width: 900px;
}
/* AI推荐管理样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #42b983, #3aa776);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}


.behavior-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.behavior-badge.view {
  background: #42b983;
}

.behavior-badge.click {
  background: #f56c6c;
}

.behavior-badge.favorite {
  background: #e74c3c;
}

.behavior-badge.like {
  background: #f39c12;
}

.behavior-badge.search {
  background: #9b59b6;
}

.behavior-data {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  color: #666;
}

.test-controls {
  display: flex;
  gap: 20px;
  align-items: end;
  margin-bottom: 20px;
}

.test-controls .form-group {
  flex: 1;
}

.test-result {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.test-result h4 {
  margin-bottom: 15px;
  color: #333;
}

.result-content {
  background: white;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
}

.result-content pre {
  margin: 0;
  font-size: 12px;
  line-height: 1.4;
}

.large-modal .modal-content {
  max-width: 800px;
  width: 90%;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-row .form-group {
  margin-bottom: 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .tab-content {
    /* 移除高度限制，让内容自然滚动 */
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .test-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* 用户搜索相关样式 */
.user-search-results {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 行为记录内容区域 */
.behavior-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.table-container {
  flex: 1;
  min-width: 0;
}

/* 行为表格限定高度并滚动 */
.behavior-table-container {
  max-height: 500px;
  overflow: auto;
}

/* 已选择用户侧边栏 */
.selected-users-sidebar {
  width: 300px;
  min-width: 300px;
  background: #e8f5e8;
  border-radius: 8px;
  border: 1px solid #c3e6c3;
  padding: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.selected-users-sidebar h4 {
  margin: 0 0 15px 0;
  color: #2d5a2d;
  font-size: 16px;
  border-bottom: 1px solid #c3e6c3;
  padding-bottom: 10px;
}

.no-selected-users {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 20px 0;
}

.no-selected-users p {
  margin: 0;
}

.user-search-results h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 16px;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}

.user-list::-webkit-scrollbar {
  width: 6px;
}

.user-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.user-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.user-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.user-email {
  color: #666;
  font-size: 12px;
}

.selected-users {
  margin: 20px 0;
  padding: 15px;
  background: #e8f5e8;
  border-radius: 8px;
  border: 1px solid #c3e6c3;
}

.selected-users h4 {
  margin: 0 0 15px 0;
  color: #2d5a2d;
  font-size: 16px;
}

.selected-user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}

.selected-user-list::-webkit-scrollbar {
  width: 6px;
}

.selected-user-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.selected-user-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.selected-user-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.selected-user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #c3e6c3;
}

.selected-user-item.active {
  border-color: #42b983;
  box-shadow: 0 0 0 2px rgba(66,185,131,0.15);
}

.test-user-info {
  min-height: 40px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.no-users {
  color: #666;
  font-style: italic;
}

.test-user-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.test-user-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border-radius: 20px;
  border: 1px solid #ddd;
  font-size: 14px;
}

/* AI推荐测试结果样式 */
.test-result {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.test-result h4 {
  margin: 0;
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  color: #333;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px;
}

.recommendation-card {
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  transition: all 0.2s;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #007bff;
}

.item-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.item-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s;
}

.recommendation-card:hover .item-thumbnail {
  transform: scale(1.05);
}

.item-details {
  padding: 15px;
  flex: 1;
}

.item-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-category {
  margin: 0 0 5px 0;
  font-size: 12px;
  color: #666;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
}

.item-price {
  margin: 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #e74c3c;
}

.item-condition {
  margin: 0 0 15px 0;
  font-size: 12px;
  color: #666;
}

.item-actions {
  padding: 0 15px 15px 15px;
}

.item-actions .btn {
  width: 100%;
  justify-content: center;
}

.no-recommendations {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.no-recommendations p {
  margin: 0;
  font-size: 16px;
}

/* 商品选择范围配置样式 */
.config-section {
  margin-top: 20px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 弹窗内的配置样式 */
.modal-body .config-content {
  padding: 0;
}

.modal-body .config-tabs {
  margin-bottom: 0;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.modal-body .tab-content {
  padding: 20px 0;
  max-height: 400px;
  overflow-y: auto;
}

.modal-body .sort-configs,
.modal-body .category-configs,
.modal-body .general-configs {
  max-height: 350px;
  overflow-y: auto;
}

.config-section h3 {
  margin: 0;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  color: #333;
  font-size: 18px;
}

.config-content {
  padding: 0;
}

.config-tabs {
  display: flex;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.tab-btn {
  flex: 1;
  padding: 15px 20px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-btn:hover {
  background: #e9ecef;
  color: #333;
}

.tab-btn.active {
  background: white;
  color: #007bff;
  border-bottom-color: #007bff;
  font-weight: 600;
}

.tab-content {
  padding: 30px;
}

.config-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.config-header h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.config-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.sort-configs,
.category-configs,
.general-configs {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sort-config-item,
.category-config-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.config-row {
  display: flex;
  gap: 30px;
  align-items: center;
}

.config-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-field label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-field input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #007bff;
}

.config-field input[type="number"] {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 100px;
}

.config-field input[type="number"]:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.general-configs .config-row {
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
}

.general-configs .config-field {
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.general-configs .config-field label {
  margin: 0;
  white-space: nowrap;
}

.general-configs .config-field input[type="number"] {
  width: 150px;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .config-field {
    width: 100%;
  }
  
  .config-field input[type="number"] {
    width: 100%;
    max-width: 200px;
  }
  
  .general-configs .config-field {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .user-item,
  .selected-user-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .user-info {
    width: 100%;
  }
  
  .behavior-content {
    flex-direction: column;
  }
  
  .selected-users-sidebar {
    width: 100%;
    min-width: auto;
    max-height: 300px;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
    gap: 15px;
    padding: 15px;
  }
  
  .recommendation-card {
    margin-bottom: 0;
  }
}

/* 商品管理头部操作样式 */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.header-actions .filters {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.header-actions .action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 优化滚动体验 */
.admin-container {
  overflow-x: hidden;
  min-height: 100vh;
}

/* 让内容自然滚动，移除不必要的滚动条限制 */
.tab-content {
  min-height: auto;
}

/* 表格容器优化 */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 保持必要的水平滚动条用于宽表格 */
.users-table,
.items-table,
.buy-requests-table,
.merchants-table,
.messages-table {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 排序配置模态框样式 */
.large-modal {
  max-width: 90vw;
  width: 1200px;
}

.sorting-config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.config-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.config-card h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
}

.config-item {
  margin-bottom: 15px;
}

.config-item:last-child {
  margin-bottom: 0;
}

.config-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
}

.config-item small {
  color: #6c757d;
  font-size: 12px;
}

.sorting-status-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
  margin-top: 20px;
}

.sorting-status-section h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.status-label {
  font-weight: 500;
  color: #495057;
}

.status-value {
  color: #007bff;
  font-weight: 600;
}

.status-running {
  color: #28a745 !important;
  font-weight: 600;
}

/* 排序历史记录样式 */
.sorting-history-section {
  margin-top: 30px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.sorting-history-section h4 {
  margin: 0 0 20px 0;
  color: #495057;
  font-size: 18px;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
}

.history-controls {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.history-table {
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.history-table th,
.history-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.history-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
}

.history-table td {
  color: #6c757d;
  font-size: 14px;
}

.history-table tbody tr:hover {
  background: #f8f9fa;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: #d4edda;
  color: #155724;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.sorting-config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.config-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.config-card h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 8px;
}

.config-item {
  margin-bottom: 15px;
}

.config-item:last-child {
  margin-bottom: 0;
}

.config-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.config-item input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.config-item input:focus {
  outline: 0;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.config-item small {
  display: block;
  margin-top: 4px;
  color: #6c757d;
  font-size: 12px;
}

.sorting-status-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.sorting-status-section h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 8px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.status-label {
  font-weight: 500;
  color: #495057;
  font-size: 14px;
}

.status-value {
  color: #007bff;
  font-weight: 600;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sorting-config-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
  
  .section-actions {
    flex-direction: column;
  }
  
  .sorting-settings-section .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>