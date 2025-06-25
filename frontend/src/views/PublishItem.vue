<template>
  <div class="container">
    <h1 class="page-title">{{ editing ? '编辑商品' : '发布商品' }}</h1>
    
    <div class="card">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>
            商品标题
            <span v-if="aiFilledFields.title" class="ai-field-badge" title="AI自动填充">
              <i class="fas fa-robot"></i> AI
            </span>
          </label>
          <input 
            type="text" 
            v-model="form.title" 
            placeholder="请输入商品标题" 
            required
            @input="clearAiBadge('title')"
            :data-ai-filled="aiFilledFields.title"
          >
        </div>
        
        <div class="form-group">
          <label>
            商品描述
            <span v-if="aiFilledFields.description" class="ai-field-badge" title="AI自动填充">
              <i class="fas fa-robot"></i> AI
            </span>
          </label>
          <textarea 
            v-model="form.description" 
            placeholder="请输入商品描述" 
            rows="5" 
            required
            @input="clearAiBadge('description')"
            :data-ai-filled="aiFilledFields.description"
          ></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>价格 (¥)</label>
            <input type="number" v-model="form.price" placeholder="0.00" required step="0.01" min="0" @input="onPriceInput">
          </div>
          
          <div class="form-group">
            <label>
              分类
              <span v-if="aiFilledFields.category" class="ai-field-badge" title="AI自动填充">
                <i class="fas fa-robot"></i> AI
              </span>
            </label>
            <select 
              v-model="form.category" 
              required
              @change="clearAiBadge('category')"
              :data-ai-filled="aiFilledFields.category"
            >
              <option value="">请选择分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label>商品图片</label>
          <div class="upload-area" @click="triggerFileInput">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>点击上传图片 (最多6张)</p>
            <p class="upload-tip">支持拖拽调整图片顺序</p>
            <input 
              type="file" 
              ref="fileInput" 
              multiple 
              accept="image/*" 
              name="files"
              @change="handleFileUpload"
              style="display: none"
            >
          </div>
          <div class="image-preview">
            <div 
              v-for="(image, index) in form.images" 
              :key="index" 
              class="preview-item"
              draggable="true"
              @dragstart="dragStart(index, $event)"
              @dragover.prevent
              @drop="drop(index, $event)"
              @dragenter.prevent
            >
              <img :src="image.url" alt="Preview">
              <button type="button" class="remove-btn" @click="removeImage(index)" title="删除图片">
                <i class="fas fa-times"></i>
              </button>
              <div class="image-overlay">
                <span class="image-index">{{ index + 1 }}</span>
              </div>
            </div>
            <div v-if="form.images.length === 0" class="no-images">
              <i class="fas fa-image"></i>
              <p>暂无图片</p>
            </div>
          </div>
          <!-- AI自动补充小按钮 -->
          <button
            type="button"
            class="ai-mini-btn"
            @click="autoFillAI"
            :disabled="form.images.length === 0 || form.images.length > 4 || aiLoading"
            :title="form.images.length === 0 ? '请先上传图片' : (form.images.length > 4 ? '最多支持4张图片' : 'AI自动识别图片并补全信息')"
          >
            <i class="fas fa-robot"></i>
            <span v-if="!aiLoading">AI自动补充</span>
            <span v-else>AI分析中...</span>
          </button>
          <div v-if="form.images.length > 4" class="ai-mini-warning">
            最多支持4张图片进行AI识别
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>所在地区</label>
            <input type="text" v-model="form.location" placeholder="例如: 北京朝阳区" required>
          </div>
          
          <div class="form-group">
            <label>商品状态</label>
            <select v-model="form.condition" required>
              <option value="">请选择商品状态</option>
              <option value="new">全新</option>
              <option value="like_new">几乎全新</option>
              <option value="good">轻微使用痕迹</option>
              <option value="fair">使用痕迹明显</option>
            </select>
          </div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn btn-outline wide-btn" @click="cancel">取消</button>
          <button type="submit" class="btn btn-primary">{{ editing ? '更新商品' : '发布商品' }}</button>
        </div>
        
        <!-- AI错误提示 -->
        <div v-if="aiError" class="ai-error-message">
          <i class="fas fa-exclamation-circle"></i>
          <span>{{ aiError }}</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { useAuthStore } from '@/store/auth' // 导入 Pinia store

