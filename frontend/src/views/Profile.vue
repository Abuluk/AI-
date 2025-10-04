<template>
  <div class="container">
    <!-- 用户头部信息 -->
    <div class="profile-header card">
      <div class="user-info">
        <div class="avatar-container">
          <!-- 头像上传区域 -->
          <div class="avatar-wrapper" :class="{ 'loading': avatarLoading }">
            <img :src="avatarUrl" class="user-avatar" @error="handleImageError">
            <div class="avatar-overlay" v-if="avatarLoading">
              <i class="fas fa-spinner fa-spin"></i>
            </div>
          </div>
          <label for="avatar-upload" class="avatar-edit">
            <i class="fas fa-camera"></i>
            <input 
              id="avatar-upload" 
              type="file" 
              accept="image/*" 
              @change="handleAvatarUpload($event, false)"
              hidden
            >
          </label>
          
          <!-- 头像上传进度 -->
          <div v-if="avatarUploadProgress > 0" class="upload-progress">
            <div class="progress-bar" :style="{ width: avatarUploadProgress + '%' }"></div>
            <span>{{ avatarUploadProgress }}%</span>
          </div>
          
          <!-- 头像上传错误提示 -->
          <div v-if="avatarError" class="avatar-error">
            <i class="fas fa-exclamation-triangle"></i> {{ avatarError }}
          </div>
        </div>
        
        <div class="user-details">
          <h2 class="username">{{ user.username }}</h2>
          <p class="user-bio">{{ user.bio || '这个人很懒，什么都没留下' }}</p>
          
          <!-- 商家状态显示 -->
          <div class="merchant-status" v-if="user.is_merchant || user.is_pending_merchant">
            <div class="status-badge" :class="getMerchantStatusClass()">
              <i class="fas fa-store"></i>
              {{ getMerchantStatusText() }}
            </div>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <strong>{{ user.followers || 0 }}</strong>
              <span>粉丝</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.following || 0 }}</strong>
              <span>关注</span>
            </div>
            <div class="stat-item">
              <strong>{{ user.items_count || 0 }}</strong>
              <span>商品</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="profile-actions">
        <button class="btn btn-outline" @click="openEditModal">
          <i class="fas fa-edit"></i> 编辑资料
        </button>
        
        <!-- 商家认证按钮 -->
        <button 
          v-if="!user.is_merchant && !user.is_pending_merchant && !user.is_pending_verification" 
          class="btn btn-primary" 
          @click="openMerchantModal"
        >
          <i class="fas fa-store"></i> 申请商家认证
        </button>
        
        <div v-else-if="user.is_pending_merchant" class="merchant-status-buttons">
          <button class="btn btn-warning" @click="openMerchantModal">
            <i class="fas fa-clock"></i> 查看认证状态
          </button>
          <button class="btn btn-sm btn-outline-danger ml-2" @click="cancelApplication">
            <i class="fas fa-times"></i> 取消申请
          </button>
        </div>
        
        <div v-else-if="user.is_merchant" class="merchant-status-buttons">
          <button class="btn btn-success" @click="openMerchantModal">
            <i class="fas fa-store"></i> 商家中心
          </button>
          <button class="btn btn-sm btn-outline-danger ml-2" @click="openCancelMerchantModal">
            <i class="fas fa-times"></i> 取消商家认证
          </button>
        </div>
        
        <button 
          v-else-if="user.is_pending_verification" 
          class="btn btn-danger" 
          @click="openMerchantModal"
        >
          <i class="fas fa-exclamation-triangle"></i> 待认证状态
        </button>
        
        <button 
          v-else-if="user.is_merchant || user.is_pending_merchant" 
          class="btn btn-success" 
          @click="openMerchantSettings"
        >
          <i class="fas fa-cog"></i> 商家设置
        </button>
      </div>
    </div>
      <!-- 修改后的按钮区域 - 添加布局类 -->
      <div class="profile-actions actions-right">
        <!-- 显示设置按钮 - 所有用户都可以设置 -->
        <button class="btn btn-outline-primary" @click="openDisplaySettings">
          <i class="fas fa-eye"></i> 显示设置
        </button>
        <button class="btn btn-primary" @click="navigateToPublish">
          <i class="fas fa-plus"></i> 上传商品
        </button>
        <button class="btn btn-outline" @click="openOfflineModal">
          <i class="fas fa-ban"></i> 已下架商品
        </button>
      </div>    
    <!-- 商品标签页 -->
    <div class="profile-tabs card">
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.id" 
          :class="{ active: activeTab === tab.id }"
          @click="changeTab(tab.id)"
        >
          {{ tab.label }}
          <span class="badge" v-if="tab.count > 0">{{ tab.count }}</span>
        </button>
      </div>
      
      <div class="tab-content">
      <!-- 在售商品标签页 -->
        <div v-if="activeTab === 'selling'">
          <div class="section-header">
           <h3>在售商品 ({{ sellingItems.length }})</h3>
            <div class="sort-controls">
              <!-- 修复排序功能：移除@change事件，改为使用计算属性 -->
              <select v-model="sorting.selling">
              <option value="newest">最新发布</option>
               <option value="popular">最受欢迎</option>
               <option value="price_asc">价格从低到高</option>
               <option value="price_desc">价格从高到低</option>
              </select>
            </div>
           </div>
          
          <div v-if="loading.selling" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="sellingItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in sortedSellingItems" 
                :key="`selling-${item.id}`" 
                :product="item" 
                :showActions="true"
                @offline="handleOfflineItem"
                @online="handleOnlineItem"
                @sold="handleSoldItem"
                @delete="handleDeleteItem"
                @edit="handleEditItem"
              >
                <span>发布时间：{{ formatDateTime(item.created_at) }}</span>
              </ProductCard>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-store-slash"></i>
              <p>暂无在售商品</p>
              <button class="btn btn-primary" @click="navigateToPublish">
                去发布商品
              </button>
            </div>
            <!-- 自动加载更多触发器，仅在还有更多数据时显示 -->
            <div v-if="sellingItems.length > 0 && hasMoreSelling" ref="infiniteScrollTrigger" style="height: 1px;"></div>
          </div>
        </div>
        
        <!-- 已售商品 -->
        <div v-if="activeTab === 'sold'">
          <div class="section-header">
            <h3>已售商品 ({{ soldItems.length }})</h3>
            <div class="sort-controls">
                <select v-model="sorting.sold" @change="fetchSoldItems(true)">
                <option value="newest">最新售出</option>
                <option value="oldest">最早售出</option>
                </select>
            </div>
          </div>
          
          <div v-if="loading.sold" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="soldItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in soldItems" 
                :key="`sold-${item.id}`" 
                :product="item" 
                :sold="true"
                :showActions="true"
                @delete="handleDeleteItem"
                @edit="handleEditItem"
              >
                <span>售出时间：{{ formatDateTime(item.soldAt) }}</span>
              </ProductCard>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-box-open"></i>
              <p>暂无已售商品</p>
            </div>
            <!-- 自动加载更多触发器，仅在还有更多数据时显示 -->
            <div v-if="soldItems.length > 0 && hasMoreSold" ref="infiniteScrollSoldTrigger" style="height: 1px;"></div>
          </div>
        </div>
        
        <!-- 收藏商品 -->
        <div v-if="activeTab === 'favorites'">
          <div class="section-header">
            <h3>收藏的商品 ({{ favoriteItems.length }})</h3>
          </div>
          
          <div v-if="loading.favorites" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="favoriteItems.length > 0" class="products-grid">
              <ProductCard 
                v-for="item in favoriteItems" 
                :key="`fav-${item.id}`" 
                :product="item" 
                :showActions="true"
                :isFavorite="true"
                @unfavorite="handleUnfavoriteItem"
                @edit="handleEditItem"
              >
                <span>收藏时间：{{ formatDateTime(item.favoritedAt) }}</span>
              </ProductCard>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-heart"></i>
              <p>暂无收藏商品</p>
              <button class="btn btn-primary" @click="navigateToDiscover">
                     去首页浏览
              </button>
            </div>
            <!-- 自动加载更多触发器，仅在还有更多数据时显示 -->
            <div v-if="favoriteItems.length > 0 && hasMoreFavorite" ref="infiniteScrollFavTrigger" style="height: 1px;"></div>
          </div>
        </div>
        <!-- 求购信息tab -->
        <div v-else-if="activeTab === 'buy_requests'" class="tab-content">
          <div class="section-header">
            <h3>我的求购</h3>
          </div>
          <div v-if="myBuyRequests.length === 0" class="empty-state">
            <i class="fas fa-shopping-cart"></i>
            <p>暂无求购信息</p>
          </div>
          <div v-else>
            <div v-for="buyRequest in myBuyRequests" :key="buyRequest.id" class="buy-request-card" @click="goToBuyRequestDetail(buyRequest.id)">
              <div class="buy-request-main">
                <img v-if="hasBuyRequestImage(buyRequest.images)" :src="getBuyRequestImage(buyRequest.images)" :alt="buyRequest.title" class="buy-request-img">
                <div class="buy-request-info">
                  <h4>{{ buyRequest.title }}</h4>
                  <div class="budget">预算：<span class="price">¥{{ buyRequest.budget }}</span></div>
                  <div class="desc">{{ buyRequest.description }}</div>
                  <div class="meta">
                    <span class="time">{{ formatDateTime(buyRequest.created_at) }}</span>
                    <span class="likes">👍 {{ buyRequest.like_count || 0 }}</span>
                  </div>
                </div>
                <div class="buy-request-actions" @click.stop>
                  <button class="btn btn-primary btn-sm" @click="handleEditBuyRequest(buyRequest.id)">编辑</button>
                  <button class="btn btn-outline btn-sm" @click="handleDeleteBuyRequest(buyRequest.id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 取消商家认证模态框 -->
    <div v-if="showCancelMerchantModal" class="modal-overlay" @click.self="closeCancelMerchantModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>取消商家认证</h3>
          <button class="modal-close" @click="closeCancelMerchantModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="warning-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>取消商家认证后，您将失去商家特权，包括商品展示频率提升等权益。您可以随时重新申请商家认证。</p>
          </div>
          
          <div class="form-group">
            <label for="cancel_reason">取消原因 *</label>
            <textarea 
              id="cancel_reason" 
              v-model="cancelMerchantReason" 
              placeholder="请说明取消商家认证的原因"
              rows="4"
              required
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeCancelMerchantModal">取消</button>
          <button 
            class="btn btn-danger" 
            @click="cancelMerchantApplication"
            :disabled="!cancelMerchantReason.trim() || cancelingMerchant"
          >
            <i class="fas fa-spinner fa-spin" v-if="cancelingMerchant"></i>
            {{ cancelingMerchant ? '提交中...' : '确认取消' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 编辑资料模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑个人资料</h3>
          <button class="modal-close" @click="closeEditModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveProfile">
            <div class="form-group avatar-form-group">
              <label>头像</label>
              <div class="avatar-edit-preview">
                <img :src="editForm.avatarPreview" class="preview-image">
                <label for="edit-avatar-upload" class="avatar-edit-btn">
                  <i class="fas fa-camera"></i> 更换
                  <input 
                    id="edit-avatar-upload" 
                    type="file" 
                    accept="image/*" 
                    @change="handleAvatarFileChange"
                    hidden
                  >
                </label>
              </div>
            </div>

            <div class="form-group">
              <label for="username">用户名</label>
              <input id="username" type="text" v-model="editForm.username" required>
            </div>
            <div class="form-group">
              <label for="bio">个人简介</label>
              <textarea id="bio" v-model="editForm.bio" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label for="location">所在地区</label>
              <input id="location" type="text" v-model="editForm.location">
            </div>
            <div class="form-group">
              <label for="contact">联系方式</label>
              <input id="contact" type="text" v-model="editForm.contact">
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="closeEditModal">取消</button>
          <button type="button" class="btn btn-primary" @click="saveProfile" :disabled="savingProfile">
            <span v-if="savingProfile">保存中...</span>
            <span v-else>保存</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 已下架商品模态框 -->
    <div v-if="showOfflineModal" class="modal-overlay" @click.self="closeOfflineModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>已下架商品</h3>
          <button class="modal-close" @click="closeOfflineModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="loading.offline" class="loading-state">
            <div class="skeleton-card" v-for="n in 4" :key="n"></div>
          </div>
          
          <div v-else>
            <div v-if="offlineItems.length > 0" class="offline-items-grid">
              <div v-for="item in offlineItems" :key="`offline-${item.id}`" class="offline-item">
                <img :src="getFirstImage(item)" :alt="item.title" class="item-image">
                <div class="item-info">
                  <h4>{{ item.title }}</h4>
                  <p class="price">¥{{ item.price }}</p>
                  <p class="status">已下架</p>
                </div>
                <div class="item-actions">
                  <button class="btn btn-success btn-sm" @click="handleOnlineItem(item.id)">
                    <i class="fas fa-check"></i> 重新上架
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-box-open"></i>
              <p>暂无已下架商品</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeOfflineModal">关闭</button>
        </div>
      </div>
    </div>
    
    <!-- 商家认证模态框 -->
    <div v-if="showMerchantModal" class="modal-overlay" @click.self="closeMerchantModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ getMerchantModalTitle() }}</h3>
          <button class="modal-close" @click="closeMerchantModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- 待定商家状态显示（申请中） -->
          <div v-if="user.is_pending_merchant" class="merchant-status-info">
            <div class="status-pending">
              <i class="fas fa-clock"></i>
              <h4>认证审核中</h4>
              <p>您的商家认证申请正在审核中，请耐心等待管理员审核。</p>
              <div class="status-tips">
                <p><i class="fas fa-check-circle"></i> 您可以正常发布和管理商品</p>
                <p><i class="fas fa-info-circle"></i> 审核通过后即可享受商家特权</p>
              </div>
            </div>
          </div>
          
          <!-- 待认证状态显示和表单 -->
          <div v-else-if="user.is_pending_verification" class="merchant-status-info">
            <div class="status-pending-verification">
              <i class="fas fa-exclamation-triangle"></i>
              <h4>待认证状态</h4>
              <p>管理员判定您为商家，需要完成认证才能解除此状态。</p>
              <div class="status-tips">
                <p><i class="fas fa-info-circle"></i> 您的所有商品已自动下架</p>
                <p><i class="fas fa-info-circle"></i> 无法发布新商品</p>
                <p><i class="fas fa-info-circle"></i> 请填写以下信息完成认证</p>
              </div>
            </div>
            
            <!-- 待认证用户填写表单 -->
            <div class="merchant-verification-form">
              <h4>完善商家信息</h4>
              <form @submit.prevent="submitMerchantVerification">
                <div class="form-group">
                  <label for="verification_business_name">店铺名称 *</label>
                  <input 
                    id="verification_business_name" 
                    type="text" 
                    v-model="verificationForm.business_name" 
                    placeholder="请输入店铺名称"
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label for="verification_contact_person">联系人姓名 *</label>
                  <input 
                    id="verification_contact_person" 
                    type="text" 
                    v-model="verificationForm.contact_person" 
                    placeholder="请输入联系人姓名"
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label for="verification_contact_phone">联系电话 *</label>
                  <input 
                    id="verification_contact_phone" 
                    type="tel" 
                    v-model="verificationForm.contact_phone" 
                    placeholder="请输入联系电话"
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label for="verification_business_address">店铺地址 *</label>
                  <input 
                    id="verification_business_address" 
                    type="text" 
                    v-model="verificationForm.business_address" 
                    placeholder="请输入店铺地址"
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label for="verification_business_license">营业执照号（可选）</label>
                  <input 
                    id="verification_business_license" 
                    type="text" 
                    v-model="verificationForm.business_license" 
                    placeholder="请输入营业执照号"
                  >
                </div>
                
                <div class="form-group">
                  <label for="verification_business_description">店铺描述</label>
                  <textarea 
                    id="verification_business_description" 
                    v-model="verificationForm.business_description" 
                    placeholder="请简单描述您的店铺特色"
                    rows="3"
                  ></textarea>
                </div>
              </form>
            </div>
          </div>
          
          <!-- 申请商家认证表单 -->
          <div v-else class="merchant-application-form">
            <form @submit.prevent="submitMerchantApplication">
              <div class="form-group">
                <label for="business_name">店铺名称 *</label>
                <input 
                  id="business_name" 
                  type="text" 
                  v-model="merchantForm.business_name" 
                  placeholder="请输入店铺名称"
                  required
                >
              </div>
              
              <div class="form-group">
                <label for="contact_person">联系人姓名 *</label>
                <input 
                  id="contact_person" 
                  type="text" 
                  v-model="merchantForm.contact_person" 
                  placeholder="请输入联系人姓名"
                  required
                >
              </div>
              
              <div class="form-group">
                <label for="contact_phone">联系电话 *</label>
                <input 
                  id="contact_phone" 
                  type="tel" 
                  v-model="merchantForm.contact_phone" 
                  placeholder="请输入联系电话"
                  required
                >
              </div>
              
              <div class="form-group">
                <label for="business_address">店铺地址 *</label>
                <input 
                  id="business_address" 
                  type="text" 
                  v-model="merchantForm.business_address" 
                  placeholder="请输入店铺地址"
                  required
                >
              </div>
              
              <div class="form-group">
                <label for="business_license">营业执照号（可选）</label>
                <input 
                  id="business_license" 
                  type="text" 
                  v-model="merchantForm.business_license" 
                  placeholder="请输入营业执照号"
                >
              </div>
              
              <div class="form-group">
                <label for="business_description">店铺描述</label>
                <textarea 
                  id="business_description" 
                  v-model="merchantForm.business_description" 
                  placeholder="请简单描述您的店铺特色"
                  rows="3"
                ></textarea>
              </div>
              
              <div class="form-tips">
                <p><i class="fas fa-info-circle"></i> 申请商家认证后，您将获得以下权益：</p>
                <ul>
                  <li>商品展示频率提升</li>
                  <li>专属商家标识</li>
                  <li>更多营销工具</li>
                </ul>
              </div>
            </form>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeMerchantModal">
            {{ user.is_pending_merchant ? '关闭' : '取消' }}
          </button>
          <button 
            v-if="!user.is_pending_merchant && !user.is_pending_verification" 
            class="btn btn-primary" 
            @click="submitMerchantApplication"
            :disabled="submittingMerchant"
          >
            <span v-if="submittingMerchant">提交中...</span>
            <span v-else>提交申请</span>
          </button>
          <button 
            v-if="user.is_pending_verification" 
            class="btn btn-primary" 
            @click="submitMerchantVerification"
            :disabled="submittingMerchant"
          >
            <span v-if="submittingMerchant">提交中...</span>
            <span v-else>提交申请</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 显示设置模态框 - 所有用户都可以设置 -->
    <div v-if="showDisplaySettingsModal" class="modal-overlay" @click.self="closeDisplaySettingsModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>显示设置</h3>
          <button class="modal-close" @click="closeDisplaySettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="display-settings">
            <div class="setting-group">
              <h4>商品展示设置</h4>
              <div class="form-group">
                <label for="display_frequency">商家商品展示频率</label>
                <select id="display_frequency" v-model="displaySettings.display_frequency">
                  <option value="3">每3个普通商品展示1个商家商品</option>
                  <option value="5">每5个普通商品展示1个商家商品</option>
                  <option value="10">每10个普通商品展示1个商家商品</option>
                </select>
                <p class="form-hint">此设置仅影响您看到的商品展示顺序</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeDisplaySettingsModal">取消</button>
          <button class="btn btn-primary" @click="saveDisplaySettings" :disabled="savingSettings">
            <span v-if="savingSettings">保存中...</span>
            <span v-else>保存设置</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 商家设置模态框 -->
    <div v-if="showMerchantSettingsModal" class="modal-overlay" @click.self="closeMerchantSettingsModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>商家设置</h3>
          <button class="modal-close" @click="closeMerchantSettingsModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="merchant-settings">
            <div class="setting-group">
              <h4>商家信息</h4>
              <div v-if="!isEditingMerchant" class="merchant-info">
                <!-- 状态显示 -->
                <div class="merchant-status-display">
                  <span class="status-badge" :class="getMerchantStatusClass()">
                    <i class="fas fa-store"></i>
                    {{ getMerchantStatusText() }}
                  </span>
                  <p v-if="user.is_pending_merchant" class="status-note">
                    <i class="fas fa-info-circle"></i>
                    您的商家信息已修改，正在等待管理员重新审核
                  </p>
                </div>
                
                <p><strong>店铺名称：</strong>{{ merchantInfo.business_name }}</p>
                <p><strong>联系人：</strong>{{ merchantInfo.contact_person }}</p>
                <p><strong>联系电话：</strong>{{ merchantInfo.contact_phone }}</p>
                <p><strong>店铺地址：</strong>{{ merchantInfo.business_address }}</p>
                <p v-if="merchantInfo.business_description"><strong>店铺描述：</strong>{{ merchantInfo.business_description }}</p>
                <div class="action-buttons">
                  <button @click="startEditMerchant" class="btn btn-primary">
                    <i class="fas fa-edit"></i> 修改信息
                  </button>
                </div>
              </div>
              
              <div v-else class="merchant-edit-form">
                <div class="form-group">
                  <label>店铺名称：</label>
                  <input v-model="editMerchantForm.business_name" type="text" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>联系人：</label>
                  <input v-model="editMerchantForm.contact_person" type="text" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>联系电话：</label>
                  <input v-model="editMerchantForm.contact_phone" type="text" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>店铺地址：</label>
                  <input v-model="editMerchantForm.business_address" type="text" class="form-input" required>
                </div>
                <div class="form-group">
                  <label>店铺描述：</label>
                  <textarea v-model="editMerchantForm.business_description" class="form-textarea" rows="3"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer" :class="{ 'vertical-buttons': isEditingMerchant }">
          <!-- 编辑状态下的按钮 -->
          <template v-if="isEditingMerchant">
            <button @click="saveMerchantInfo" class="btn btn-primary" :disabled="savingMerchant">
              <i class="fas fa-save"></i> {{ savingMerchant ? '提交中...' : '提交' }}
            </button>
            <button @click="cancelEditMerchant" class="btn btn-outline">
              <i class="fas fa-times"></i> 取消
            </button>
          </template>
          <!-- 非编辑状态下的按钮 -->
          <template v-else>
            <button class="btn btn-outline" @click="closeMerchantSettingsModal">关闭</button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import ProductCard from '@/components/ProductCard.vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api' // 添加这行导入API服务
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'

onBeforeUnmount(() => {
  // 清理临时头像 URL
  if (editForm.avatarPreview && editForm.avatarPreview.startsWith('blob:')) {
    URL.revokeObjectURL(editForm.avatarPreview);
  }
});
const router = useRouter()
const route = useRoute()
const activeTab = ref('selling')
const showEditModal = ref(false)
const showOfflineModal = ref(false)
const showMerchantModal = ref(false)
const showCancelMerchantModal = ref(false)
const showMerchantSettingsModal = ref(false)
const showDisplaySettingsModal = ref(false)
const savingProfile = ref(false)
const submittingMerchant = ref(false)
const cancelingMerchant = ref(false)
const cancelMerchantReason = ref('')
const savingSettings = ref(false)
// 添加响应式时间戳
const avatarTimestamp = ref(Date.now())
const authStore = useAuthStore();

// 使用计算属性确保响应式更新
const avatarUrl = computed(() => {
  if (!authStore.user?.avatar) return '/static/images/default_avatar.png';
  
  // 修复HTTPS协议问题
  let avatarUrl = authStore.user.avatar;
  if (avatarUrl.startsWith('https://127.0.0.1:8000')) {
    avatarUrl = avatarUrl.replace('https://127.0.0.1:8000', 'http://127.0.0.1:8000');
  }
  
  // 添加时间戳强制刷新
  return `${avatarUrl}?t=${avatarTimestamp.value}`;
});

// 监听头像变化，强制更新
watch(() => authStore.user?.avatar, (newAvatar) => {
  if (newAvatar) {
    console.log('检测到头像变化，强制刷新:', newAvatar);
    avatarTimestamp.value = Date.now();
  }
});

const handleImageError = (event) => {
  console.log('头像加载失败，使用默认头像');
  event.target.src = '/static/images/default_avatar.png';
};

// 头像上传状态
const avatarLoading = ref(false)
const avatarUploadProgress = ref(0)
const avatarError = ref('')

// 处理头像上传
const handleEditAvatarUpload = (e) => {
  handleAvatarUpload(e, false)
}

// 编辑表单
const editForm = reactive({
  username: '',
  bio: '',
  avatarPreview: '',
  contact: '',
  location: ''
})

// 商家认证表单
const merchantForm = reactive({
  business_name: '',
  contact_person: '',
  contact_phone: '',
  business_address: '',
  business_license: '',
  business_description: ''
})

// 待认证用户验证表单
const verificationForm = reactive({
  business_name: '',
  contact_person: '',
  contact_phone: '',
  business_address: '',
  business_license: '',
  business_description: ''
})

// 商家信息
const merchantInfo = ref({})

// 商家编辑相关
const isEditingMerchant = ref(false)
const savingMerchant = ref(false)
const editMerchantForm = ref({
  business_name: '',
  contact_person: '',
  contact_phone: '',
  business_address: '',
  business_description: ''
})

// 展示设置
const displaySettings = reactive({
  display_frequency: 5
})

// 用于保存新头像文件对象
const newAvatarFile = ref(null)

// 新增：打开编辑模态框并填充数据
const openEditModal = () => {
  const currentUser = authStore.user;
  if (currentUser) {
    editForm.username = currentUser.username || '';
    editForm.bio = currentUser.bio || '';
    editForm.location = currentUser.location || '';
    editForm.contact = currentUser.contact || '';
    editForm.avatarPreview = currentUser.avatar ? `${currentUser.avatar}?t=${new Date().getTime()}` : ''; // 加时间戳避免缓存
  }
  newAvatarFile.value = null; // 重置文件
  showEditModal.value = true;
};

// 关闭模态框，并清理可能存在的Blob URL
const closeEditModal = () => {
  if (editForm.avatarPreview && editForm.avatarPreview.startsWith('blob:')) {
    URL.revokeObjectURL(editForm.avatarPreview);
  }
  showEditModal.value = false;
};

// 当用户选择新头像文件时
const handleAvatarFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    newAvatarFile.value = file;
    // 创建一个临时的URL用于预览
    editForm.avatarPreview = URL.createObjectURL(file);
  }
};

