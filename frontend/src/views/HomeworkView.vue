<script setup>
import { computed, onMounted, ref } from 'vue'
import { Check, ChevronDown, ClipboardList } from '@lucide/vue'
import { api } from '../api/client'
import ResultsTabs from '../components/course/ResultsTabs.vue'

const items = ref([])
const coordinators = ref([])
const loading = ref(true)
const error = ref('')
// user_id раскрытых карточек
const expanded = ref({})
// `${user_id}:${slide_id}` отметок, отправляющихся прямо сейчас
const busy = ref({})

const checked = ref({}) // user_id -> Set(slide_id)
const answers = ref({}) // user_id -> { slide_id -> {text, updated_at} }

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/homework')
    items.value = data.items
    coordinators.value = data.coordinators
    checked.value = Object.fromEntries(
      data.coordinators.map((c) => [c.user_id, new Set(c.checked_slide_ids)]),
    )
    answers.value = Object.fromEntries(
      data.coordinators.map((c) => [
        c.user_id,
        Object.fromEntries(c.answers.map((a) => [a.slide_id, a])),
      ]),
    )
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить домашки'
  } finally {
    loading.value = false
  }
}

function doneCount(userId) {
  return checked.value[userId]?.size || 0
}

// сдано, но ещё не зачтено — то, что ждёт проверки
function pendingCount(userId) {
  const set = checked.value[userId]
  return Object.keys(answers.value[userId] || {}).filter((sid) => !set?.has(Number(sid))).length
}

function fmtDate(iso) {
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

async function toggle(userId, slideId) {
  const key = `${userId}:${slideId}`
  if (busy.value[key]) return
  const set = checked.value[userId]
  const next = !set.has(slideId)
  // оптимистично, при ошибке откатываем
  next ? set.add(slideId) : set.delete(slideId)
  busy.value[key] = true
  try {
    await api.post('/homework/check', { user_id: userId, slide_id: slideId, done: next })
  } catch (e) {
    next ? set.delete(slideId) : set.add(slideId)
    error.value = e.response?.data?.detail || 'Не удалось сохранить отметку'
  } finally {
    delete busy.value[key]
  }
}

function initials(name) {
  const p = (name || '').split(' ').filter(Boolean)
  return (p[0]?.[0] || '') + (p[1]?.[0] || '') || '?'
}

const totalDone = computed(() =>
  coordinators.value.reduce((s, c) => s + doneCount(c.user_id), 0),
)

onMounted(load)
</script>

<template>
  <div class="rise flex flex-col gap-6">
    <header>
      <p class="font-display text-[12px] font-semibold uppercase tracking-[0.2em] text-accent">
        Обучение
      </p>
      <h1 class="mt-1.5 text-[28px]">Домашки</h1>
    </header>

    <ResultsTabs />

    <p v-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">{{ error }}</p>

    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 3" :key="i" class="skeleton h-20 border border-line"></div>
    </div>

    <div
      v-else-if="!items.length"
      class="border border-dashed border-line bg-surface p-8 text-center text-[15px] text-muted"
    >
      Пока нет домашних заданий. Добавьте задание к слайду в редакторе блока —
      оно появится здесь и под слайдом у координаторов.
    </div>

    <template v-else>
      <p class="-mt-2 text-[13px] text-muted">
        {{ items.length }} заданий в курсе · {{ totalDone }} отметок о зачёте
      </p>

      <div
        v-if="!coordinators.length"
        class="border border-dashed border-line bg-surface p-8 text-center text-[15px] text-muted"
      >
        Пока нет координаторов для проверки.
      </div>

      <section v-else class="flex flex-col gap-3">
        <article
          v-for="c in coordinators"
          :key="c.user_id"
          class="border border-line bg-surface"
          :class="!c.is_active && 'opacity-60'"
        >
          <!-- шапка координатора -->
          <button class="flex w-full items-center gap-3 p-4 text-left" @click="expanded[c.user_id] = !expanded[c.user_id]">
            <div class="flex h-11 w-11 flex-none items-center justify-center bg-surface-2 font-display text-[15px] font-bold text-accent">
              {{ initials(c.full_name) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate font-semibold">{{ c.full_name }}</p>
              <p class="truncate text-[13px] text-muted">{{ c.email }}</p>
              <p v-if="pendingCount(c.user_id)" class="mt-0.5 text-[12px] font-semibold text-orange">
                {{ pendingCount(c.user_id) }} ждёт проверки
              </p>
            </div>
            <div class="text-right">
              <p class="font-display text-[20px] font-bold leading-none tabular-nums"
                 :class="doneCount(c.user_id) === items.length ? 'text-accent' : 'text-content'">
                {{ doneCount(c.user_id) }}<span class="text-muted">/{{ items.length }}</span>
              </p>
              <p class="mt-1 text-[11px] text-muted">зачтено</p>
            </div>
            <ChevronDown
              :size="18"
              class="flex-none text-muted transition-transform"
              :class="expanded[c.user_id] && 'rotate-180'"
            />
          </button>

          <!-- список домашек -->
          <div v-if="expanded[c.user_id]" class="flex flex-col border-t border-line">
            <div
              v-for="it in items"
              :key="it.slide_id"
              class="flex items-start gap-3 border-b border-line px-4 py-3 last:border-b-0"
            >
              <button
                class="mt-0.5 flex h-7 w-7 flex-none items-center justify-center border transition-colors"
                :class="checked[c.user_id].has(it.slide_id)
                  ? 'border-accent bg-accent text-on-accent'
                  : 'border-line text-transparent hover:border-accent/50'"
                :disabled="busy[`${c.user_id}:${it.slide_id}`]"
                :title="checked[c.user_id].has(it.slide_id) ? 'Снять зачёт' : 'Зачесть'"
                @click="toggle(c.user_id, it.slide_id)"
              >
                <Check :size="15" />
              </button>
              <div class="min-w-0 flex-1">
                <p class="text-[12px] font-semibold text-muted">
                  {{ it.block_title }} · слайд {{ it.slide_position + 1 }}
                </p>
                <p class="mt-0.5 line-clamp-2 whitespace-pre-line text-[14px] leading-snug">
                  <ClipboardList :size="13" class="mr-1 inline-block align-[-1px] text-accent" />{{ it.homework }}
                </p>
                <div
                  v-if="answers[c.user_id]?.[it.slide_id]"
                  class="mt-2 border-l-2 border-accent/50 bg-surface-2/60 px-3 py-2"
                >
                  <p class="text-[11px] font-semibold uppercase tracking-[0.1em] text-muted">
                    Ответ · {{ fmtDate(answers[c.user_id][it.slide_id].updated_at) }}
                  </p>
                  <p class="mt-1 whitespace-pre-line text-[13px] leading-snug">
                    {{ answers[c.user_id][it.slide_id].text }}
                  </p>
                </div>
                <p v-else class="mt-1.5 text-[12px] italic text-muted">Ответ ещё не отправлен</p>
              </div>
            </div>
          </div>
        </article>
      </section>
    </template>
  </div>
</template>
