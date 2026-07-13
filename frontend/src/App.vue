<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TopBar from './components/shell/TopBar.vue'
import BottomNav from './components/shell/BottomNav.vue'

const route = useRoute()
const bare = computed(() => route.meta.bare)
// focus-режим (редактор): без нижней навигации — у экрана своя панель действий
const showNav = computed(() => !route.meta.focus)
</script>

<template>
  <!-- Голый экран (вход) — без оболочки -->
  <RouterView v-if="bare" />

  <!-- Приложение -->
  <div v-else class="flex min-h-dvh flex-col">
    <TopBar />
    <main class="momentum mx-auto w-full max-w-lg flex-1 px-4 pt-5" :class="showNav ? 'pb-28' : 'pb-5'">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <BottomNav v-if="showNav" />
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.22s ease, transform 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