// 保存所有资料
const saveProfile = async () => {
  if (!editForm.username) {
    alert('用户名不能为空！');
    return;
  }
  savingProfile.value = true;
  try {
    // 1. 如果有新头像，先上传头像
    if (newAvatarFile.value) {
      await authStore.updateAvatar(newAvatarFile.value);
    }
    
    // 2. 更新其他文本资料
    const profileData = {
      username: editForm.username,
      bio: editForm.bio,
      location: editForm.location,
      contact: editForm.contact,
    };
    
    await authStore.updateUserProfile(profileData);
    
    alert('资料更新成功！');
    closeEditModal();
    // 强制刷新一次用户信息，确保页面数据同步
    await authStore.fetchCurrentUser();

  } catch (error) {
    console.error('资料更新失败:', error);
    alert('资料更新失败，请重试。');
  } finally {
    savingProfile.value = false;
  }
};

// 通用的头像上传处理函数
const handleAvatarUpload = async (e, isProfileHeader = false) => {
  const file = e.target.files[0]
  if (!file) return

  // 验证文件类型和大小
  const validImageTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!validImageTypes.includes(file.type)) {
    const errorMsg = '只支持 JPG, PNG 或 GIF 格式的图片'
    if (isProfileHeader) {
      avatarError.value = errorMsg
    } else {
      alert(errorMsg)
    }
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    const errorMsg = '图片大小不能超过 5MB'
    if (isProfileHeader) {
      avatarError.value = errorMsg
    } else {
      alert(errorMsg)
    }
    return
  }

  // 重置错误状态
  if (isProfileHeader) {
    avatarError.value = ''
  }

  // 创建预览
  const previewUrl = URL.createObjectURL(file)

  // 页面顶部的头像上传
  if (isProfileHeader) {
    avatarLoading.value = true
    avatarUploadProgress.value = 0
    avatarTimestamp.value = Date.now()
    
    try {
      // 模拟上传进度
      const interval = setInterval(() => {
        avatarUploadProgress.value += 10
        if (avatarUploadProgress.value >= 100) {
          clearInterval(interval)
        }
      }, 200)
      
      // 等待上传完成
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 实际调用API更新头像
      const updatedUser = await authStore.updateAvatar(file)
      
      // 重要：使用服务器返回的新头像URL，而不是临时预览URL
      // 因为临时URL会在页面刷新后失效
      authStore.user.avatar = updatedUser.avatar
      
    } catch (error) {
      console.error('头像上传失败:', error)
      avatarError.value = '上传失败，请重试'
      // 显示更具体的错误信息
      if (error.response?.data?.detail) {
        avatarError.value = error.response.data.detail
      }
    } finally {
      avatarLoading.value = false
      e.target.value = null
      setTimeout(() => {
        avatarUploadProgress.value = 0
      }, 2000)
    }
  } 
  // 编辑模态框中的头像上传
  else {
    // 释放之前的临时URL（如果存在）
    if (newAvatarFile.value && editForm.avatarPreview.startsWith('blob:')) {
      URL.revokeObjectURL(editForm.avatarPreview)
    }
    // 创建预览
    editForm.avatarPreview = previewUrl
    // 保存文件对象用于后续上传
    newAvatarFile.value = file
    e.target.value = null
  }
  // 在编辑模态框分支结束时添加：
  if (!isProfileHeader && newAvatarFile.value) {
    // 组件卸载时清理临时URL
    onBeforeUnmount(() => {
      if (editForm.avatarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(editForm.avatarPreview)
      }
    })
  }
};


