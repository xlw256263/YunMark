// 导入 Vue 应用创建函数
import { createApp } from 'vue'
// 导入 Pinia 状态管理
import { createPinia } from 'pinia'
// 导入根组件
import App from './App.vue'
// 导入路由配置（不需要写扩展名，Vite 会自动解析）
import router from './router'
// 导入全局样式
import './style.css'

// 导入 Element Plus UI 组件库
import ElementPlus from 'element-plus'
// 导入 Element Plus 中文语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
// 导入 Element Plus 样式文件
import 'element-plus/dist/index.css'
// 导入所有 Element Plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建 Vue 应用实例
const app = createApp(App)
// 创建 Pinia 实例
const pinia = createPinia()

// 注册 Pinia 状态管理
app.use(pinia)
// 注册 Vue Router 路由
app.use(router)
// 注册 Element Plus 组件库，配置中文语言
app.use(ElementPlus, {
  locale: zhCn,
})

// 全局注册所有 Element Plus 图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 挂载应用到 #app 元素
app.mount('#app')
