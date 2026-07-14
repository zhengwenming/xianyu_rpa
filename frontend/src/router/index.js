import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/shops', name: 'Shops', component: () => import('../views/Shops.vue') },
  { path: '/tasks', name: 'Tasks', component: () => import('../views/Tasks.vue') },
  { path: '/llm-config', name: 'LLMConfig', component: () => import('../views/LLMConfig.vue') },
  { path: '/listing-logs', name: 'ListingLogs', component: () => import('../views/ListingLogs.vue') },
  { path: '/delisting-logs', name: 'DelistingLogs', component: () => import('../views/DelistingLogs.vue') },
  { path: '/task-logs', name: 'TaskLogs', component: () => import('../views/TaskLogs.vue') },
  { path: '/auto-reply', name: 'AutoReply', component: () => import('../views/AutoReply.vue') },
  { path: '/delivery', name: 'Delivery', component: () => import('../views/Delivery.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
]

// hash 模式：打包后本地文件加载也能正常工作
const router = createRouter({ history: createWebHashHistory(), routes })
export default router