// 添加获取真实数据的方法
// Profile.vue
// 修改监听器
watch(
  () => authStore.user?.items_count, // 使用可选链避免访问 null
  (newCount, oldCount) => {
    // 确保值存在且有效
    if (newCount !== undefined && oldCount !== undefined && newCount > oldCount) {
      fetchRealSellingItems();
    }
  }
);
const fetchRealSellingItems = async () => {
  try {
    if (!authStore.user || !authStore.user.id) {
      console.error('用户信息未加载');
      return;
    }
    loading.selling = true;
    hasMoreSelling.value = true;
    const params = {
      skip: 0,
      limit: pagination.selling.perPage,
      order_by: sorting.selling
    };
    const response = await api.getUserSellingItems(
      authStore.user.id,
      params
    );
    sellingItems.value = response.data.data;
    if (response.data.data.length < pagination.selling.perPage) {
      hasMoreSelling.value = false;
    }
    tabs.value[0].count = response.data.total;
  } catch (error) {
    console.error('获取商品失败:', error);
    alert('获取商品失败，请刷新页面重试');
  } finally {
    loading.selling = false;
    loading.more = false;
  }
};

// 标签页数据，动态统计数量
const tabs = computed(() => [
  { id: 'selling', label: '在售', count: sellingItems.value.length },
  { id: 'sold', label: '已售', count: soldItems.value.length },
  { id: 'favorites', label: '收藏', count: favoriteItems.value.length },
  { id: 'buy_requests', label: '求购', count: myBuyRequests.value.length }
])

