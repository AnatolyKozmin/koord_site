<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { House, BookOpen, BarChart3, Users, User } from '@lucide/vue'
import { useAuthStore } from '../../stores/auth'
import { ROLES } from '../../constants/roles'

const auth = useAuthStore()
const route = useRoute()
const EDITOR = [ROLES.SUPERADMIN, ROLES.TRAINING_COORDINATOR]

const tabs = computed(() => {
  const all = [
    { to: '/', label: 'Главная', icon: House },
    { to: '/course', label: 'Курс', icon: BookOpen },
    { to: '/results', label: 'Итоги', icon: BarChart3, roles: EDITOR },
    { to: '/users', label: 'Люди', icon: Users, roles: EDITOR },
    { to: '/profile', label: 'Профиль', icon: User },
  ]
  return all.filter((t) => !t.roles || t.roles.includes(auth.role))
})

function isActive(to) {
  if (to === '/') return route.path === '/'
  return route.path === to || route.path.startsWith(to + '/')
}

function tap() {
  if (navigator.vibrate) navigator.vibrate(6)
}
</script>

<template>
  <nav
    class="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/85 backdrop-blur-xl"
    style="padding-bottom: env(safe-area-inset-bottom)"
  >
    <div class="mx-auto flex max-w-lg items-stretch justify-around">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        class="relative flex flex-1 flex-col items-center gap-1 py-2.5 transition-colors"
        :class="isActive(tab.to) ? 'text-accent' : 'text-muted'"
        @click="tap"
      >
        <span
          class="absolute top-0 h-0.5 w-8 -translate-y-px bg-accent transition-transform duration-200"
          :class="isActive(tab.to) ? 'scale-x-100' : 'scale-x-0'"
        ></span>
        <component :is="tab.icon" :size="22" :stroke-width="2" />
        <span class="text-[11px] font-medium">{{ tab.label }}</span>
      </RouterLink>
    </div>
  </nav>
</template>
