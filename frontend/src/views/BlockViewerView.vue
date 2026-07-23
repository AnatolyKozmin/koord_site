<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, ChevronDown, Check, ClipboardList } from '@lucide/vue'
import { api } from '../api/client'
import { videoEmbed } from '../utils/videoEmbed'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const block = ref(null)
const slides = ref([])
const loading = ref(true)
const error = ref('')
const current = ref(0)

const total = computed(() => slides.value.length)
const atEnd = computed(() => current.value >= total.value - 1)

// раскрытые панели домашек (по индексу слайда)
const hwOpen = ref({})
function toggleHw(i) {
  hwOpen.value[i] = !hwOpen.value[i]
}

// черновики ответов и отправка (по id слайда)
const hwDraft = ref({})
const hwSending = ref({})
const hwError = ref({})

function hwStatus(s) {
  if (s.homework_done) return { label: 'Зачтено', cls: 'bg-gold/15 text-[#8a6b12]' }
  if (s.homework_answer) return { label: 'На проверке', cls: 'bg-accent/10 text-accent' }
  return { label: 'Не сдано', cls: 'text-muted' }
}

async function sendAnswer(s) {
  const text = (hwDraft.value[s.id] || '').trim()
  if (!text || hwSending.value[s.id]) return
  hwSending.value[s.id] = true
  hwError.value[s.id] = ''
  try {
    await api.post('/homework/answer', { slide_id: s.id, text })
    s.homework_answer = text
  } catch (e) {
    hwError.value[s.id] = e.response?.data?.detail || 'Не удалось отправить ответ'
  } finally {
    hwSending.value[s.id] = false
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/blocks/${id}`)
    block.value = data
    slides.value = data.slides
    for (const s of data.slides) {
      if (s.homework) hwDraft.value[s.id] = s.homework_answer || ''
    }
    current.value = Math.min(data.progress?.last_slide || 0, Math.max(0, data.slides.length - 1))
    saveProgress()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Блок недоступен'
  } finally {
    loading.value = false
  }
}

async function saveProgress() {
  if (!slides.value.length) return
  try {
    await api.post(`/blocks/${id}/progress`, { last_slide: current.value })
  } catch {
    /* тихо: прогресс не критичен для просмотра */
  }
}

function go(dir) {
  const next = current.value + dir
  if (next < 0 || next >= total.value) return
  current.value = next
  if (navigator.vibrate) navigator.vibrate(6)
  saveProgress()
}

// свайп
let startX = 0
function onTouchStart(e) {
  startX = e.changedTouches[0].clientX
}
function onTouchEnd(e) {
  const dx = e.changedTouches[0].clientX - startX
  if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1)
}
function onKey(e) {
  if (e.key === 'ArrowRight') go(1)
  if (e.key === 'ArrowLeft') go(-1)
}

onMounted(() => {
  load()
  window.addEventListener('keydown', onKey)
})
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="flex flex-col gap-4">
    <button
      class="inline-flex items-center gap-1 text-[14px] text-muted transition-colors hover:text-content"
      @click="router.push('/course')"
    >
      <ChevronLeft :size="18" /> Курс
    </button>

    <div v-if="loading" class="skeleton h-[60vh] border border-line"></div>
    <p v-else-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">{{ error }}</p>

    <template v-else>
      <div>
        <h1 class="text-[22px]">{{ block.title }}</h1>
        <!-- индикатор слайдов -->
        <div class="mt-3 flex gap-1.5">
          <span
            v-for="(s, i) in slides"
            :key="i"
            class="h-1 flex-1 transition-colors"
            :class="i <= current ? 'bg-accent' : 'bg-surface-2'"
          ></span>
        </div>
      </div>

      <!-- сцена слайдов -->
      <div
        class="relative overflow-hidden border border-line bg-surface"
        @touchstart.passive="onTouchStart"
        @touchend.passive="onTouchEnd"
      >
        <div
          class="flex transition-transform duration-300 ease-[cubic-bezier(0.22,1,0.36,1)]"
          :style="{ transform: `translateX(-${current * 100}%)` }"
        >
          <div
            v-for="(s, i) in slides"
            :key="i"
            class="flex min-h-[52vh] w-full flex-none flex-col items-center justify-center gap-4 p-6"
          >
            <!-- текст -->
            <p v-if="s.type === 'text'" class="max-w-prose text-center text-[19px] leading-relaxed">
              {{ s.content }}
            </p>

            <!-- картинка -->
            <template v-else-if="s.type === 'image'">
              <img :src="s.media_url" :alt="s.content" class="max-h-[46vh] w-full object-contain" />
              <p v-if="s.content" class="text-center text-[14px] text-muted">{{ s.content }}</p>
            </template>

            <!-- видео -->
            <template v-else>
              <div class="w-full">
                <iframe
                  v-if="videoEmbed(s.media_url)"
                  :src="videoEmbed(s.media_url)"
                  class="aspect-video w-full border border-line"
                  allow="autoplay; fullscreen; encrypted-media; picture-in-picture"
                  allowfullscreen
                ></iframe>
                <video v-else :src="s.media_url" controls class="w-full border border-line"></video>
              </div>
              <p v-if="s.content" class="text-center text-[14px] text-muted">{{ s.content }}</p>
            </template>

            <!-- домашнее задание -->
            <div v-if="s.homework" class="w-full max-w-prose border border-line bg-surface-2/40">
              <button
                class="flex w-full items-center justify-between gap-3 px-4 py-3 text-left"
                @click="toggleHw(i)"
              >
                <span class="inline-flex items-center gap-2 font-display text-[12px] font-bold uppercase tracking-[0.14em]">
                  <ClipboardList :size="16" class="text-accent" /> Домашнее задание
                </span>
                <span class="inline-flex items-center gap-2">
                  <span
                    class="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold"
                    :class="hwStatus(s).cls"
                  >
                    <Check v-if="s.homework_done" :size="12" /> {{ hwStatus(s).label }}
                  </span>
                  <ChevronDown
                    :size="16"
                    class="text-muted transition-transform"
                    :class="hwOpen[i] && 'rotate-180'"
                  />
                </span>
              </button>
              <div v-if="hwOpen[i]" class="flex flex-col gap-3 border-t border-line px-4 py-3 text-left">
                <p class="whitespace-pre-line text-[15px] leading-relaxed">{{ s.homework }}</p>

                <!-- ответ координатора -->
                <template v-if="!s.homework_done">
                  <textarea
                    v-model="hwDraft[s.id]"
                    v-autosize
                    rows="2"
                    placeholder="Напиши свой ответ здесь…"
                    class="w-full rounded-xs border border-line bg-surface px-3 py-2.5 text-[14px] text-content focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
                  ></textarea>
                  <div class="flex items-center gap-3">
                    <button
                      class="bg-accent px-4 py-2 text-[13px] font-medium text-on-accent transition-[filter] hover:brightness-110 disabled:opacity-40"
                      :disabled="!(hwDraft[s.id] || '').trim() || hwSending[s.id]"
                      @click="sendAnswer(s)"
                    >
                      {{ hwSending[s.id] ? 'Отправка…' : s.homework_answer ? 'Обновить ответ' : 'Отправить ответ' }}
                    </button>
                    <span v-if="s.homework_answer && !hwSending[s.id]" class="text-[12px] text-muted">
                      Ответ отправлен — его видят обучающие
                    </span>
                  </div>
                  <p v-if="hwError[s.id]" class="text-[13px] text-pink">{{ hwError[s.id] }}</p>
                </template>
                <p v-else class="whitespace-pre-line border-l-2 border-gold bg-gold/10 px-3 py-2 text-[14px]">
                  {{ s.homework_answer }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- навигация -->
      <div class="flex items-center gap-3">
        <button
          class="flex h-11 w-11 flex-none items-center justify-center border border-line text-content transition-colors hover:bg-surface-2 disabled:opacity-30"
          :disabled="current === 0"
          @click="go(-1)"
        >
          <ChevronLeft :size="20" />
        </button>

        <div class="flex-1 text-center text-[14px] tabular-nums text-muted">
          {{ current + 1 }} / {{ total }}
        </div>

        <button
          v-if="!atEnd"
          class="flex h-11 w-11 flex-none items-center justify-center border border-line text-content transition-colors hover:bg-surface-2"
          @click="go(1)"
        >
          <ChevronRight :size="20" />
        </button>
        <button
          v-else
          class="flex h-11 flex-none items-center justify-center gap-2 bg-accent px-4 text-[14px] font-medium text-on-accent transition-[filter] hover:brightness-110"
          @click="router.push('/course')"
        >
          <Check :size="18" /> Готово
        </button>
      </div>
    </template>
  </div>
</template>
