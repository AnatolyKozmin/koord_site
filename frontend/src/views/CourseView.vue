<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@lucide/vue'
import { api } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { blockAccent, blockNumber } from '../data/blockStyle'
import BlockCard from '../components/course/BlockCard.vue'
import AppButton from '../components/ui/AppButton.vue'

const auth = useAuthStore()
const router = useRouter()

const blocks = ref([])
const loading = ref(true)
const creating = ref(false)
const error = ref('')

const isEditor = computed(() => auth.isSuperadmin || auth.isTrainingCoordinator)

// нумерация по общему порядку
const numbered = computed(() =>
  blocks.value.map((b, i) => ({ ...b, _number: blockNumber(i + 1) })),
)
const theory = computed(() => numbered.value.filter((b) => b.kind === 'theory'))
const electives = computed(() => numbered.value.filter((b) => b.kind === 'elective'))

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/blocks')
    blocks.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить курс'
  } finally {
    loading.value = false
  }
}

async function createBlock() {
  creating.value = true
  try {
    const { data } = await api.post('/blocks', {
      title: 'Новый блок',
      description: '',
      kind: 'elective',
    })
    router.push(`/editor/${data.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось создать блок'
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="rise flex flex-col gap-7">
    <header class="flex items-start justify-between gap-3">
      <div>
        <p class="font-display text-[12px] font-semibold uppercase tracking-[0.2em] text-accent">
          Программа обучения
        </p>
        <h1 class="mt-1.5 text-[28px]">Курс координатора</h1>
      </div>
      <AppButton v-if="isEditor" size="sm" :loading="creating" @click="createBlock">
        <Plus :size="18" /> Блок
      </AppButton>
    </header>

    <p v-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">
      {{ error }}
    </p>

    <!-- скелетоны -->
    <div v-if="loading" class="flex flex-col gap-4">
      <div class="skeleton h-40 border border-line"></div>
      <div class="grid gap-4 sm:grid-cols-2">
        <div v-for="i in 2" :key="i" class="skeleton h-44 border border-line"></div>
      </div>
    </div>

    <!-- пустое состояние -->
    <div
      v-else-if="!blocks.length"
      class="border border-dashed border-line bg-surface p-8 text-center"
    >
      <p class="text-[15px] text-muted">
        {{ isEditor ? 'Пока нет ни одного блока. Создайте первый.' : 'Курс ещё готовится. Загляните позже.' }}
      </p>
      <AppButton v-if="isEditor" class="mt-4" :loading="creating" @click="createBlock">
        <Plus :size="18" /> Создать блок
      </AppButton>
    </div>

    <template v-else>
      <p class="-mt-3 max-w-prose text-[15px] text-muted">
        Сначала — общая теория. Затем выбираешь блок на прокачку: один обязателен,
        остальные — по желанию.
      </p>

      <section v-if="theory.length" class="flex flex-col gap-4">
        <BlockCard
          v-for="b in theory"
          :key="b.id"
          :block="b"
          :number="b._number"
          :accent="blockAccent(b)"
          :editable="isEditor"
          featured
        />
      </section>

      <section v-if="electives.length">
        <div class="mb-3 flex items-baseline justify-between">
          <h2 class="text-[17px]">Блоки на выбор</h2>
          <span class="text-[13px] text-muted">1 обязателен · остальные по желанию</span>
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <BlockCard
            v-for="(b, i) in electives"
            :key="b.id"
            :block="b"
            :number="b._number"
            :accent="blockAccent(b, i)"
            :editable="isEditor"
          />
        </div>
      </section>
    </template>
  </div>
</template>
