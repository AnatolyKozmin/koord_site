<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LighthouseMark from '../components/brand/LighthouseMark.vue'
import AppButton from '../components/ui/AppButton.vue'
import AppField from '../components/ui/AppField.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(route.query.redirect || '/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось войти. Проверьте подключение.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="relative min-h-dvh overflow-hidden">
    <!-- сетчатый фон + зерно -->
    <div class="mesh grain absolute inset-0"></div>
    <div
      class="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-black/25 to-transparent"
    ></div>

    <div class="relative flex min-h-dvh flex-col items-center justify-center px-6 py-10">
      <div class="w-full max-w-[400px]">
        <!-- герой -->
        <div class="rise mb-8 flex flex-col items-center text-center">
          <LighthouseMark class="mb-5 h-36 w-auto drop-shadow-[0_10px_30px_rgba(68,23,102,0.55)]" />
          <p
            class="mb-1 font-display text-[13px] font-semibold uppercase tracking-[0.28em] text-white/80"
          >
            Курс координатора
          </p>
          <h1
            class="glow-text font-display text-[clamp(22px,7.5vw,28px)] font-bold leading-none tracking-tight text-white"
          >
            Координаторство<span class="text-glow">'26</span>
          </h1>
        </div>

        <!-- карточка входа -->
        <form
          class="rise border border-white/15 bg-surface/95 p-6 shadow-[0_24px_60px_-20px_rgba(21,12,28,0.6)] backdrop-blur-xl"
          style="animation-delay: 0.08s"
          @submit.prevent="submit"
        >
          <h2 class="mb-5 text-lg">Вход</h2>
          <div class="flex flex-col gap-4">
            <AppField
              v-model="email"
              label="Email"
              type="email"
              autocomplete="username"
              placeholder="you@koord.ru"
            />
            <AppField
              v-model="password"
              label="Пароль"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              :error="error"
            />
            <AppButton type="submit" variant="primary" size="lg" block :loading="submitting">
              {{ submitting ? 'Входим…' : 'Войти' }}
            </AppButton>
          </div>
        </form>

        <p class="rise mt-6 text-center text-[13px] text-white/70" style="animation-delay: 0.16s">
          Доступ выдаёт координационный центр
        </p>
      </div>
    </div>
  </div>
</template>
