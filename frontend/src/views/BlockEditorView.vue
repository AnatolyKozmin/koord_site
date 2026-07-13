<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, Plus, Trash2, Check } from '@lucide/vue'
import { api } from '../api/client'
import AppButton from '../components/ui/AppButton.vue'
import AppField from '../components/ui/AppField.vue'
import SlideEditor from '../components/course/SlideEditor.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

const form = ref({ title: '', description: '', kind: 'elective', is_published: false })
const slides = ref([])

const slideError = computed(() => {
  const bad = slides.value.find(
    (s) => (s.type === 'image' || s.type === 'video') && !s.media_url,
  )
  return bad ? 'У слайдов с картинкой/видео должна быть ссылка или файл' : ''
})

async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/blocks/${id}`)
    form.value = {
      title: data.title,
      description: data.description,
      kind: data.kind,
      is_published: data.is_published,
    }
    slides.value = data.slides.map((s) => ({
      type: s.type,
      content: s.content,
      media_url: s.media_url,
    }))
  } catch (e) {
    error.value = e.response?.data?.detail || 'Блок не найден'
  } finally {
    loading.value = false
  }
}

async function save() {
  error.value = ''
  if (!form.value.title.trim()) {
    error.value = 'Введите название блока'
    return
  }
  if (slideError.value) {
    error.value = slideError.value
    return
  }
  saving.value = true
  try {
    await api.patch(`/blocks/${id}`, form.value)
    await api.put(`/blocks/${id}/slides`, slides.value)
    saved.value = true
    setTimeout(() => (saved.value = false), 1800)
  } catch (e) {
    const d = e.response?.data?.detail
    error.value = Array.isArray(d) ? d[0]?.msg || 'Ошибка сохранения' : d || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

async function togglePublish() {
  form.value.is_published = !form.value.is_published
  await save()
}

async function removeBlock() {
  if (!confirm('Удалить блок целиком?')) return
  try {
    await api.delete(`/blocks/${id}`)
    router.push('/course')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось удалить'
  }
}

function addSlide() {
  slides.value.push({ type: 'text', content: '', media_url: null })
}
function move(i, dir) {
  const j = i + dir
  if (j < 0 || j >= slides.value.length) return
  const arr = slides.value
  ;[arr[i], arr[j]] = [arr[j], arr[i]]
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-5 pb-24">
    <!-- шапка -->
    <div class="flex items-center justify-between">
      <button
        class="inline-flex items-center gap-1 text-[14px] text-muted transition-colors hover:text-content"
        @click="router.push('/course')"
      >
        <ChevronLeft :size="18" /> Курс
      </button>
      <button
        class="inline-flex items-center gap-1.5 text-[14px] text-muted transition-colors hover:text-pink"
        @click="removeBlock"
      >
        <Trash2 :size="16" /> Удалить
      </button>
    </div>

    <div v-if="loading" class="flex flex-col gap-3">
      <div class="skeleton h-28 border border-line"></div>
      <div class="skeleton h-40 border border-line"></div>
    </div>

    <template v-else>
      <div>
        <p class="font-display text-[12px] font-semibold uppercase tracking-[0.2em] text-accent">
          Редактор блока
        </p>
        <h1 class="mt-1.5 text-[24px]">{{ form.title || 'Без названия' }}</h1>
      </div>

      <!-- мета -->
      <section class="flex flex-col gap-4 border border-line bg-surface p-4">
        <AppField v-model="form.title" label="Название" placeholder="Например: Эмоциональный интеллект" />
        <label class="flex flex-col gap-1.5">
          <span class="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">Описание</span>
          <textarea
            v-model="form.description"
            rows="2"
            placeholder="О чём этот блок"
            class="w-full resize-y rounded-xs border border-line bg-surface px-3.5 py-3 text-[15px] text-content focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
          ></textarea>
        </label>
        <div>
          <span class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">Тип</span>
          <div class="flex border border-line">
            <button
              class="flex-1 py-2.5 text-[14px] font-medium transition-colors"
              :class="form.kind === 'theory' ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
              @click="form.kind = 'theory'"
            >
              Обязательный (теория)
            </button>
            <button
              class="flex-1 py-2.5 text-[14px] font-medium transition-colors"
              :class="form.kind === 'elective' ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
              @click="form.kind = 'elective'"
            >
              На выбор
            </button>
          </div>
        </div>
      </section>

      <!-- слайды -->
      <section class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <h2 class="text-[16px]">Слайды <span class="text-muted">· {{ slides.length }}</span></h2>
          <AppButton size="sm" variant="outline" @click="addSlide">
            <Plus :size="16" /> Слайд
          </AppButton>
        </div>

        <p v-if="!slides.length" class="border border-dashed border-line bg-surface p-6 text-center text-[14px] text-muted">
          Пока нет слайдов. Добавьте текст, картинку или видео.
        </p>

        <SlideEditor
          v-for="(s, i) in slides"
          :key="i"
          :slide="s"
          :index="i"
          :total="slides.length"
          @remove="slides.splice(i, 1)"
          @move-up="move(i, -1)"
          @move-down="move(i, 1)"
        />
      </section>

      <p v-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">{{ error }}</p>
    </template>

    <!-- нижняя панель сохранения -->
    <div
      v-if="!loading"
      class="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-surface/90 backdrop-blur-xl"
      style="padding-bottom: env(safe-area-inset-bottom)"
    >
      <div class="mx-auto flex max-w-lg items-center gap-3 px-4 py-3">
        <button
          class="flex items-center gap-2 text-[14px] font-medium transition-colors"
          :class="form.is_published ? 'text-accent' : 'text-muted hover:text-content'"
          @click="togglePublish"
        >
          <span
            class="relative h-5 w-9 rounded-full transition-colors"
            :class="form.is_published ? 'bg-accent' : 'bg-surface-2 border border-line'"
          >
            <span
              class="absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all"
              :class="form.is_published ? 'left-[18px]' : 'left-0.5'"
            ></span>
          </span>
          {{ form.is_published ? 'Опубликован' : 'Черновик' }}
        </button>
        <AppButton class="ml-auto" :loading="saving" @click="save">
          <Check v-if="saved" :size="18" /> {{ saved ? 'Сохранено' : 'Сохранить' }}
        </AppButton>
      </div>
    </div>
  </div>
</template>