export default {
  data() {
    return {
      editing: false,
      form: {
        title: '',
        description: '',
        price: '',
        category: '',
        location: '',
        condition: '',
        images: []
      },
      categories: [
        { id: 1, name: '手机数码' },
        { id: 2, name: '电脑办公' },
        { id: 3, name: '家用电器' },
        { id: 4, name: '服装鞋包' },
        { id: 5, name: '美妆护肤' },
        { id: 6, name: '图书文娱' },
        { id: 7, name: '运动户外' },
        { id: 8, name: '家居家装' }
      ],
      aiLoading: false,
      aiError: null,
      aiFilledFields: {
        title: false,
        description: false,
        category: false,
        condition: false
      }
    }
  },
  mounted() {
    // 页面加载时重置AI标识
    this.resetAiBadges();
  },
  methods: {
    // 获取商品数据方法（编辑时使用）
    async fetchItemData() {
      try {
        const response = await api.getItem(this.itemId)
        const item = response.data
        this.form = {
          title: item.title,
          description: item.description,
          price: item.price,
          category: item.category,
          location: item.location,
          condition: item.condition,
          images: item.images ? item.images.split(',').map(url => ({ url })) : []
        }
      } catch (error) {
        console.error('获取商品数据失败:', error)
        alert('无法加载商品数据')
      }
    },
    
    // 表单提交方法
    async submitForm() {
  try {
    const formData = new FormData();
    formData.append('title', this.form.title);
    formData.append('description', this.form.description);
    formData.append('price', this.form.price);
    formData.append('category', this.form.category);
    formData.append('location', this.form.location);
    formData.append('condition', this.form.condition);
    
    // 添加图片文件
    this.form.images.forEach((img, index) => {
      if (img.file) {
        formData.append('images', img.file, `image_${index}.jpg`);
      }
    });

    // 调用API创建商品
    const response = await api.createItem(formData);
    const newItem = response.data;
    
    // 更新用户状态
    const authStore = useAuthStore();
    if (authStore.user) {
      authStore.user.items_count += 1;
    }
    // 单独处理用户信息刷新，不影响主流程
    try {
      await authStore.fetchCurrentUser();
    } catch (fetchError) {
      console.error('刷新用户信息失败:', fetchError);
    }
    // 无论用户信息刷新是否成功，都跳转到个人主页
    this.$router.push({ path: '/profile' });
    // 显示成功提示
    alert('发布成功！');
  } catch (error) {
    console.error('发布失败:', error);
    let errorMessage = '发布失败，请重试';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    alert(errorMessage);
  }
},
    
    // 触发文件选择
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    // 处理文件上传
    handleFileUpload(e) {
      const files = e.target.files
      if (!files || files.length === 0) return
      
      if (this.form.images.length + files.length > 6) {
        alert('最多只能上传6张图片')
        return
      }
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        
        // 验证文件类型
        if (!file.type.match('image.*')) {
          alert(`文件 "${file.name}" 不是有效的图片格式`)
          continue
        }
        
        // 验证文件大小（限制为5MB）
        if (file.size > 5 * 1024 * 1024) {
          alert(`文件 "${file.name}" 太大，请选择小于5MB的图片`)
          continue
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          // 保证file对象被保存
          this.form.images.push({
            file: file,
            url: e.target.result
          })
          console.log('图片已加入form.images:', file)
        }
        reader.onerror = () => {
          alert(`读取文件 "${file.name}" 失败`)
        }
        reader.readAsDataURL(file)
      }
      
      // 重置input以允许选择相同文件
      this.$refs.fileInput.value = null
    },
    
    // 移除图片
    removeImage(index) {
      if (confirm('确定要删除这张图片吗？')) {
        // 释放内存中的文件对象
        if (this.form.images[index].file) {
          URL.revokeObjectURL(this.form.images[index].url);
        }
        this.form.images.splice(index, 1);
      }
    },
    
    // 拖拽开始
    dragStart(index, event) {
      event.dataTransfer.setData('text/plain', index);
      event.target.style.opacity = '0.5';
    },
    
    // 拖拽放置
    drop(index, event) {
      event.preventDefault();
      const draggedIndex = parseInt(event.dataTransfer.getData('text/plain'));
      event.target.style.opacity = '1';
      
      if (draggedIndex !== index) {
        // 交换图片位置
        const temp = this.form.images[draggedIndex];
        this.form.images.splice(draggedIndex, 1);
        this.form.images.splice(index, 0, temp);
      }
    },
    
    // 取消按钮功能
    cancel() {
      // 返回上一页或首页
      this.$router.go(-1)
    },
    onPriceInput(e) {
      // 限制最多两位小数
      let value = e.target.value;
      if (value && value.includes('.')) {
        const [intPart, decPart] = value.split('.');
        if (decPart.length > 2) {
          value = intPart + '.' + decPart.slice(0, 2);
          this.form.price = value;
        }
      }
    },
    async autoFillAI() {
      console.log('autoFillAI被调用');
      const files = this.form.images.filter(img => img.file).map(img => img.file);
      console.log('AI补全上传files:', files);
      
      if (!files.length) {
        alert('请先上传至少一张商品图片');
        return;
      }
      
      if (files.length > 4) {
        alert('最多只能选择4张图片用于AI补全');
        return;
      }
      
      this.aiLoading = true;
      this.aiError = null;
      
      // 重置所有AI标识
      this.resetAiBadges();
      
      try {
        console.log('准备发起AI补全请求');
        const response = await api.aiAutoCompleteItemByImage(files);
        console.log('AI补全请求已返回:', response);
        
        if (response.data.success && response.data.data) {
          const ai = response.data.data;
          console.log('AI返回数据:', ai);
          
          // 根据AI返回的数据更新表单
          if (ai.title && ai.title !== '未知') {
            this.form.title = ai.title;
            this.aiFilledFields.title = true;
          }
          
          if (ai.description && ai.description !== '未知') {
            this.form.description = ai.description;
            this.aiFilledFields.description = true;
          }
          
          if (ai.category && ai.category !== '未知') {
            // 确保category是数字类型
            const categoryId = parseInt(ai.category);
            if (!isNaN(categoryId) && categoryId >= 1 && categoryId <= 8) {
              this.form.category = categoryId.toString();
              this.aiFilledFields.category = true;
            }
          }
          
          if (ai.condition && ai.condition !== '未知') {
            this.form.condition = ai.condition;
          }
          
          // 显示价格建议（如果有的话）
          if (ai.price_suggestion && ai.price_suggestion !== '未知') {
            alert(`AI建议价格范围：${ai.price_suggestion}\n请根据实际情况调整价格。`);
          }
          
          // 显示AI补全成功的详细信息
          const filledFields = [];
          if (ai.title && ai.title !== '未知') filledFields.push('标题');
          if (ai.description && ai.description !== '未知') filledFields.push('描述');
          if (ai.category && ai.category !== '未知') filledFields.push('分类');
          if (ai.condition && ai.condition !== '未知') filledFields.push('状态');
          
          if (filledFields.length > 0) {
            alert(`🎉 AI自动补全成功！\n\n已自动填充：${filledFields.join('、')}\n\n请核对并完善商品信息。`);
          } else {
            alert('🤖 AI已分析图片，但未能识别出具体信息。\n\n请手动填写商品信息，或上传更清晰的商品图片重试。');
          }
        } else {
          this.aiError = response.data.message || 'AI自动补全失败';
          alert('AI自动补全失败：' + this.aiError);
        }
      } catch (error) {
        console.error('AI服务异常:', error);
        let errorMessage = 'AI服务异常，请稍后重试';
        
        if (error.response) {
          // 服务器返回了错误响应
          if (error.response.data && error.response.data.message) {
            errorMessage = error.response.data.message;
          } else if (error.response.status === 413) {
            errorMessage = '图片文件过大，请选择更小的图片';
          } else if (error.response.status === 400) {
            errorMessage = '请求参数错误，请检查图片格式';
          } else if (error.response.status === 500) {
            errorMessage = '服务器内部错误，请稍后重试';
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          errorMessage = '网络连接失败，请检查网络连接';
        } else {
          // 其他错误
          errorMessage = error.message || '未知错误';
        }
        
        this.aiError = errorMessage;
        alert('AI服务异常: ' + errorMessage);
      } finally {
        this.aiLoading = false;
      }
    },
    clearAiBadge(field) {
      this.aiFilledFields[field] = false;
    },
    resetAiBadges() {
      this.aiFilledFields = {
        title: false,
        description: false,
        category: false,
        condition: false
      };
    }
  }
}
</script>

