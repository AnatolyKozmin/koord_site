import { defineStore } from 'pinia'
import { api } from '../api/client'
import { ROLES } from '../constants/roles'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    // токен держим в реактивном состоянии — иначе геттер, читающий localStorage,
    // закэшируется на первом (пустом) значении и не увидит вход
    token: localStorage.getItem('access_token'),
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null,
    role: (state) => state.user?.role ?? null,
    isSuperadmin: (state) => state.user?.role === ROLES.SUPERADMIN,
    isTrainingCoordinator: (state) => state.user?.role === ROLES.TRAINING_COORDINATOR,
    hasToken: (state) => Boolean(state.token),
  },

  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      this.token = data.access_token
      await this.fetchMe()
    },

    async fetchMe() {
      this.loading = true
      try {
        const { data } = await api.get('/auth/me')
        this.user = data
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
  },
})
