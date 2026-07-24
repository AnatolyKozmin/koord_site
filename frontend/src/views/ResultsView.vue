<script setup>
import { computed, onMounted, ref } from 'vue'
import { Users, GraduationCap, TrendingUp } from '@lucide/vue'
import { api } from '../api/client'
import ResultsTabs from '../components/course/ResultsTabs.vue'

const data = ref({ blocks: [], coordinators: [] })
const loading = ref(true)
const error = ref('')
const selectedTeam = ref(null) // null = все факультеты

// список факультетов с числом координаторов, отсортирован по-русски
const teams = computed(() => {
  const counts = {}
  for (const c of data.value.coordinators) {
    if (c.team) counts[c.team] = (counts[c.team] || 0) + 1
  }
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => a.name.localeCompare(b.name, 'ru'))
})

const visibleCoordinators = computed(() =>
  selectedTeam.value
    ? data.value.coordinators.filter((c) => c.team === selectedTeam.value)
    : data.value.coordinators,
)

const ELECTIVE = ['#ff87ab', '#f58414', '#fccf50', '#b1aaff']

// цвет блока по его позиции среди опубликованных
const accentByBlock = computed(() => {
  const map = {}
  let e = 0
  for (const b of data.value.blocks) {
    map[b.id] = b.kind === 'theory' ? '#5612be' : ELECTIVE[e++ % ELECTIVE.length]
  }
  return map
})

// сводка считается по выбранному факультету (или по всем)
const summary = computed(() => {
  const cs = visibleCoordinators.value
  const avg = cs.length ? Math.round(cs.reduce((s, c) => s + c.overall_percent, 0) / cs.length) : 0
  const active = cs.filter((c) => c.overall_percent > 0).length
  return { count: cs.length, avg, active }
})

function initials(name) {
  const p = (name || '').split(' ').filter(Boolean)
  return (p[0]?.[0] || '') + (p[1]?.[0] || '') || '?'
}

async function load() {
  loading.value = true
  try {
    const { data: d } = await api.get('/results')
    data.value = d
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить результаты'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="rise flex flex-col gap-6">
    <header>
      <p class="font-display text-[12px] font-semibold uppercase tracking-[0.2em] text-accent">
        Обучение
      </p>
      <h1 class="mt-1.5 text-[28px]">Результаты</h1>
    </header>

    <ResultsTabs />

    <p v-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">{{ error }}</p>

    <!-- фильтр по факультетам -->
    <div v-if="!loading && teams.length" class="flex flex-wrap gap-2">
      <button
        class="border border-line px-3 py-1.5 text-[13px] font-medium transition-colors"
        :class="selectedTeam === null ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
        @click="selectedTeam = null"
      >
        Все <span class="tabular-nums opacity-70">{{ data.coordinators.length }}</span>
      </button>
      <button
        v-for="t in teams"
        :key="t.name"
        class="border border-line px-3 py-1.5 text-[13px] font-medium transition-colors"
        :class="selectedTeam === t.name ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
        @click="selectedTeam = t.name"
      >
        {{ t.name }} <span class="tabular-nums opacity-70">{{ t.count }}</span>
      </button>
    </div>

    <!-- сводка -->
    <section v-if="!loading" class="grid grid-cols-3 gap-3">
      <div class="border border-line bg-surface p-3.5">
        <Users :size="18" class="text-accent" />
        <p class="mt-2 font-display text-[24px] font-bold leading-none tabular-nums">{{ summary.count }}</p>
        <p class="mt-1 text-[12px] leading-tight text-muted">координаторов</p>
      </div>
      <div class="border border-line bg-surface p-3.5">
        <TrendingUp :size="18" class="text-accent" />
        <p class="mt-2 font-display text-[24px] font-bold leading-none tabular-nums">{{ summary.avg }}%</p>
        <p class="mt-1 text-[12px] leading-tight text-muted">средний прогресс</p>
      </div>
      <div class="border border-line bg-surface p-3.5">
        <GraduationCap :size="18" class="text-accent" />
        <p class="mt-2 font-display text-[24px] font-bold leading-none tabular-nums">{{ summary.active }}</p>
        <p class="mt-1 text-[12px] leading-tight text-muted">приступили</p>
      </div>
    </section>

    <!-- скелетоны -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 3" :key="i" class="skeleton h-28 border border-line"></div>
    </div>

    <div
      v-else-if="!visibleCoordinators.length"
      class="border border-dashed border-line bg-surface p-8 text-center text-[15px] text-muted"
    >
      {{ selectedTeam ? `Нет координаторов на факультете «${selectedTeam}».` : 'Пока нет координаторов для отслеживания.' }}
    </div>

    <!-- список координаторов -->
    <section v-else class="flex flex-col gap-3">
      <article
        v-for="c in visibleCoordinators"
        :key="c.user_id"
        class="border border-line bg-surface p-4"
        :class="!c.is_active && 'opacity-60'"
      >
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 flex-none items-center justify-center bg-surface-2 font-display text-[15px] font-bold text-accent">
            {{ initials(c.full_name) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate font-semibold">{{ c.full_name }}</p>
            <p class="truncate text-[13px] text-muted">{{ c.email }}</p>
            <span v-if="c.team" class="mt-1 inline-block bg-surface-2 px-1.5 py-0.5 text-[11px] font-medium text-muted">{{ c.team }}</span>
          </div>
          <div class="text-right">
            <p class="font-display text-[22px] font-bold leading-none tabular-nums text-accent">{{ c.overall_percent }}%</p>
            <p class="mt-1 text-[11px] text-muted">общий</p>
          </div>
        </div>

        <!-- разбивка по блокам -->
        <div class="mt-4 flex flex-col gap-2">
          <div v-for="pb in c.per_block" :key="pb.block_id" class="flex items-center gap-3">
            <span class="w-28 flex-none truncate text-[12px] text-muted">{{ pb.title }}</span>
            <div class="h-1.5 flex-1 overflow-hidden bg-surface-2">
              <div class="h-full transition-[width] duration-500" :style="{ width: pb.percent + '%', background: accentByBlock[pb.block_id] }"></div>
            </div>
            <span
              class="w-9 flex-none text-right text-[12px] font-semibold tabular-nums"
              :style="{ color: accentByBlock[pb.block_id] }"
            >{{ pb.percent }}%</span>
          </div>
        </div>

        <div class="mt-3 flex items-center gap-4 border-t border-line pt-3 text-[12px] text-muted">
          <span><b class="text-content">{{ c.blocks_done }}</b> из {{ data.blocks.length }} блоков</span>
          <span><b class="text-content">{{ c.slides_viewed }}</b> слайдов</span>
          <span><b class="text-content">{{ c.tests_passed }}</b> тестов</span>
          <span v-if="data.homework_total"><b class="text-content">{{ c.homework_done }}</b> из {{ data.homework_total }} ДЗ</span>
        </div>
      </article>
    </section>
  </div>
</template>