// 用户信息
const user = computed(() => {
  return authStore.user || {
    id: 0,
    username: '加载中...',
    avatar: 'default_avatar.png',
    bio: '',
    followers: 0,
    following: 0,
    items_count: 0,
    contact: '',
    location: ''
  }
});

// 分页相关状态
const pagination = reactive({
  selling: { page: 1, perPage: 8, total: 0 },
  sold: { page: 1, perPage: 8, total: 0 },
  favorites: { page: 1, perPage: 8, total: 0 }
})

const hasMore = reactive({
  selling: true,
  sold: true,
  favorites: true
})

const loading = reactive({
  selling: false,
  sold: false,
  favorites: false,
  offline: false,
  more: false
})

const sorting = reactive({
  selling: 'newest'
})

const sellingItems = ref([])
const soldItems = ref([])
const favoriteItems = ref([])
const offlineItems = ref([])

// 计算属性：排序后的在售商品
const sortedSellingItems = computed(() => {
  if (sellingItems.value.length === 0) return []
  
  // 创建副本以避免修改原始数据
  const items = [...sellingItems.value]
  
  switch (sorting.selling) {
    case 'price_asc':
      // 价格从低到高
      return items.sort((a, b) => a.price - b.price)
    case 'price_desc':
      // 价格从高到低
      return items.sort((a, b) => b.price - a.price)
    case 'popular':
      // 最受欢迎（按浏览量）
      return items.sort((a, b) => b.views - a.views)
    case 'newest':
    default:
      // 最新发布（按创建时间）
      const parseTime = (t) => {
        if (!t) return 0
        let date
        if (typeof t === 'string') {
          let iso = t.replace(' ', 'T')
          if (!iso.endsWith('Z')) iso += 'Z'
          date = new Date(iso)
        } else {
          date = new Date(t)
        }
        return isNaN(date.getTime()) ? 0 : date.getTime()
      }
      return items.sort((a, b) => 
        parseTime(b.created_at) - parseTime(a.created_at)
      )
  }
})

// 添加排序计算属性
const sortedSoldItems = computed(() => {
  if (soldItems.value.length === 0) return [];
  
  const items = [...soldItems.value];
  
  switch (sorting.sold) {
    case 'oldest':
      return items.sort((a, b) => 
        new Date(a.soldAt).getTime() - new Date(b.soldAt).getTime()
      );
    case 'newest':
    default:
      return items.sort((a, b) => 
        new Date(b.soldAt).getTime() - new Date(a.soldAt).getTime()
      );
  }
})

// 监听标签切换，切到求购时拉取数据
watch(activeTab, (newTab) => {
  if (newTab === 'selling' && sellingItems.value.length === 0) {
    fetchSellingItems()
  } else if (newTab === 'sold' && soldItems.value.length === 0) {
    fetchSoldItems()
  } else if (newTab === 'favorites' && favoriteItems.value.length === 0) {
    fetchFavoriteItems()
  } else if (newTab === 'buy_requests' && myBuyRequests.value.length === 0) {
    fetchMyBuyRequests()
  }
})

