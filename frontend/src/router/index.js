import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ROLES } from '../constants/roles'

const EDITOR_ROLES = [ROLES.SUPERADMIN, ROLES.TRAINING_COORDINATOR]

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true, bare: true },
  },
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/course',
    name: 'course',
    component: () => import('../views/CourseView.vue'),
  },
  {
    path: '/course/:id',
    name: 'block-viewer',
    component: () => import('../views/BlockViewerView.vue'),
  },
  {
    path: '/editor/:id',
    name: 'block-editor',
    component: () => import('../views/BlockEditorView.vue'),
    meta: { roles: EDITOR_ROLES, focus: true },
  },
  {
    path: '/results',
    name: 'results',
    component: () => import('../views/ResultsView.vue'),
    meta: { roles: EDITOR_ROLES },
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('../views/UsersView.vue'),
    meta: { roles: EDITOR_ROLES },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.public) {
    return auth.hasToken ? '/' : true
  }

  if (!auth.hasToken) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.role)) {
    return '/'
  }

  return true
})
