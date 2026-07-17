<script setup>
// переключатель разделов для обучающих: прогресс ↔ домашки
const tabs = [
  { to: '/results', label: 'Прогресс' },
  { to: '/results/homework', label: 'Домашки' },
]
</script>

<template>
  <nav class="-mt-2 flex self-start border border-line">
    <RouterLink
      v-for="t in tabs"
      :key="t.to"
      :to="t.to"
      class="px-4 py-2 text-[14px] font-medium transition-colors"
      exact-active-class="bg-accent text-on-accent"
      :class="$route.path !== t.to && 'text-muted hover:text-content'"
    >
      {{ t.label }}
    </RouterLink>
  </nav>
</template>
