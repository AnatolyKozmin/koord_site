import axios from 'axios'

// same-origin: в проде /api проксирует nginx, в деве — прокси Vite (см. vite.config.js)
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

// Подставляем access-токен в каждый запрос
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// При 401 пробуем обновить пару токенов и повторить запрос один раз
let refreshPromise = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const refreshToken = localStorage.getItem('refresh_token')
    const isAuthUrl = original?.url?.startsWith('/auth/')

    if (error.response?.status === 401 && refreshToken && !original._retried && !isAuthUrl) {
      original._retried = true
      try {
        refreshPromise ??= api.post('/auth/refresh', { refresh_token: refreshToken })
        const { data } = await refreshPromise
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        return api(original)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
      } finally {
        refreshPromise = null
      }
    }
    return Promise.reject(error)
  },
)
