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

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
