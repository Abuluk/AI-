import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/views/Home.vue') },
  { path: '/item/:id', name: 'ItemDetail', component: () => import('@/views/ItemDetail.vue'), props: true },
  { path: '/publish',name: 'Publish', component: () => import('@/views/PublishItem.vue') },
  { path: '/publish-buy-request', name: 'PublishBuyRequest', component: () => import('@/views/BuyRequestPublish.vue') },
  { path: '/login', component: () => import('@/views/LoginRegister.vue') },
  { path: '/profile',name: 'Profile', component: () => import('@/views/Profile.vue') },
  { path: '/user/:id', name: 'UserProfile', component: () => import('@/views/UserProfile.vue'), props: true },
  { path: '/messages', component: () => import('@/views/MessagesList.vue') },
  { path: '/chat/:id/:other_user_id/:type?', name: 'Chat', component: () => import('@/views/Chat.vue'), meta: { requiresAuth: true }, props: true },
  { path: '/system-messages', name: 'SystemMessagesAll', component: () => import('@/views/SystemMessagesAll.vue') },
  { path: '/system-messages/:id', name: 'SystemMessageDetail', component: () => import('@/views/SystemMessageDetail.vue'), props: true },
  { path: '/admin', name: 'Admin', component: () => import('@/views/Admin.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/AdminLogin.vue') },
  { path: '/discover', component: () => import('@/views/Home.vue') },
  { path: '/forgot-password', component: () => import('@/views/ForgotPassword.vue') },
  { path: '/terms', component: () => import('@/views/Home.vue') },
  { path: '/privacy', component: () => import('@/views/Home.vue') },
  { path: '/buy-request/:id', name: 'BuyRequestDetail', component: () => import('@/views/BuyRequestDetail.vue') },
  { path: '/friends', name: 'Friends', component: () => import('@/views/Friends.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router