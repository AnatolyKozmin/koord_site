import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Шрифты бренда (с кириллицей)
import '@fontsource/unbounded/700.css'
import '@fontsource/unbounded/900.css'
import '@fontsource/golos-text/400.css'
import '@fontsource/golos-text/500.css'
import '@fontsource/golos-text/600.css'
import '@fontsource/golos-text/700.css'

import App from './App.vue'
import { router } from './router'
import { initTheme } from './composables/useTheme'
import './style.css'

initTheme()

// v-autosize: textarea растёт под содержимое по мере ввода
function fitTextarea(el) {
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 2 + 'px' // +2 — компенсация рамки
}
const autosize = {
  mounted(el) {
    el.style.overflowY = 'hidden'
    el.style.resize = 'none'
    fitTextarea(el)
    el.addEventListener('input', () => fitTextarea(el))
  },
  updated(el) {
    fitTextarea(el)
  },
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.directive('autosize', autosize)
app.mount('#app')
