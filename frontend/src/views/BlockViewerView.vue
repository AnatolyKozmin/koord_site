<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, Check } from '@lucide/vue'
import { api } from '../api/client'

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

function youtubeEmbed(url) {
  const m = url?.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([\w-]+)/)
  return m ? `https://www.youtube.com/embed/${m[1]}` : null
}

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/blocks/${id}`)
    block.value = data
    slides.value = data.slides
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
                  v-if="youtubeEmbed(s.media_url)"
                  :src="youtubeEmbed(s.media_url)"
                  class="aspect-video w-full border border-line"
                  allowfullscreen
                ></iframe>
                <video v-else :src="s.media_url" controls class="w-full border border-line"></video>
              </div>
              <p v-if="s.content" class="text-center text-[14px] text-muted">{{ s.content }}</p>
            </template>
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
