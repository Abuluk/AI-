<template>
  <div class="container buy-request-publish">
    <h1 class="page-title">发布求购信息</h1>
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
          </div>
        </div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-outline" @click="cancel">取消</button>
        <button type="submit" class="btn btn-primary">发布</button>
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
  methods: {
    async handleImageChange(e) {
      const files = Array.from(e.target.files)
      this.imageFiles = files
      this.imagePreviews = files.map(file => URL.createObjectURL(file))
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
        await api.createBuyRequest({ ...this.form, images })
        this.msg = '发布成功！即将跳转...'
        setTimeout(() => {
          this.$router.push('/')
        }, 1000)
      } catch (e) {
        this.msg = '发布失败，请重试'
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
.image-preview img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #eee;
}
</style> 