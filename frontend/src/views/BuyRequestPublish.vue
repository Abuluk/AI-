<template>
  <div class="container buy-request-publish">
    <h1 class="page-title">{{ editing ? '编辑求购信息' : '发布求购信息' }}</h1>
    <form class="buy-request-form" @submit.prevent="submitBuyRequest">
      <div class="form-group">
        <label>求购标题</label>
        <input v-model="form.title" placeholder="请输入求购标题" required />
      </div>
      <div class="form-group">
        <label>描述</label>
        <textarea v-model="form.description" placeholder="请输入描述" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label>预算(元)</label>
        <input v-model="form.budget" type="number" min="0" step="0.01" placeholder="请输入预算" />
      </div>
      <div class="form-group">
        <label>上传图片</label>
        <input type="file" multiple accept="image/*" @change="handleImageChange" />
        <div class="image-preview-list">
          <div v-for="(img, idx) in imagePreviews" :key="idx" class="image-preview">
            <img :src="img" />
            <button type="button" class="remove-image" @click="removeImage(idx)">×</button>
          </div>
        </div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-outline" @click="cancel">取消</button>
        <button type="submit" class="btn btn-primary">{{ editing ? '更新' : '发布' }}</button>
      </div>
      <div v-if="msg" class="msg">{{ msg }}</div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api'
export default {
  data() {
    return {
      editing: false,
      buyRequestId: null,
      form: {
        title: '',
        description: '',
        budget: '',
        images: []
      },
      msg: '',
      imageFiles: [],
      imagePreviews: []
    }
  },
  mounted() {
    // 检查是否是编辑模式
    const editId = this.$route.query.edit;
    if (editId) {
      this.editing = true;
      this.buyRequestId = editId;
      this.fetchBuyRequestData();
    }
  },
  methods: {
    // 获取求购信息数据（编辑时使用）
    async fetchBuyRequestData() {
      try {
        const response = await api.getBuyRequest(this.buyRequestId);
        const buyRequest = response.data;
        this.form = {
          title: buyRequest.title,
          description: buyRequest.description,
          budget: buyRequest.budget,
          images: buyRequest.images || []
        };
        // 显示现有图片
        if (buyRequest.images) {
          // 检查images的类型，如果是字符串则分割，如果是数组则直接使用
          let imageArray = [];
          if (typeof buyRequest.images === 'string') {
            imageArray = buyRequest.images.split(',').filter(img => img.trim());
          } else if (Array.isArray(buyRequest.images)) {
            imageArray = buyRequest.images;
          }
          
          this.imagePreviews = imageArray.map(img => {
            if (img.startsWith('http')) return img;
            return `http://localhost:8000/static/images/${img}`;
          });
        }
      } catch (error) {
        console.error('获取求购信息失败:', error);
        alert('无法加载求购信息');
      }
    },
    async handleImageChange(e) {
      const files = Array.from(e.target.files)
      this.imageFiles = files
      this.imagePreviews = files.map(file => URL.createObjectURL(file))
    },
    removeImage(index) {
      this.imagePreviews.splice(index, 1);
      if (index < this.imageFiles.length) {
        this.imageFiles.splice(index, 1);
      }
    },
    async uploadImages() {
      const uploaded = []
      for (const file of this.imageFiles) {
        const formData = new FormData()
        formData.append('file', file)
        const res = await api.uploadBuyRequestImage(formData)
        uploaded.push(res.data.url)
      }
      return uploaded
    },
    async submitBuyRequest() {
      try {
        let images = []
        if (this.imageFiles.length > 0) {
          images = await this.uploadImages()
        }
        
        if (this.editing) {
          // 编辑模式：更新求购信息
          await api.updateBuyRequest(this.buyRequestId, { ...this.form, images });
          this.msg = '更新成功！即将跳转...';
        } else {
          // 新建模式：创建求购信息
          await api.createBuyRequest({ ...this.form, images });
          this.msg = '发布成功！即将跳转...';
        }
        
        setTimeout(() => {
          this.$router.push('/profile?tab=buy_requests');
        }, 1000)
      } catch (e) {
        this.msg = this.editing ? '更新失败，请重试' : '发布失败，请重试';
      }
    },
    cancel() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.buy-request-publish {
  max-width: 500px;
  margin: 40px auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  padding: 32px 24px;
}
.page-title {
  font-size: 1.6rem;
  font-weight: bold;
  margin-bottom: 24px;
  text-align: center;
}
.buy-request-form .form-group {
  margin-bottom: 18px;
}
.buy-request-form label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}
.buy-request-form input,
.buy-request-form textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}
.form-actions {
  display: flex;
  gap: 18px;
  margin-top: 20px;
}
.btn.btn-outline {
  border: 1px solid #3498db;
  color: #3498db;
  background: #fff;
  padding: 10px 24px;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
}
.btn.btn-outline:hover {
  background: #eaf6fd;
}
.btn.btn-primary {
  background: #3498db;
  color: #fff;
  border: none;
  padding: 10px 24px;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
}
.btn.btn-primary:hover {
  background: #217dbb;
}
.msg {
  margin-top: 16px;
  color: #27ae60;
  text-align: center;
}
.image-preview-list {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
.image-preview {
  position: relative;
}
.image-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #eee;
}
.remove-image {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #e74c3c;
  color: white;
  border: none;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.remove-image:hover {
  background: #c0392b;
}
</style> 