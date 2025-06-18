<template>
  <div class="container">
    <div class="auth-container">
      <div class="auth-card card">
        <div class="auth-header">
          <h2>{{ isLoginMode ? '登录' : '注册' }}</h2>
          <p>{{ isLoginMode ? '欢迎回来' : '创建新账户' }}</p>
        </div>
        
        <form @submit.prevent="submitForm">
          <div v-if="!isLoginMode" class="form-group">
            <label>用户名</label>
            <input type="text" v-model="form.username" placeholder="设置您的用户名" required>
          </div>
          
          <div class="form-group">
            <label>手机号</label>
            <input type="tel" v-model="form.phone" placeholder="请输入手机号" required>
          </div>
          
          <div class="form-group">
            <label>{{ isLoginMode ? '密码' : '设置密码' }}</label>
            <div class="password-input">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                v-model="form.password" 
                placeholder="请输入密码" 
                required
              >
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
          </div>
          
          <div v-if="!isLoginMode" class="form-group">
            <label>确认密码</label>
            <input 
              type="password" 
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
          
          <button type="submit" class="btn btn-primary auth-btn">
            {{ isLoginMode ? '登录' : '注册' }}
          </button>
        </form>
        
        <div class="auth-footer">
          <p>
            {{ isLoginMode ? '还没有账号?' : '已有账号?' }}
            <a href="#" @click.prevent="toggleMode">{{ isLoginMode ? '立即注册' : '立即登录' }}</a>
          </p>
          
          <div class="social-login">
            <p>其他登录方式</p>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoginMode: true,
      showPassword: false,
      rememberMe: false,
      form: {
        username: '',
        phone: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    toggleMode() {
      this.isLoginMode = !this.isLoginMode
      // 重置表单
      this.form = {
        username: '',
        phone: '',
        password: '',
        confirmPassword: ''
      }
    },
    submitForm() {
      if (!this.isLoginMode && this.form.password !== this.form.confirmPassword) {
        alert('两次输入的密码不一致')
        return
      }
      
      // 这里应该发送API请求
      console.log('提交表单:', this.form)
      alert(this.isLoginMode ? '登录成功' : '注册成功')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 500px;
  margin: 40px auto;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.auth-header p {
  color: var(--text-light);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--border);
  border-radius: 5px;
  font-size: 1rem;
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.forgot-password {
  color: var(--primary);
  text-decoration: none;
}

.auth-btn {
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
}

.auth-footer {
  margin-top: 30px;
  text-align: center;
}

.auth-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
}

.social-login {
  margin-top: 30px;
  border-top: 1px solid var(--border);
  padding-top: 30px;
}

.social-login p {
  margin-bottom: 15px;
  color: var(--text-light);
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.social-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.social-btn:hover {
  transform: translateY(-5px);
}

.social-btn.wechat {
  background-color: #07C160;
  color: white;
}

.social-btn.qq {
  background-color: #12B7F5;
  color: white;
}

.social-btn.weibo {
  background-color: #E6162D;
  color: white;
}
</style>