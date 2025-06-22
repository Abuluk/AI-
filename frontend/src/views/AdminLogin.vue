<template>
  <div class="admin-login-container">
    <div class="login-card">
      <div class="login-header">
        <i class="fas fa-shield-alt"></i>
        <h1>管理员登录</h1>
        <p>请输入您的管理员凭据</p>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="identifier">账号</label>
          <input 
            id="identifier"
            type="text" 
            v-model="identifier"
            placeholder="请输入管理员手机号/邮箱"
            required
            class="form-control"
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            id="password"
            type="password" 
            v-model="password"
            placeholder="请输入密码"
            required
            class="form-control"
          >
        </div>
        <button type="submit" class="btn-login" :disabled="loading">
          <span v-if="loading">正在登录...</span>
          <span v-else>登 录</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const identifier = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');

const router = useRouter();
const authStore = useAuthStore();

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    // 调用登录接口
    await authStore.login({
      identifier: identifier.value,
      password: password.value,
    });
    
    // 登录成功后，检查是否是管理员
    if (authStore.user && authStore.user.is_admin) {
      // 是管理员，跳转到后台
      router.push('/admin');
    } else {
      // 不是管理员，登出并显示错误
      await authStore.logout();
      errorMessage.value = '您没有管理员权限，请使用管理员账号登录。';
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查您的账号和密码。';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  text-align: center;
}
.login-header {
  margin-bottom: 30px;
}
.login-header .fa-shield-alt {
  font-size: 3rem;
  color: #1890ff;
}
.login-header h1 {
  font-size: 1.8rem;
  margin: 15px 0 10px;
}
.login-header p {
  color: #888;
}
.form-group {
  margin-bottom: 20px;
  text-align: left;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}
.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 1rem;
  transition: all 0.3s;
}
.form-control:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  outline: none;
}
.btn-login {
  width: 100%;
  padding: 12px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}
.btn-login:hover {
  background-color: #40a9ff;
}
.btn-login:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}
.error-message {
  color: #f5222d;
  background: #fff1f0;
  border: 1px solid #ffa39e;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}
</style> 