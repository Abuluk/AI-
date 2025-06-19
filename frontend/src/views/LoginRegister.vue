<template>
  <div class="login-register-container">
    <div class="brand-header">
      <div class="logo">
        <i class="fas fa-gem"></i>
        好物精选
      </div>
      <p class="tagline">发现生活之美，精选品质好物</p>
    </div>
    
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h2>{{ isLoginMode ? '欢迎回来' : '创建账户' }}</h2>
          <p>{{ isLoginMode ? '请登录您的账户继续' : '注册新账户享受更多权益' }}</p>
          
          <div class="mode-switch">
            <div 
              class="mode-btn" 
              :class="{ active: isLoginMode }"
              @click="setLoginMode(true)"
            >
              登录
            </div>
            <div 
              class="mode-btn" 
              :class="{ active: !isLoginMode }"
              @click="setLoginMode(false)"
            >
              注册
            </div>
          </div>
        </div>
        
        <div v-if="authStore.error" class="error-message">
          <i class="fas fa-exclamation-circle"></i> {{ authStore.error }}
        </div>
        
        <div class="form-container">
          <form @submit.prevent="submitForm">
            <div v-if="!isLoginMode" class="form-group">
              <label class="form-label">用户名</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="form.username" 
                placeholder="设置您的用户名"
                required
              >
            </div>
            
            <div v-if="!isLoginMode" class="form-group">
              <label class="form-label">邮箱</label>
              <input 
                type="email" 
                class="form-control" 
                v-model="form.email" 
                placeholder="请输入邮箱"
                required
              >
            </div>
            
            <div class="form-group">
              <label class="form-label">手机号</label>
              <input 
                type="tel" 
                class="form-control" 
                v-model="form.phone" 
                placeholder="请输入手机号"
                required
              >
            </div>
            
            <div class="form-group">
              <label class="form-label">{{ isLoginMode ? '密码' : '设置密码' }}</label>
              <div class="password-input">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  v-model="form.password" 
                  placeholder="请输入密码"
                  required
                  @input="checkPasswordStrength"
                >
                <button 
                  type="button" 
                  class="toggle-password" 
                  @click="showPassword = !showPassword"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="!isLoginMode" class="password-strength">
                <div class="strength-meter" :class="passwordStrength"></div>
              </div>
            </div>
            
            <div v-if="!isLoginMode" class="form-group">
              <label class="form-label">确认密码</label>
              <input 
                type="password" 
                class="form-control" 
                v-model="form.confirmPassword" 
                placeholder="请再次输入密码"
                required
              >
            </div>
            
            <div v-if="isLoginMode" class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="rememberMe"> 记住我
              </label>
              <router-link to="/forgot-password" class="forgot-password">忘记密码?</router-link>
            </div>
            
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="authStore.loading"
            >
              <span v-if="authStore.loading">
                <i class="fas fa-spinner spinner"></i> 处理中...
              </span>
              <span v-else>
                {{ isLoginMode ? '登录' : '立即注册' }}
              </span>
            </button>
          </form>
          
          <div class="divider">
            <div class="divider-text">或使用社交账号登录</div>
          </div>
          
          <div class="social-login">
            <div class="social-title">一键登录更便捷</div>
            <div class="social-icons">
              <button class="social-btn wechat">
                <i class="fab fa-weixin"></i>
              </button>
              <button class="social-btn qq">
                <i class="fab fa-qq"></i>
              </button>
              <button class="social-btn weibo">
                <i class="fab fa-weibo"></i>
              </button>
            </div>
          </div>
          
          <div class="auth-footer">
            <p>
              {{ isLoginMode ? '还没有账号?' : '已有账号?' }}
              <a href="#" @click.prevent="toggleMode">{{ isLoginMode ? '立即注册' : '立即登录' }}</a>
            </p>
            <p style="margin-top: 10px;">
              <router-link to="/terms">用户协议</router-link> 和 
              <router-link to="/privacy">隐私政策</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const router = useRouter()

const isLoginMode = ref(true)
const showPassword = ref(false)
const rememberMe = ref(false)
const passwordStrength = ref('')

const form = reactive({
  username: '',
  email: '',
  phone: '',
  password: '',
  confirmPassword: ''
})

const setLoginMode = (isLogin) => {
  isLoginMode.value = isLogin
  authStore.error = null
}

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  // 重置表单
  form.username = ''
  form.email = ''
  form.phone = ''
  form.password = ''
  form.confirmPassword = ''
  authStore.error = null
}

const checkPasswordStrength = () => {
  if (!form.password) {
    passwordStrength.value = ''
    return
  }
  
  const strength = calculatePasswordStrength(form.password)
  passwordStrength.value = strength
}

const calculatePasswordStrength = (password) => {
  if (password.length < 6) return 'weak'
  
  let score = 0
  // 包含数字
  if (/\d/.test(password)) score++
  // 包含小写字母
  if (/[a-z]/.test(password)) score++
  // 包含大写字母
  if (/[A-Z]/.test(password)) score++
  // 包含特殊字符
  if (/[^a-zA-Z0-9]/.test(password)) score++
  
  if (score < 2) return 'weak'
  if (score < 4) return 'medium'
  return 'strong'
}

