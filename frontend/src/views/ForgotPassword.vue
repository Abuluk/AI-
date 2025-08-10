<template>
  <div class="forgot-password-container card">
    <h2>找回密码</h2>
    <div class="form-group">
      <label>邮箱</label>
      <input v-model="email" type="email" placeholder="请输入注册邮箱" />
    </div>
    <div class="form-group code-group">
      <label>验证码</label>
      <input v-model="code" type="text" placeholder="请输入验证码" />
      <button class="btn btn-outline" :disabled="sendingCode || !email" @click="sendCode">
        {{ sendingCode ? countdown + 's后重试' : '获取验证码' }}
      </button>
    </div>
    <div class="form-group">
      <label>新密码</label>
      <input v-model="newPassword" type="password" placeholder="请输入新密码" />
    </div>
    <button class="btn btn-primary" :disabled="loading" @click="resetPassword">重置密码</button>
    <div v-if="message" class="message">{{ message }}</div>
  </div>
</template>

<script>
import api from '@/services/api'
export default {
  data() {
    return {
      email: '',
      code: '',
      newPassword: '',
      sendingCode: false,
      countdown: 60,
      timer: null,
      loading: false,
      message: ''
    }
  },
  methods: {
    async sendCode() {
      if (!this.email) return;
      this.sendingCode = true;
      this.message = '';
      try {
        await api.requestPasswordReset({ account: this.email });
        this.message = '验证码已发送，请查收邮箱';
        this.startCountdown();
      } catch (e) {
        this.message = e.response?.data?.detail || '发送失败';
        this.sendingCode = false;
      }
    },
    startCountdown() {
      this.countdown = 60;
      this.timer = setInterval(() => {
        this.countdown--;
        if (this.countdown <= 0) {
          clearInterval(this.timer);
          this.sendingCode = false;
        }
      }, 1000);
    },
    async resetPassword() {
      if (!this.email || !this.code || !this.newPassword) {
        this.message = '请填写完整信息';
        return;
      }
      this.loading = true;
      this.message = '';
      try {
        await api.resetPassword({ account: this.email, code: this.code, new_password: this.newPassword });
        this.message = '密码重置成功，请前往登录';
        setTimeout(() => this.$router.push('/login'), 1500);
      } catch (e) {
        this.message = e.response?.data?.detail || '重置失败';
      } finally {
        this.loading = false;
      }
    }
  },
  beforeDestroy() {
    if (this.timer) clearInterval(this.timer);
  }
}
</script>

<style scoped>
.forgot-password-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 30px 30px 20px 30px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-group {
  margin-bottom: 18px;
}
.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #666;
}
.form-group input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}
.code-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.btn {
  min-width: 90px;
}
.message {
  margin-top: 15px;
  color: #d9534f;
  font-size: 0.95rem;
}
</style> 