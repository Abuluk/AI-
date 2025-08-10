import { createApp } from 'vue'
import { createPinia } from 'pinia' // 导入 Pinia
import App from './App.vue'
import router from './router'  // Import router
import { useAuthStore } from './store/auth' // 导入认证store

const app = createApp(App)

// 创建 Pinia 实例并挂载
const pinia = createPinia()
app.use(pinia)

// 初始化认证状态
const authStore = useAuthStore()
authStore.initialize()

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否需要认证
  if (to.path.startsWith('/admin') && to.name !== 'AdminLogin') {
    // 如果token不存在，直接跳转到管理员登录页
    if (!authStore.token) {
      return next({ name: 'AdminLogin' })
    }
    
    // 如果用户信息不存在，尝试获取
    if (!authStore.user) {
      try {
        await authStore.fetchCurrentUser()
      } catch (e) {
        // 获取失败，可能是无效token，跳转到登录页
        return next({ name: 'AdminLogin' })
      }
    }
    
    // 检查是否是管理员
    if (!authStore.user.is_admin) {
      alert('您没有管理员权限！');
      return next({ path: '/' });
    }
  }
  
  next()
})

app.use(router)  // Use Vue Router
app.mount('#app')  // Mount the app