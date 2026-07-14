import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './style.css'

// 桌面 App 环境下，axios 请求指向本地后端服务器
// 开发模式（vite dev）: 走 vite 代理，baseURL 为空
// 打包模式（file:// 或 pywebview）: 直连本地后端
if (window.location.protocol === 'file:' || !window.location.host) {
  axios.defaults.baseURL = 'http://localhost:8765'
}
axios.defaults.timeout = 30000

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
