<template>
  <div class="container">
    <h1 class="page-title">{{ editing ? '编辑商品' : '发布商品' }}</h1>
    
    <div class="card">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label>商品标题</label>
          <input type="text" v-model="form.title" placeholder="请输入商品标题" required>
        </div>
        
        <div class="form-group">
          <label>商品描述</label>
          <textarea v-model="form.description" placeholder="请输入商品描述" rows="5" required></textarea>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>价格 (¥)</label>
            <input type="number" v-model="form.price" placeholder="0.00" required step="0.01" min="0" @input="onPriceInput">
          </div>
          
          <div class="form-group">
            <label>分类</label>
            <select v-model="form.category" required>
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
          <button type="button" class="btn btn-outline" @click="cancel">取消</button>
          <button type="submit" class="btn btn-primary">{{ editing ? '更新商品' : '发布商品' }}</button>
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
      ]
    }
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
          this.form.images.push({
            file: file,
            url: e.target.result
          })
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
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
}
</style>