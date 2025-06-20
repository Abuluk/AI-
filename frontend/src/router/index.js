import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/Home.vue') },
  { path: '/item/:id', name: 'ItemDetail', component: () => import('@/views/ItemDetail.vue'), props: true },
  { path: '/publish',name: 'Publish', component: () => import('@/views/PublishItem.vue') },
  { path: '/login', component: () => import('@/views/LoginRegister.vue') },
  { path: '/profile',name: 'Profile', component: () => import('@/views/Profile.vue') },
  { path: '/messages', component: () => import('@/views/MessagesList.vue') },
  { path: '/chat/:id', name: 'Chat', component: () => import('@/views/Chat.vue'), props: true }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router