// 监听排序变化
watch(() => sorting.selling, () => {
  if (activeTab.value === 'selling') {
    pagination.selling.page = 1; // 重置到第一页
    fetchRealSellingItems();
  }
})

// 修改onMounted钩子
onMounted(async () => {
  try {
    // 确保用户信息已加载
    if (!authStore.user) {
      await authStore.fetchCurrentUser();
    }
    // 进入页面时同时拉取三类商品的第一页，刷新tab数字
    await Promise.all([
      fetchRealSellingItems(),
      fetchSoldItems(true),
      fetchFavoriteItems(true),
      fetchMyBuyRequests()
    ]);
  } catch (error) {
    console.error('初始化失败:', error);
    alert('加载用户信息失败，请刷新页面');
  }
});

// 切换标签
const changeTab = (tabId) => {
  activeTab.value = tabId
  if (tabId === 'selling' && sellingItems.value.length === 0) {
    fetchSellingItems()
  } else if (tabId === 'sold' && soldItems.value.length === 0) {
    fetchSoldItems()
  } else if (tabId === 'favorites' && favoriteItems.value.length === 0) {
    fetchFavoriteItems()
  } else if (tabId === 'buy_requests' && myBuyRequests.value.length === 0) {
    fetchMyBuyRequests()
  }
}

// 获取标签数据
const fetchTabData = (tabId) => {
  if (tabId === 'selling') {
    fetchSellingItems()
  } else if (tabId === 'sold') {
    fetchSoldItems()
  } else if (tabId === 'favorites') {
    fetchFavoriteItems()
  } else if (tabId === 'buy_requests') {
    fetchMyBuyRequests()
  }
}

// 获取已售商品
const fetchSoldItems = async (reset = false) => {
  if (reset) {
    pagination.sold.page = 1;
    soldItems.value = [];
  }
  loading.sold = true;
  try {
    if (!authStore.user || !authStore.user.id) {
      console.error('用户信息未加载');
      return;
    }
    const response = await api.getUserSoldItems(
      authStore.user.id,
      {
        skip: (pagination.sold.page - 1) * pagination.sold.perPage,
        limit: pagination.sold.perPage
      }
    );
    if (response.data.data.length === 0 && pagination.sold.page > 1) {
      pagination.sold.page -= 1;
      alert('已经是最后一页');
      await fetchSoldItems();
      return;
    }
    if (pagination.sold.page === 1) {
      soldItems.value = response.data.data;
    } else {
      soldItems.value = [...soldItems.value, ...response.data.data];
    }
    tabs.value[1].count = response.data.total;
    if (response.data.data.length < pagination.sold.perPage) {
      hasMoreSold.value = false;
    }
  } catch (error) {
    console.error('获取已售商品失败:', error);
    alert('获取已售商品失败，请重试');
  } finally {
    loading.sold = false;
    loading.more = false;
  }
};

// 获取收藏商品
const fetchFavoriteItems = async (reset = false) => {
  if (reset) {
    pagination.favorites.page = 1;
    favoriteItems.value = [];
  }
  loading.favorites = true;
  try {
    if (!authStore.user || !authStore.user.id) {
      console.error('用户信息未加载');
      return;
    }
    const response = await api.getUserFavorites(
      authStore.user.id,
      {
        skip: (pagination.favorites.page - 1) * pagination.favorites.perPage,
        limit: pagination.favorites.perPage
      }
    );
    const items = response.data.map(favorite => favorite.item);
    // 自动回退
    if (items.length === 0 && pagination.favorites.page > 1) {
      pagination.favorites.page -= 1;
      alert('已经是最后一页');
      await fetchFavoriteItems();
      return;
    }
    if (pagination.favorites.page === 1) {
      favoriteItems.value = items;
    } else {
      favoriteItems.value = [...favoriteItems.value, ...items];
    }
    // 收藏总数（如后端支持total字段）
    if (response.data.total !== undefined) {
      tabs.value[2].count = response.data.total;
    } else {
      tabs.value[2].count = items.length;
    }
    if (items.length < pagination.favorites.perPage) {
      hasMoreFavorite.value = false;
    }
  } catch (error) {
    console.error('获取收藏商品失败:', error);
    alert('获取收藏商品失败，请重试');
  } finally {
    loading.favorites = false;
    loading.more = false;
  }
};

// 加载更多
const loadMore = (type) => {
  loading.more = true;
  pagination[type].page += 1;
  fetchTabData(type);
};

// 加载上一页
const loadPrevious = (type) => {
  if (pagination[type].page > 1) {
    loading.more = true;
    pagination[type].page -= 1;
    fetchTabData(type);
  }
};

// 导航函数
const navigateToPublish = () => {
  router.push({ name: 'Publish' }); // 确保与路由配置中的名称匹配
};

const navigateToDiscover = () => {
  router.push('/');
};

// 获取在售商品
const fetchSellingItems = async (reset = false) => {
  if (reset) {
    pagination.selling.page = 1;
    sellingItems.value = [];
  }
  loading.selling = true;
  try {
    const response = await api.getUserSellingItems(user.value.id, {
      page: pagination.selling.page,
      per_page: pagination.selling.perPage
    });
    sellingItems.value = reset ? response.data.data : [...sellingItems.value, ...response.data.data];
  } catch (error) {
    console.error('获取在售商品失败:', error);
  } finally {
    loading.selling = false;
  }
};

// 模拟数据生成函数
const generateMockSellingItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1 + (pagination.selling.page - 1) * pagination.selling.perPage,
    title: `商品 ${i + 1 + (pagination.selling.page - 1) * pagination.selling.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    views: Math.floor(Math.random() * 500),
    createdAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
};

const generateMockSoldItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `sold-${i + 1 + (pagination.sold.page - 1) * pagination.sold.perPage}`,
    title: `已售商品 ${i + 1 + (pagination.sold.page - 1) * pagination.sold.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    soldAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
};

const generateMockFavoriteItems = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `fav-${i + 1 + (pagination.favorites.page - 1) * pagination.favorites.perPage}`,
    title: `收藏商品 ${i + 1 + (pagination.favorites.page - 1) * pagination.favorites.perPage}`,
    price: Math.floor(Math.random() * 1000) + 100,
    image: `https://picsum.photos/300/300?random=${Math.floor(Math.random() * 1000)}`,
    location: ['北京', '上海', '广州', '深圳'][Math.floor(Math.random() * 4)],
    favoritedAt: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString()
  }))
}

// 关闭已下架商品模态框
const closeOfflineModal = () => {
  showOfflineModal.value = false
}

// 打开已下架商品模态框
const openOfflineModal = async () => {
  showOfflineModal.value = true
  if (offlineItems.value.length === 0) {
    await fetchOfflineItems()
  }
}

// 获取已下架商品
const fetchOfflineItems = async () => {
  loading.offline = true;
  try {
    if (!authStore.user || !authStore.user.id) {
      console.error('用户信息未加载')
      return
    }
    const response = await api.getUserOfflineItems(
      authStore.user.id,
      {
        skip: 0,
        limit: 50 // 获取更多已下架商品
      }
    )
    offlineItems.value = response.data.data
    // 可选：tabs.value[3].count = response.data.total
  } catch (error) {
    console.error('获取已下架商品失败:', error)
    alert('获取已下架商品失败，请重试')
  } finally {
    loading.offline = false
  }
}

// 重新上架商品
const handleOnlineItem = async (itemId) => {
  try {
    await api.updateItemStatus(itemId, 'online')
    
    // 从在售商品列表中移除（如果存在）
    sellingItems.value = sellingItems.value.filter(item => item.id !== itemId)
    
    // 从已下架商品列表中移除（如果存在）
    offlineItems.value = offlineItems.value.filter(item => item.id !== itemId)
    
    // 刷新在售商品列表
    await fetchRealSellingItems()
    
    // 更新用户商品数量统计
    if (authStore.user) {
      authStore.user.items_count = (authStore.user.items_count || 0) + 1;
    }
    
    alert('商品已重新上架')
  } catch (error) {
    console.error('上架商品失败:', error)
    alert('上架失败，请重试')
  }
}

// 处理商品下架
const handleOfflineItem = async (itemId) => {
  if (confirm('确定要下架该商品吗？下架后其他用户将无法看到此商品。')) {
    try {
      await api.updateItemStatus(itemId, 'offline')
      
      // 从在售商品列表中移除
      sellingItems.value = sellingItems.value.filter(item => item.id !== itemId)
      
      // 更新用户商品数量统计
      if (authStore.user) {
        authStore.user.items_count = Math.max(0, (authStore.user.items_count || 0) - 1);
      }
      
      // 如果已下架商品模态框是打开的，刷新已下架商品列表
      if (showOfflineModal.value) {
        await fetchOfflineItems()
      }
      
      alert('商品已下架')
    } catch (error) {
      console.error('已下架商品失败:', error)
      alert('下架失败，请重试')
    }
  }
}

