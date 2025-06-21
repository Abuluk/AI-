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
            <input type="number" v-model="form.price" placeholder="0.00" required>
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
            <div v-for="(image, index) in form.images" :key="index" class="preview-item">
              <img :src="image.url" alt="Preview">
              <button type="button" class="remove-btn" @click="removeImage(index)">
                <i class="fas fa-times"></i>
              </button>
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
      if (this.form.images.length + files.length > 6) {
        alert('最多只能上传6张图片')
        return
      }
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        if (!file.type.match('image.*')) {
          continue
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          this.form.images.push({
            file: file,
            url: e.target.result
          })
        }
        reader.readAsDataURL(file)
      }
      
      // 重置input以允许选择相同文件
      this.$refs.fileInput.value = null
    },
    
    // 移除图片
    removeImage(index) {
      this.form.images.splice(index, 1)
    },
    
    // 取消按钮功能
    cancel() {
      // 返回上一页或首页
      this.$router.go(-1)
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
  border-radius: 5px;
  overflow: hidden;
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
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
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