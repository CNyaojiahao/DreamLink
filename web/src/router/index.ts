import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/video/:id',
      name: 'video',
      component: () => import('@/views/VideoView.vue')
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('@/views/UploadView.vue')
    },
    {
      path: '/user/:id',
      name: 'user',
      component: () => import('@/views/UserView.vue')
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue')
    },
    {
      path: '/ranking',
      name: 'ranking',
      component: () => import('@/views/RankingView.vue')
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('@/views/AccountView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue')
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLoginView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/AdminDashboardView.vue')
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/AdminUsersView.vue')
    },
    {
      path: '/admin/videos',
      name: 'admin-videos',
      component: () => import('@/views/admin/AdminVideosView.vue')
    },
    {
      path: '/admin/reports',
      name: 'admin-reports',
      component: () => import('@/views/admin/AdminReportsView.vue')
    },
    {
      path: '/admin/categories',
      name: 'admin-categories',
      component: () => import('@/views/admin/AdminCategoriesView.vue')
    }
  ]
})

export default router