// 获取商品第一张图片
const getFirstImage = (item) => {
  if (!item.images) return '/static/images/default_product.jpg'
  const images = item.images.split(',')
  const img = images[0]
  if (!img) return '/static/images/default_product.jpg'
  // 如果已经是完整URL（包含http），直接返回
  if (img.startsWith('http')) return img
  // 如果是相对路径，添加/前缀
  if (img.startsWith('/')) return img
  return `/${img}`
}

// 处理商品已售出
const handleSoldItem = async (itemId) => {
  if (confirm('确定要将该商品标记为已售吗？')) {
    try {
      await api.markItemSold(itemId)
      
      // 从在售商品列表中移除
      sellingItems.value = sellingItems.value.filter(item => item.id !== itemId)
      
      // 如果已售商品标签页是当前激活的，刷新已售商品列表
      if (activeTab.value === 'sold') {
        await fetchSoldItems()
      }
      
      alert('商品已标记为已售')
    } catch (error) {
      console.error('标记为已售失败:', error)
      alert('操作失败，请重试')
    }
  }
}

// 处理商品删除
const handleDeleteItem = async (itemId) => {
  if (!confirm('确定要删除该商品吗？删除后将无法恢复。')) {
    return;
  }
  try {
    await api.deleteItem(itemId);
    
    // 从在售商品列表中移除
    sellingItems.value = sellingItems.value.filter(item => item.id !== itemId);
    
    // 从已售商品列表中移除
    soldItems.value = soldItems.value.filter(item => item.id !== itemId);
    
    // 从已下架商品列表中移除（如果存在）
    offlineItems.value = offlineItems.value.filter(item => item.id !== itemId);
    
    // 更新统计数据
    tabs.value[0].count = sellingItems.value.length;
    tabs.value[1].count = soldItems.value.length;
    
    // 更新用户商品数量统计
    if (authStore.user) {
      authStore.user.items_count = Math.max(0, (authStore.user.items_count || 0) - 1);
    }
    
    alert('商品已删除');
  } catch (error) {
    console.error('删除商品失败:', error);
    alert('删除失败，请重试');
  }
}

// 处理商品编辑
const handleEditItem = (itemId) => {
  router.push(`/publish?edit=${itemId}`);
}

// 取消收藏商品
const handleUnfavoriteItem = async (itemId) => {
  if (confirm('确定要取消收藏该商品吗？')) {
    try {
      await api.removeFavorite(authStore.user.id, itemId)
      
      // 从收藏商品列表中移除
      favoriteItems.value = favoriteItems.value.filter(item => item.id !== itemId)
      
      // 更新统计数据
      tabs.value[2].count = favoriteItems.value.length
      
      alert('商品已取消收藏')
    } catch (error) {
      console.error('取消收藏失败:', error)
      alert('取消收藏失败，请重试')
    }
  }
}

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

const hasMoreSelling = ref(true)
const loadMoreSelling = async () => {
  loading.more = true;
  pagination.selling.page += 1;
  try {
    const response = await api.getUserSellingItems(authStore.user.id, {
      skip: (pagination.selling.page - 1) * pagination.selling.perPage,
      limit: pagination.selling.perPage,
      order_by: sorting.selling
    });
    if (response.data.data.length < pagination.selling.perPage) {
      hasMoreSelling.value = false;
    }
    sellingItems.value = [...sellingItems.value, ...response.data.data];
    tabs.value[0].count = response.data.total;
  } catch (error) {
    console.error('加载更多商品失败:', error);
    alert('加载更多失败，请重试');
  } finally {
    loading.more = false;
  }
}

const infiniteScrollTrigger = ref(null)
let observer = null

onMounted(() => {
  // 只监听在售商品tab
  observer = new window.IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMoreSelling.value && !loading.more && activeTab.value === 'selling') {
      loadMoreSelling()
    }
  }, { threshold: 0.1 })
  if (infiniteScrollTrigger.value) {
    observer.observe(infiniteScrollTrigger.value)
  }
})

onBeforeUnmount(() => {
  if (observer && infiniteScrollTrigger.value) {
    observer.unobserve(infiniteScrollTrigger.value)
  }
})

const hasMoreSold = ref(true)
const hasMoreFavorite = ref(true)
const infiniteScrollSoldTrigger = ref(null)
const infiniteScrollFavTrigger = ref(null)
let observerSold = null
let observerFav = null

const loadMoreSold = async () => {
  loading.more = true;
  pagination.sold.page += 1;
  try {
    const response = await api.getUserSoldItems(authStore.user.id, {
      skip: (pagination.sold.page - 1) * pagination.sold.perPage,
      limit: pagination.sold.perPage
    });
    if (response.data.data.length < pagination.sold.perPage) {
      hasMoreSold.value = false;
    }
    soldItems.value = [...soldItems.value, ...response.data.data];
    tabs.value[1].count = response.data.total;
  } catch (error) {
    console.error('加载更多已售商品失败:', error);
    alert('加载更多失败，请重试');
  } finally {
    loading.more = false;
  }
}
const loadMoreFavorite = async () => {
  loading.more = true;
  pagination.favorites.page += 1;
  try {
    const response = await api.getUserFavorites(authStore.user.id, {
      skip: (pagination.favorites.page - 1) * pagination.favorites.perPage,
      limit: pagination.favorites.perPage
    });
    const items = response.data.map(favorite => favorite.item);
    if (items.length < pagination.favorites.perPage) {
      hasMoreFavorite.value = false;
    }
    favoriteItems.value = [...favoriteItems.value, ...items];
  } catch (error) {
    console.error('加载更多收藏商品失败:', error);
    alert('加载更多失败，请重试');
  } finally {
    loading.more = false;
  }
}

// IntersectionObserver 绑定修复，确保ref变化时自动observe
watch(
  () => infiniteScrollTrigger.value,
  (el, oldEl) => {
    if (observer && oldEl) observer.unobserve(oldEl)
    if (observer && el) observer.observe(el)
  }
)
watch(
  () => infiniteScrollSoldTrigger.value,
  (el, oldEl) => {
    if (observerSold && oldEl) observerSold.unobserve(oldEl)
    if (observerSold && el) observerSold.observe(el)
  }
)
watch(
  () => infiniteScrollFavTrigger.value,
  (el, oldEl) => {
    if (observerFav && oldEl) observerFav.unobserve(oldEl)
    if (observerFav && el) observerFav.observe(el)
  }
)

const myBuyRequests = ref([])
const loadingBuyRequests = ref(false)

const fetchMyBuyRequests = async () => {
  loadingBuyRequests.value = true;
  try {
    const res = await api.getMyBuyRequests();
    myBuyRequests.value = res.data;
  } finally {
    loadingBuyRequests.value = false;
  }
}

const handleDeleteBuyRequest = async (id) => {
  if (!confirm('确定要删除该求购信息吗？')) return;
  await api.deleteBuyRequest(id);
  fetchMyBuyRequests();
}

const handleEditBuyRequest = (id) => {
  router.push(`/publish-buy-request?edit=${id}`);
}

const goToBuyRequestDetail = (id) => {
  router.push(`/buy-request/${id}`);
}

onMounted(() => {
  // 支持通过URL参数tab自动切换
  if (route.query.tab && ['selling','sold','favorites','buy_requests'].includes(route.query.tab)) {
    activeTab.value = route.query.tab
  }
})

watch(() => route.query.tab, (newTab) => {
  if (newTab && ['selling','sold','favorites','buy_requests'].includes(newTab)) {
    activeTab.value = newTab
  }
})

const hasBuyRequestImage = (images) => {
  if (!images) return false
  let img = ''
  if (typeof images === 'string') {
    img = images.split(',')[0]
  } else if (Array.isArray(images)) {
    img = images[0]
  }
  return !!img
}

const getBuyRequestImage = (images) => {
  if (!images) return null
  let img = ''
  if (typeof images === 'string') {
    img = images.split(',')[0]
  } else if (Array.isArray(images)) {
    img = images[0]
  }
  if (!img) return null
  // 如果是完整URL，直接返回
  if (img.startsWith('http')) return img
  // 如果是以/static开头，补全域名
  if (img.startsWith('/static')) return 'http://127.0.0.1:8000' + img
  // 否则拼成 /static/images/xxx
  return 'http://127.0.0.1:8000/static/images/' + img
}

// 商家认证相关方法
const getMerchantStatusText = () => {
  if (user.value.is_merchant) return '已认证商家'
  if (user.value.is_pending_merchant) return '认证审核中'
  if (user.value.is_pending_verification) return '待认证状态'
  return '普通用户'
}

