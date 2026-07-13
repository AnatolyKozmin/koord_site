import { ref } from 'vue'

const STORAGE_KEY = 'koord-theme'
const theme = ref('system') // 'light' | 'dark' | 'system'

function apply(value) {
  const root = document.documentElement
  if (value === 'system') {
    root.removeAttribute('data-theme')
  } else {
    root.setAttribute('data-theme', value)
  }
}

export function initTheme() {
  const saved = localStorage.getItem(STORAGE_KEY)
  theme.value = saved || 'system'
  apply(theme.value)
}

export function useTheme() {
  function setTheme(value) {
    theme.value = value
    localStorage.setItem(STORAGE_KEY, value)
    apply(value)
  }

  function toggle() {
    // system → определяем текущий эффективный режим и переключаем на противоположный
    const isDark =
      theme.value === 'dark' ||
      (theme.value === 'system' &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)
    setTheme(isDark ? 'light' : 'dark')
  }

  return { theme, setTheme, toggle }
}