const submitForm = async () => {
  if (isLoginMode.value) {
    try {
      await authStore.login({
        identifier: form.username || form.phone,
        password: form.password
      })
      router.push('/')
    } catch (error) {
      console.error('登录失败:', error)
    }
  } else {
    if (form.password !== form.confirmPassword) {
      authStore.error = '两次输入的密码不一致'
      return
    }
    
    const strength = calculatePasswordStrength(form.password)
    if (strength === 'weak') {
      authStore.error = '密码强度不足，请使用更复杂的密码'
      return
    }
    
    try {
  await authStore.register({
    username: form.username,
    email: form.email,
    phone: form.phone,
    password: form.password
  })
  router.push('/')
} catch (error) {
  // 处理Axios等HTTP客户端的错误
  if (error.response) {
    console.error('API错误响应:', error.response.data)
    console.error('状态码:', error.response.status)
    console.error('请求头:', error.response.headers)
    
    // 处理常见错误
    if (error.response.status === 400) {
      console.error('输入验证失败:', error.response.data.errors)
    } else if (error.response.status === 409) {
      console.error('用户名或邮箱已存在')
    }
  } 
  // 处理网络错误
  else if (error.request) {
    console.error('网络请求已发出，但未收到响应:', error.request)
  } 
  // 处理其他错误
  else {
    console.error('注册过程中发生错误:', error.message)
  }
}
  }
}
</script>

<style scoped>
.login-register-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 20px;
  color: #333;
  line-height: 1.6;
  width: 100%;
}

:root {
  --primary: #42b983;
  --primary-dark: #3aa776;
  --secondary: #ff6b6b;
  --text: #333;
  --text-light: #666;
  --border: #e0e0e0;
  --bg-light: #f8f9fa;
  --bg-card: #ffffff;
  --shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  --success: #4caf50;
  --error: #e74c3c;
}

.brand-header {
  text-align: center;
  margin-bottom: 30px;
  width: 100%;
}

.logo {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo i {
  margin-right: 10px;
  font-size: 2.2rem;
}

.tagline {
  font-size: 1.1rem;
  color: var(--text-light);
  max-width: 500px;
  margin: 0 auto;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 800px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  background: var(--bg-card);
}

.auth-card {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.auth-header p {
  font-size: 1rem;
  color: var(--text-light);
}

.mode-switch {
  display: flex;
  background: var(--bg-light);
  border-radius: 50px;
  padding: 5px;
  margin: 20px auto;
  max-width: 300px;
}

.mode-btn {
  flex: 1;
  padding: 12px;
  text-align: center;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mode-btn.active {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 10px rgba(66, 185, 131, 0.3);
}

.form-container {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text);
  transition: all 0.3s ease;
}

.input-group {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid var(--border);
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: var(--bg-light);
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.2);
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  font-size: 1.1rem;
}

.password-strength {
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.strength-meter {
  height: 100%;
  width: 0;
  transition: width 0.4s ease;
}

.weak { background: var(--error); width: 30%; }
.medium { background: #ffca28; width: 60%; }
.strong { background: var(--success); width: 100%; }

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 25px 0;
}

.remember-me {
  display: flex;
  align-items: center;
  font-size: 0.95rem;
  color: var(--text-light);
}

.remember-me input {
  margin-right: 8px;
}

.forgot-password {
  color: var(--primary);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.btn {
  display: block;
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 15px rgba(66, 185, 131, 0.4);
}

.btn-primary:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(66, 185, 131, 0.5);
}

.btn-primary:disabled {
  background: #a0d9bb;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.divider {
  display: flex;
  align-items: center;
  margin: 30px 0;
  color: var(--text-light);
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
}

.divider-text {
  padding: 0 15px;
  font-size: 0.9rem;
}

.social-login {
  text-align: center;
}

.social-title {
  font-size: 1rem;
  color: var(--text-light);
  margin-bottom: 15px;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.social-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;
}

.social-btn.wechat {
  background: #09bb07;
}

.social-btn.qq {
  background: #12b7f5;
}

.social-btn.weibo {
  background: #e6162d;
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.auth-footer {
  margin-top: 25px;
  text-align: center;
  font-size: 0.95rem;
  color: var(--text-light);
}

.auth-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  margin-left: 5px;
  transition: color 0.2s;
}

.auth-footer a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.error-message {
  color: var(--error);
  background-color: rgba(231, 76, 60, 0.1);
  padding: 12px 15px;
  border-radius: 8px;
  margin-top: 15px;
  font-size: 0.95rem;
  border-left: 3px solid var(--error);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .auth-card {
    padding: 30px 20px;
  }
  
  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .forgot-password {
    align-self: flex-end;
  }
  
  .logo {
    font-size: 2rem;
  }
  
  .auth-header h2 {
    font-size: 1.6rem;
  }
}

.spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>