const getMerchantStatusClass = () => {
  if (user.value.is_merchant) return 'status-approved'
  if (user.value.is_pending_merchant) return 'status-pending'
  if (user.value.is_pending_verification) return 'status-pending-verification'
  return 'status-normal'
}

const getMerchantModalTitle = () => {
  if (user.value.is_pending_merchant) return '商家认证状态'
  if (user.value.is_pending_verification) return '待认证状态'
  return '申请商家认证'
}

const openMerchantModal = () => {
  showMerchantModal.value = true
  if (user.value.is_pending_merchant) {
    // 如果是待定商家，获取商家信息
    fetchMerchantInfo()
  } else if (user.value.is_pending_verification) {
    // 如果是待认证用户，获取商家信息并预填充验证表单
    fetchMerchantInfoForVerification()
  }
}

const closeMerchantModal = () => {
  showMerchantModal.value = false
  // 重置表单
  Object.assign(merchantForm, {
    business_name: '',
    contact_person: '',
    contact_phone: '',
    business_address: '',
    business_license: '',
    business_description: ''
  })
}

const openMerchantSettings = () => {
  showMerchantSettingsModal.value = true
  fetchMerchantInfo()
}

const closeMerchantSettingsModal = () => {
  showMerchantSettingsModal.value = false
  isEditingMerchant.value = false
}

// 开始编辑商家信息
const startEditMerchant = () => {
  editMerchantForm.value = {
    business_name: merchantInfo.value.business_name || '',
    contact_person: merchantInfo.value.contact_person || '',
    contact_phone: merchantInfo.value.contact_phone || '',
    business_address: merchantInfo.value.business_address || '',
    business_description: merchantInfo.value.business_description || ''
  }
  isEditingMerchant.value = true
}

// 取消编辑商家信息
const cancelEditMerchant = () => {
  isEditingMerchant.value = false
  editMerchantForm.value = {
    business_name: '',
    contact_person: '',
    contact_phone: '',
    business_address: '',
    business_description: ''
  }
}

// 提交商家信息修改
const saveMerchantInfo = async () => {
  if (!editMerchantForm.value.business_name.trim()) {
    alert('请输入店铺名称')
    return
  }
  if (!editMerchantForm.value.contact_person.trim()) {
    alert('请输入联系人')
    return
  }
  if (!editMerchantForm.value.contact_phone.trim()) {
    alert('请输入联系电话')
    return
  }
  if (!editMerchantForm.value.business_address.trim()) {
    alert('请输入店铺地址')
    return
  }

  savingMerchant.value = true
  try {
    // 更新商家信息
    await api.updateMerchantInfo(editMerchantForm.value)
    
    // 更新本地商家信息
    Object.assign(merchantInfo.value, editMerchantForm.value)
    
    alert('商家信息已修改，需要重新审核')
    isEditingMerchant.value = false
    
    // 重新加载用户信息
    await authStore.fetchCurrentUser()
  } catch (error) {
    console.error('提交商家信息失败:', error)
    alert('提交失败，请重试')
  } finally {
    savingMerchant.value = false
  }
}

const openDisplaySettings = () => {
  showDisplaySettingsModal.value = true
  fetchDisplaySettings()
}

const closeDisplaySettingsModal = () => {
  showDisplaySettingsModal.value = false
}

const submitMerchantApplication = async () => {
  if (!merchantForm.business_name || !merchantForm.contact_person || 
      !merchantForm.contact_phone || !merchantForm.business_address) {
    alert('请填写所有必填项')
    return
  }
  
  submittingMerchant.value = true
  try {
    await api.createMerchantApplication(merchantForm)
    alert('商家认证申请已提交，请等待管理员审核')
    closeMerchantModal()
    // 刷新用户信息
    await authStore.fetchCurrentUser()
  } catch (error) {
    console.error('提交商家认证申请失败:', error)
    alert('提交失败，请重试')
  } finally {
    submittingMerchant.value = false
  }
}

// 待认证用户提交验证信息
const submitMerchantVerification = async () => {
  if (!verificationForm.business_name || !verificationForm.contact_person || 
      !verificationForm.contact_phone || !verificationForm.business_address) {
    alert('请填写所有必填项')
    return
  }
  
  submittingMerchant.value = true
  try {
    await api.updateMerchantInfo(verificationForm)
    alert('商家信息已提交，请等待管理员审核')
    closeMerchantModal()
    // 刷新用户信息
    await authStore.fetchCurrentUser()
  } catch (error) {
    console.error('提交商家验证信息失败:', error)
    alert('提交失败，请重试')
  } finally {
    submittingMerchant.value = false
  }
}

const cancelApplication = async () => {
  if (!confirm('确定要取消商家认证申请吗？')) {
    return
  }
  
  try {
    await api.cancelMerchantApplication()
    alert('申请已取消')
    // 刷新用户信息
    await authStore.fetchCurrentUser()
  } catch (error) {
    console.error('取消申请失败:', error)
    alert('取消失败，请重试')
  }
}

// 取消商家认证相关函数
const openCancelMerchantModal = () => {
  cancelMerchantReason.value = ''
  showCancelMerchantModal.value = true
}

const closeCancelMerchantModal = () => {
  showCancelMerchantModal.value = false
  cancelMerchantReason.value = ''
}

const cancelMerchantApplication = async () => {
  if (!cancelMerchantReason.value.trim()) {
    alert('请输入取消原因')
    return
  }
  
  cancelingMerchant.value = true
  try {
    await api.cancelMerchantApplication(cancelMerchantReason.value)
    alert('取消申请已提交，等待管理员处理')
    closeCancelMerchantModal()
    // 刷新用户信息
    await authStore.fetchCurrentUser()
  } catch (error) {
    console.error('取消商家认证失败:', error)
    alert('提交失败，请重试')
  } finally {
    cancelingMerchant.value = false
  }
}

const fetchMerchantInfo = async () => {
  try {
    const response = await api.getMerchantInfo()
    merchantInfo.value = response.data || response
  } catch (error) {
    console.error('获取商家信息失败:', error)
  }
}

// 为待认证用户获取商家信息并预填充验证表单
const fetchMerchantInfoForVerification = async () => {
  try {
    const response = await api.getMerchantInfo()
    const merchant = response.data || response
    // 预填充验证表单
    Object.assign(verificationForm, {
      business_name: merchant.business_name || '',
      contact_person: merchant.contact_person || '',
      contact_phone: merchant.contact_phone || '',
      business_address: merchant.business_address || '',
      business_license: merchant.business_license || '',
      business_description: merchant.business_description || ''
    })
  } catch (error) {
    console.error('获取商家信息失败:', error)
  }
}

const fetchDisplaySettings = async () => {
  try {
    const response = await api.getMerchantDisplayConfig()
    if (response.data) {
      displaySettings.display_frequency = response.data.display_frequency
    }
  } catch (error) {
    console.error('获取展示设置失败:', error)
  }
}

const saveDisplaySettings = async () => {
  savingSettings.value = true
  try {
    await api.updateMerchantDisplayConfig({
      display_frequency: displaySettings.display_frequency
    })
    alert('设置已保存')
    closeMerchantSettingsModal()
  } catch (error) {
    console.error('保存展示设置失败:', error)
    alert('保存失败，请重试')
  } finally {
    savingSettings.value = false
  }
}

</script>

<style scoped>
/* 个人资料头部区域优化 */
.profile-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.user-info {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex: 1;
}

/* 头像容器优化 */
.avatar-container {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f5f5f5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 3px solid #fff;
}

.avatar-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 用户详情区域优化 */
.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.user-bio {
  color: #6c757d;
  font-size: 14px;
  margin: 0 0 12px 0;
  line-height: 1.4;
  max-width: 300px;
}

/* 商家状态优化 */
.merchant-status {
  margin: 8px 0 12px 0;
}

/* 用户统计优化 */
.user-stats {
  display: flex;
  gap: 24px;
  margin-top: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  min-width: 60px;
}

