<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Sun, Moon, MonitorSmartphone, LogOut } from '@lucide/vue'
import { useAuthStore } from '../stores/auth'
import { ROLE_LABELS } from '../constants/roles'
import { useTheme } from '../composables/useTheme'
import AppButton from '../components/ui/AppButton.vue'

const auth = useAuthStore()
const router = useRouter()
const { theme, setTheme } = useTheme()

const initials = computed(() => {
  const parts = (auth.user?.full_name || '').split(' ').filter(Boolean)
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '') || '?'
})

const themeOptions = [
  { key: 'light', label: 'Светлая', icon: Sun },
  { key: 'system', label: 'Системная', icon: MonitorSmartphone },
  { key: 'dark', label: 'Тёмная', icon: Moon },
]

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="rise flex flex-col gap-6">
    <!-- шапка профиля -->
    <section class="flex items-center gap-4">
      <div
        class="mesh grain relative flex h-16 w-16 flex-none items-center justify-center overflow-hidden font-display text-[22px] font-bold text-white"
      >
        <span class="relative glow-text">{{ initials }}</span>
      </div>
      <div class="min-w-0">
        <h1 class="truncate text-[22px]">{{ auth.user?.full_name }}</h1>
        <p class="truncate text-[14px] text-muted">{{ auth.user?.email }}</p>
        <span
          class="mt-1.5 inline-block border-l-2 border-accent bg-accent-soft px-2 py-0.5 text-[12px] font-semibold text-accent"
        >{{ ROLE_LABELS[auth.role] }}</span>
      </div>
    </section>

    <!-- тема -->
    <section>
      <h2 class="mb-3 text-[15px] uppercase tracking-wide">Оформление</h2>
      <div class="flex border border-line bg-surface p-1">
        <button
          v-for="opt in themeOptions"
          :key="opt.key"
          class="flex flex-1 items-center justify-center gap-2 px-3 py-2.5 text-[13px] font-medium transition-colors"
          :class="theme === opt.key ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
          @click="setTheme(opt.key)"
        >
          <component :is="opt.icon" :size="16" />
          {{ opt.label }}
        </button>
      </div>
    </section>

    <!-- выход -->
    <section>
      <AppButton variant="outline" size="lg" block @click="logout">
        <LogOut :size="18" /> Выйти из аккаунта
      </AppButton>
    </section>

    <p class="text-center text-[12px] text-muted">Координаторство'26 · v0.1</p>
  </div>
</template>
