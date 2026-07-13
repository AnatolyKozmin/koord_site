<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, GraduationCap, Layers, CircleCheckBig } from '@lucide/vue'
import { api } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { ROLE_LABELS } from '../constants/roles'
import { blockState, blockPercent } from '../data/blockStyle'
import AppButton from '../components/ui/AppButton.vue'

const auth = useAuthStore()
const router = useRouter()

const blocks = ref([])
const loading = ref(true)

const firstName = computed(() => auth.user?.full_name?.split(' ')[0] || 'координатор')

const resume = computed(
  () => blocks.value.find((b) => blockState(b) !== 'done') || blocks.value[0] || null,
)

function slidesViewed(b) {
  const p = b.progress || {}
  if (p.viewed) return b.slide_count
  return p.last_slide > 0 ? p.last_slide + 1 : 0
}

const stats = computed(() => {
  const done = blocks.value.filter((b) => blockState(b) === 'done').length
  const slides = blocks.value.reduce((s, b) => s + slidesViewed(b), 0)
  const tests = blocks.value.filter((b) => b.progress?.test_status === 'passed').length
  return [
    { icon: GraduationCap, value: done, label: 'блоков завершено' },
    { icon: Layers, value: slides, label: 'слайдов пройдено' },
    { icon: CircleCheckBig, value: tests, label: 'тестов сдано' },
  ]
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/blocks')
    blocks.value = data
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="rise flex flex-col gap-6">
    <header>
      <p class="text-[13px] text-muted">{{ ROLE_LABELS[auth.role] }}</p>
      <h1 class="mt-0.5 text-[26px]">Привет, {{ firstName }}!</h1>
    </header>

    <div v-if="loading" class="skeleton h-44 border border-line"></div>

    <!-- продолжить -->
    <section
      v-else-if="resume"
      class="mesh grain relative overflow-hidden p-5 text-white shadow-[0_20px_50px_-24px_rgba(68,23,102,0.7)]"
    >
      <p class="relative font-display text-[11px] font-semibold uppercase tracking-[0.18em] text-white/80">
        {{ blockState(resume) === 'new' ? 'Начать обучение' : 'Продолжить обучение' }}
      </p>
      <h2 class="relative mt-2 max-w-[16ch] text-[22px] text-white glow-text">{{ resume.title }}</h2>
      <div class="relative mt-3 flex items-center gap-3">
        <div class="h-1.5 flex-1 overflow-hidden bg-white/25">
          <div class="h-full bg-white" :style="{ width: blockPercent(resume) + '%' }"></div>
        </div>
        <span class="text-[13px] font-semibold tabular-nums">{{ blockPercent(resume) }}%</span>
      </div>
      <AppButton
        variant="glow"
        size="md"
        class="relative mt-4 !bg-white/15 !text-white backdrop-blur-sm"
        @click="router.push(`/course/${resume.id}`)"
      >
        {{ blockState(resume) === 'new' ? 'Начать' : 'Продолжить' }} <ArrowRight :size="18" />
      </AppButton>
    </section>

    <div v-else class="border border-dashed border-line bg-surface p-6 text-center text-[15px] text-muted">
      Курс ещё готовится. Загляните позже.
    </div>

    <!-- статистика -->
    <section v-if="!loading && blocks.length" class="grid grid-cols-3 gap-3">
      <div v-for="s in stats" :key="s.label" class="border border-line bg-surface p-3.5">
        <component :is="s.icon" :size="18" class="text-accent" />
        <p class="mt-2 font-display text-[24px] font-bold leading-none tabular-nums">{{ s.value }}</p>
        <p class="mt-1 text-[12px] leading-tight text-muted">{{ s.label }}</p>
      </div>
    </section>

    <!-- переход к курсу -->
    <RouterLink
      to="/course"
      class="group flex items-center justify-between border border-line bg-surface p-4 transition-colors hover:border-accent/40"
    >
      <div>
        <p class="font-display text-[15px] font-bold">Открыть курс</p>
        <p class="text-[13px] text-muted">Все блоки программы</p>
      </div>
      <ArrowRight :size="20" class="text-muted transition-transform group-hover:translate-x-1 group-hover:text-accent" />
    </RouterLink>
  </div>
</template>