.stat-item strong {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-item span {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 图片等比填充 */
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.upload-progress {
  margin-top: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  height: 24px;
  position: relative;
  width: 100%;
  max-width: 150px;
}

.progress-bar {
  height: 100%;
  background: #3498db;
  border-radius: 4px;
  transition: width 0.3s;
}

.upload-progress span {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  font-size: 12px;
  font-weight: bold;
}

.avatar-error {
  margin-top: 8px;
  color: #e74c3c;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 编辑资料模态框 */
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
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 8px;
}

.modal-body {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-footer.vertical-buttons {
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

.modal-footer.vertical-buttons .btn {
  width: 100%;
  justify-content: center;
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

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group textarea {
  resize: vertical;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.avatar-edit-preview {
  display: flex;
  align-items: center;
  gap: 20px;
}

.preview-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #eee;
  background-color: #f5f5f5;
}

.avatar-edit-btn {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  font-size: 14px;
}

.avatar-edit-btn:hover {
  background: #eaeaea;
}

/* 加载状态 */
.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 16px;
}

.skeleton-card {
  height: 250px;
  background: #f5f5f5;
  border-radius: 8px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state i {
  font-size: 60px;
  margin-bottom: 20px;
  color: #e0e0e0;
}

.empty-state p {
  margin-bottom: 20px;
  font-size: 16px;
}

.empty-state .btn {
  margin-top: 10px;
}

/* 标签页样式 */
.tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.tabs button {
  position: relative;
  padding: 12px 24px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  transition: all 0.3s;
}

.tabs button.active {
  color: #3498db;
  font-weight: 600;
}

.tabs button.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3px;
  background: #3498db;
  border-radius: 3px 3px 0 0;
}

.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 8px;
  background: #fff;
  border-radius: 10px;
  font-size: 15px;
  font-weight: bold;
  color: #3498db;
  box-shadow: none;
  border: none;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 16px;
}

.sort-controls select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

/* 商品网格 */
.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 0 16px;
}

.pagination {
  text-align: center;
  margin: 30px 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 16px;
    padding: 16px;
  }
  
  .user-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 16px;
  }
  
  .avatar-container {
    width: 100px;
    height: 100px;
  }
  
  .user-details {
    width: 100%;
  }
  
  .username {
    font-size: 20px;
  }
  
  .user-bio {
    max-width: none;
    text-align: center;
  }
  
  .user-stats {
    justify-content: center;
    gap: 20px;
  }
  
  .profile-actions {
    width: 100%;
    flex-direction: row;
    justify-content: center;
    gap: 12px;
    min-width: auto;
  }
  
  .profile-actions .btn {
    flex: 1;
    min-width: 0;
    font-size: 13px;
    padding: 8px 12px;
  }
  
  .actions-right {
    flex-direction: column;
    gap: 8px;
  }
  
  .actions-right .btn {
    width: 100%;
    min-width: 0;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .tabs button {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .sort-controls {
    align-self: flex-end;
  }
  
  .avatar-edit-preview {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* 按钮区域优化 */
.profile-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
  flex-shrink: 0;
  min-width: 140px;
}

.profile-actions .btn {
  width: 100%;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
  border: none;
  cursor: pointer;
}

.profile-actions .btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.profile-actions .btn-outline {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.profile-actions .btn-outline:hover {
  background: #3498db;
  color: white;
}

.profile-actions .btn-primary {
  background: #3498db;
  color: white;
}

.profile-actions .btn-primary:hover {
  background: #2980b9;
}

.profile-actions .btn-warning {
  background: #f39c12;
  color: white;
}

.profile-actions .btn-warning:hover {
  background: #e67e22;
}

.profile-actions .btn-success {
  background: #27ae60;
  color: white;
}

.profile-actions .btn-success:hover {
  background: #229954;
}

/* 右侧操作按钮区域 */
.actions-right {
  margin-top: 16px;
  flex-direction: row;
  justify-content: flex-end;
  min-width: auto;
}

.actions-right .btn {
  width: auto;
  min-width: 120px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

/* 空状态按钮优化 */
.empty-state .btn {
  margin-top: 15px;
}

/* 已下架商品模态框样式 */
.offline-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.offline-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #f9f9f9;
}

.offline-item .item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  background: #f0f0f0;
}

.offline-item .item-info {
  flex: 1;
  min-width: 0;
}

.offline-item .item-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.offline-item .item-info .price {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #e74c3c;
}

.offline-item .item-info .status {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.offline-item .item-actions {
  flex-shrink: 0;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-success {
  background-color: #27ae60;
  color: white;
  border: none;
}

.btn-success:hover {
  background-color: #229954;
}

.profile-buy-requests.card {
  margin-bottom: 24px;
  padding: 18px 10px 10px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.10);
  background: #fff;
}
.buying-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.post-request-btn {
  padding: 4px 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background-color 0.2s;
}
.post-request-btn:hover {
  background-color: #3aa776;
}
.request-item {
  border: none;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}
.request-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  line-height: 1.4;
}
.request-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
.request-price {
  font-size: 1.2rem;
  color: #f56c6c;
  font-weight: bold;
}
.request-user-name {
  font-size: 0.9rem;
  color: #666;
}
.delete-btn {
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-left: 8px;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: #c0392b;
}
.loading-requests {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-request {
  height: 60px;
  background: #f0f0f0;
  border-radius: 4px;
  animation: skeleton-loading 1.5s infinite;
}
.empty-requests {
  text-align: center;
  padding: 12px;
  color: #999;
  font-size: 0.9rem;
}

/* 好友和黑名单功能样式 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .search-input {
    width: 150px;
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
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
  }
}

.buy-request-card {
  display: flex;
  align-items: flex-start;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 16px;
  margin-bottom: 18px;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.buy-request-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
  border-color: #3498db;
}
.buy-request-main {
  display: flex;
  align-items: flex-start;
  width: 100%;
}
.buy-request-img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  background: #f5f5f5;
  margin-right: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid #eee;
}
.buy-request-info {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}

.buy-request-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.buy-request-info .desc {
  color: #7f8c8d;
  font-size: 14px;
  line-height: 1.4;
  margin: 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.budget {
  font-size: 14px;
  margin: 4px 0;
}

.budget .price {
  color: #e74c3c;
  font-weight: bold;
  margin-left: 4px;
  font-size: 16px;
}

.buy-request-info .meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #95a5a6;
}

.buy-request-info .meta .time {
  flex: 1;
}

.buy-request-info .meta .likes {
  color: #3498db;
  font-weight: 500;
}
.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
  border-radius: 4px;
  margin-left: 12px;
}
.buy-request-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.buy-request-actions .btn {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-request-actions .btn-primary {
  background: #3498db;
  color: white;
}

.buy-request-actions .btn-primary:hover {
  background: #2980b9;
}

.buy-request-actions .btn-outline {
  background: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}

.buy-request-actions .btn-outline:hover {
  background: #3498db;
  color: white;
}

/* 商家认证相关样式 */
.merchant-status {
  margin: 10px 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.status-badge.status-approved {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.status-pending {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.status-badge.status-pending-verification {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.status-badge.status-normal {
  background: #e2e3e5;
  color: #6c757d;
  border: 1px solid #d6d8db;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
  border: none;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-success {
  background-color: #28a745;
  color: white;
  border: none;
}

.btn-success:hover {
  background-color: #218838;
}

/* 商家认证模态框样式 */
.merchant-status-info {
  text-align: center;
  padding: 20px;
}

.warning-message {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 15px;
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

.status-pending {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.status-pending i {
  font-size: 48px;
  color: #ffc107;
  margin-bottom: 16px;
}

.status-pending h4 {
  margin: 16px 0 8px 0;
  color: #856404;
}

.status-pending p {
  color: #856404;
  margin-bottom: 16px;
}

.status-pending-verification {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.status-pending-verification i {
  font-size: 48px;
  color: #dc3545;
  margin-bottom: 16px;
}

.status-pending-verification h4 {
  margin: 16px 0 8px 0;
  color: #721c24;
}

.status-pending-verification p {
  color: #721c24;
  margin-bottom: 16px;
}

.status-tips {
  text-align: left;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
  margin-top: 16px;
}

.status-tips p {
  margin: 4px 0;
  font-size: 14px;
  color: #6c757d;
}

.status-tips i {
  color: #17a2b8;
  margin-right: 6px;
}

.merchant-application-form {
  max-height: 60vh;
  overflow-y: auto;
}

.form-tips {
  background: #e7f3ff;
  border: 1px solid #b3d7ff;
  border-radius: 4px;
  padding: 12px;
  margin-top: 16px;
}

.form-tips p {
  margin: 0 0 8px 0;
  color: #0066cc;
  font-weight: 500;
}

.form-tips ul {
  margin: 8px 0 0 20px;
  color: #0066cc;
}

.form-tips li {
  margin: 4px 0;
}

.form-hint {
  font-size: 12px;
  color: #6c757d;
  margin-top: 4px;
}

/* 商家状态按钮样式 */
.merchant-status-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.merchant-status-buttons .btn {
  width: 100%;
}

/* 商家设置样式 */
.merchant-settings {
  max-height: 60vh;
  overflow-y: auto;
}

.merchant-status-display {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.status-note {
  margin: 8px 0 0 0;
  color: #6c757d;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-group {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.setting-group:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.setting-group h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.merchant-info {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
}

.merchant-info p {
  margin: 8px 0;
  color: #555;
  font-size: 14px;
}

.merchant-info strong {
  color: #333;
  font-weight: 600;
}
</style>