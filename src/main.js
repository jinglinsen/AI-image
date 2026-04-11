import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import App from './App.vue'
import AIGCWorkbench from './views/AIGCWorkbench.vue'
import Login from './views/Login.vue'
import AdminPanel from './views/AdminPanel.vue'
import authService from './services/authService'

const routes = [
  { 
    path: '/login', 
    name: 'Login',
    component: Login,
    meta: { public: true }
  },
  { 
    path: '/', 
    name: 'Workbench',
    component: AIGCWorkbench,
    meta: { requiresAuth: true }
  },
  { 
    path: '/admin', 
    name: 'Admin',
    component: AdminPanel,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()
  const isAdmin = authService.isAdmin()
  
  // 需要认证的路由
  if (to.meta.requiresAuth && !isAuthenticated) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }
  
  // 需要管理员权限的路由
  if (to.meta.requiresAdmin && !isAdmin) {
    ElMessage.error('需要管理员权限')
    next('/')
    return
  }
  
  // 已登录用户访问登录页，跳转到首页
  if (to.path === '/login' && isAuthenticated) {
    next('/')
    return
  }
  
  next()
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')
