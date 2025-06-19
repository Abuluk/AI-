import { createApp } from 'vue'
import { createPinia } from 'pinia' // 导入 Pinia
import App from './App.vue'
import router from './router'  // Import router

const app = createApp(App)

// 创建 Pinia 实例并挂载
app.use(createPinia())

app.use(router)  // Use Vue Router
app.mount('#app')  // Mount the app