<style scoped>
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid var(--border);
  border-radius: 5px;
  font-size: 1rem;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.upload-area {
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: var(--primary);
  background-color: rgba(52, 152, 219, 0.05);
}

.upload-area i {
  font-size: 3rem;
  color: var(--primary);
  margin-bottom: 15px;
}

.upload-area p {
  color: var(--text-light);
}

.upload-tip {
  color: var(--text-light);
  font-size: 0.8rem;
  margin-top: 10px;
}

.image-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 15px;
}

.preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #eee;
  transition: all 0.3s ease;
  cursor: move;
}

.preview-item:hover {
  border-color: #3498db;
  transform: scale(1.05);
}

.preview-item:active {
  cursor: grabbing;
}

.preview-item.dragging {
  opacity: 0.5;
  transform: scale(1.1);
  z-index: 1000;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: rgba(231, 76, 60, 0.9);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  z-index: 10;
}

.remove-btn:hover {
  background-color: rgba(231, 76, 60, 1);
  transform: scale(1.1);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 5px;
  display: flex;
  justify-content: center;
}

.image-index {
  color: white;
  font-size: 12px;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

.no-images {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  color: #999;
  font-size: 12px;
}

.no-images i {
  font-size: 24px;
  margin-bottom: 5px;
}

.no-images p {
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  align-items: center;
}

.btn.wide-btn {
  min-width: 110px;
  height: 56px;
  font-size: 1.1rem;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  .btn.wide-btn {
    width: 100%;
    min-width: unset;
    height: 48px;
    font-size: 1rem;
  }
}

.ai-error {
  color: #e74c3c;
  margin-top: 10px;
  text-align: center;
}

.ai-suggestion-area {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.ai-suggestion-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  pointer-events: none;
}

.ai-suggestion-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.ai-suggestion-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.ai-suggestion-header i {
  font-size: 1.8rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-right: 12px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.ai-suggestion-header span {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.ai-badge {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
  60% { transform: translateY(-3px); }
}

.ai-suggestion-content {
  text-align: left;
}

.ai-suggestion-content p {
  margin-bottom: 15px;
  color: #34495e;
  font-weight: 500;
}

.ai-suggestion-content ul {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.ai-suggestion-content li {
  padding: 8px 0;
  color: #555;
  position: relative;
  padding-left: 25px;
}

.ai-suggestion-content li::before {
  content: '✨';
  position: absolute;
  left: 0;
  top: 8px;
  font-size: 14px;
}

.ai-fill-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 15px 25px;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.ai-fill-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.ai-fill-btn:active:not(:disabled) {
  transform: translateY(0);
}

.ai-fill-btn.loading {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  cursor: not-allowed;
}

.ai-fill-btn.disabled {
  background: linear-gradient(135deg, #bdc3c7, #95a5a6);
  cursor: not-allowed;
  opacity: 0.7;
}

.ai-btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.ai-btn-content i {
  font-size: 1.2rem;
}

.ai-progress {
  height: 4px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 12px;
  position: relative;
}

.ai-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #fff, #f0f0f0);
  border-radius: 2px;
  animation: progress 2s ease-in-out infinite;
  width: 30%;
}

@keyframes progress {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

.ai-warning {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 15px;
  padding: 10px;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 6px;
  border-left: 4px solid #e74c3c;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-warning i {
  font-size: 1rem;
}

.ai-error-message {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-suggestion-area {
    padding: 15px;
    margin-top: 15px;
  }
  
  .ai-suggestion-card {
    padding: 20px;
  }
  
  .ai-suggestion-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .ai-suggestion-header span {
    font-size: 1.1rem;
  }
  
  .ai-fill-btn {
    padding: 12px 20px;
    font-size: 1rem;
  }
}

.ai-field-badge {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  margin-left: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  animation: aiBadgePulse 2s infinite;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ai-field-badge i {
  font-size: 0.6rem;
}

@keyframes aiBadgePulse {
  0%, 100% { 
    transform: scale(1);
    opacity: 1;
  }
  50% { 
    transform: scale(1.05);
    opacity: 0.8;
  }
}

/* 为AI填充的字段添加特殊样式 */
.form-group input[data-ai-filled="true"],
.form-group textarea[data-ai-filled="true"],
.form-group select[data-ai-filled="true"] {
  border-color: #667eea;
  background-color: rgba(102, 126, 234, 0.05);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.ai-mini-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  margin-top: 10px;
}

.ai-mini-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.ai-mini-btn:active:not(:disabled) {
  transform: translateY(0);
}

.ai-mini-btn.loading {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  cursor: not-allowed;
}

.ai-mini-btn.disabled {
  background: linear-gradient(135deg, #bdc3c7, #95a5a6);
  cursor: not-allowed;
  opacity: 0.7;
}

.ai-mini-warning {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 10px;
  padding: 10px;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 6px;
  border-left: 4px solid #e74c3c;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-mini-warning i {
  font-size: 1rem;
}
</style>