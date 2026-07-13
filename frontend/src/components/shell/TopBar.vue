<script setup>
import { Sun, Moon } from '@lucide/vue'
import LighthouseMark from '../brand/LighthouseMark.vue'
import { useTheme } from '../../composables/useTheme'

const { toggle } = useTheme()
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-line bg-surface/80 backdrop-blur-xl"
    style="padding-top: env(safe-area-inset-top)"
  >
    <div class="mx-auto flex max-w-lg items-center justify-between px-4 py-3">
      <RouterLink to="/" class="flex items-center gap-2">
        <LighthouseMark :glow="false" class="h-7 w-auto" tower="var(--accent)" />
        <span class="font-display text-[15px] font-bold tracking-tight">
          Координаторство<span class="text-accent">'26</span>
        </span>
      </RouterLink>
      <button
        class="flex h-9 w-9 items-center justify-center rounded-xs text-muted transition-colors hover:bg-surface-2 hover:text-content"
        aria-label="Сменить тему"
        @click="toggle"
      >
        <Sun :size="18" class="hidden dark-hidden" />
        <Moon :size="18" class="dark-only" />
      </button>
    </div>
  </header>
</template>

<style scoped>
/* Иконка темы по эффективной теме */
.dark-only { display: none; }
.dark-hidden { display: block; }
:root[data-theme='dark'] .dark-only { display: block; }
:root[data-theme='dark'] .dark-hidden { display: none; }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme='light']) .dark-only { display: block; }
  :root:not([data-theme='light']) .dark-hidden { display: none; }
}
</style>
