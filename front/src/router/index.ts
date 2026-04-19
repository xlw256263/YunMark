/**
 * Vue Router 路由配置
 * 定义应用的所有路由规则和守卫
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

/**
 * 路由配置数组
 */
const routes: RouteRecordRaw[] = [
  {
    // 导航页（首页）- 公开访问
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { 
      title: '云藏·智能收藏夹',
      requiresAuth: false,
    },
  },
  {
    // 我的收藏页 - 需要登录
    path: '/my/bookmarks',
    name: 'Bookmarks',
    component: () => import('@/views/BookmarkView.vue'),
    meta: { 
      title: '我的收藏',
      requiresAuth: true,
    },
  },
  {
    // 官方分享页 - 公开访问
    path: '/official',
    name: 'Official',
    component: () => import('@/views/OfficialView.vue'),
    meta: { 
      title: '官方分享',
      requiresAuth: false,
    },
  },
  {
    // 统计页面 - 需要登录
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/StatsView.vue'),
    meta: { 
      title: '数据统计',
      requiresAuth: true,
    },
  },
  {
    // 个人中心 - 需要登录
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { 
      title: '个人中心',
      requiresAuth: true,
    },
  },
  {
    // 我的分享页 - 需要登录
    path: '/my/shares',
    name: 'MyShares',
    component: () => import('@/views/MySharesView.vue'),
    meta: { 
      title: '我的分享',
      requiresAuth: true,
    },
  },
  {
    // 管理员后台 - 需要管理员权限
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { 
      title: '管理员后台',
      requiresAuth: true,
      requiresAdmin: true,
    },
    children: [
      {
        // 标签分类管理
        path: 'tag-categories',
        name: 'AdminTagCategories',
        component: () => import('@/views/admin/TagCategoryAdminView.vue'),
        meta: { 
          title: '标签分类管理',
          requiresAdmin: true,
        },
      },
      {
        // 标签管理
        path: 'tags',
        name: 'AdminTags',
        component: () => import('@/views/admin/TagAdminView.vue'),
        meta: { 
          title: '标签管理',
          requiresAdmin: true,
        },
      },
      {
        // 分享审核管理
        path: 'shares',
        name: 'AdminShares',
        component: () => import('@/views/admin/ShareAdminView.vue'),
        meta: { 
          title: '分享审核管理',
          requiresAdmin: true,
        },
      },
    ],
  },
  {
    // 403 无权限页面
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Forbidden.vue'),
    meta: { title: '无权限访问' },
  },
  {
    // 404 页面不存在
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' },
  },
]

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为：切换路由时滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

/**
 * 全局前置路由守卫
 * 用于权限控制和页面标题设置
 */
router.beforeEach((to, from, next) => {
  // 获取用户 Store
  const userStore = useUserStore()
  
  // 关键修复：在路由守卫中立即恢复用户状态（同步）
  // 这样 isLoggedIn 才能正确判断
  if (!userStore.accessToken && localStorage.getItem('access_token')) {
    userStore.restoreFromStorage()
  }
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 云藏` : '云藏·智能收藏夹'
  
  // 检查是否需要登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    // 未登录，触发登录弹窗并跳转到首页
    userStore.triggerLoginDialog()
    next('/')
    return
  }
  
  // 检查是否需要管理员权限
  if (to.meta.requiresAdmin && !userStore.isAdmin) {
    // 非管理员，跳转到 403 页面
    next('/403')
    return
  }
  
  // 允许导航
  next()
})

export default router
