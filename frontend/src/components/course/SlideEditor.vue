<script setup>
import { ref } from 'vue'
import { Type, Image as ImageIcon, Video, ArrowUp, ArrowDown, Trash2, Upload } from '@lucide/vue'
import { api } from '../../api/client'

const props = defineProps({
  slide: { type: Object, required: true },
  index: { type: Number, required: true },
  total: { type: Number, required: true },
})
const emit = defineEmits(['remove', 'move-up', 'move-down'])

const uploading = ref(false)
const uploadError = ref('')

const types = [
  { key: 'text', label: 'Текст', icon: Type },
  { key: 'image', label: 'Картинка', icon: ImageIcon },
  { key: 'video', label: 'Видео', icon: Video },
]

async function onFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadError.value = ''
  uploading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post('/media/image', form)
    props.slide.media_url = data.url
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Не удалось загрузить'
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}
</script>

<template>
  <div class="border border-line bg-surface">
    <!-- шапка слайда -->
    <div class="flex items-center justify-between border-b border-line px-3 py-2">
      <span class="font-display text-[13px] font-bold text-muted">Слайд {{ index + 1 }}</span>
      <div class="flex items-center gap-1">
        <button
          class="flex h-8 w-8 items-center justify-center text-muted transition-colors hover:bg-surface-2 hover:text-content disabled:opacity-30"
          :disabled="index === 0"
          title="Выше"
          @click="emit('move-up')"
        >
          <ArrowUp :size="16" />
        </button>
        <button
          class="flex h-8 w-8 items-center justify-center text-muted transition-colors hover:bg-surface-2 hover:text-content disabled:opacity-30"
          :disabled="index === total - 1"
          title="Ниже"
          @click="emit('move-down')"
        >
          <ArrowDown :size="16" />
        </button>
        <button
          class="flex h-8 w-8 items-center justify-center text-muted transition-colors hover:bg-pink/10 hover:text-pink"
          title="Удалить слайд"
          @click="emit('remove')"
        >
          <Trash2 :size="16" />
        </button>
      </div>
    </div>

    <div class="flex flex-col gap-3 p-3">
      <!-- тип слайда -->
      <div class="flex border border-line">
        <button
          v-for="t in types"
          :key="t.key"
          class="flex flex-1 items-center justify-center gap-1.5 py-2 text-[13px] font-medium transition-colors"
          :class="slide.type === t.key ? 'bg-accent text-on-accent' : 'text-muted hover:text-content'"
          @click="slide.type = t.key"
        >
          <component :is="t.icon" :size="15" /> {{ t.label }}
        </button>
      </div>

      <!-- текст -->
      <textarea
        v-if="slide.type === 'text'"
        v-model="slide.content"
        rows="4"
        placeholder="Текст слайда…"
        class="w-full resize-y rounded-xs border border-line bg-surface px-3 py-2.5 text-[15px] text-content focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
      ></textarea>

      <!-- картинка -->
      <template v-else-if="slide.type === 'image'">
        <div v-if="slide.media_url" class="relative overflow-hidden border border-line">
          <img :src="slide.media_url" alt="" class="max-h-64 w-full object-contain" />
        </div>
        <div class="flex items-center gap-2">
          <label
            class="inline-flex cursor-pointer items-center gap-2 border border-line px-3 py-2 text-[14px] text-content transition-colors hover:bg-surface-2"
          >
            <Upload :size="16" /> {{ uploading ? 'Загрузка…' : slide.media_url ? 'Заменить' : 'Загрузить' }}
            <input type="file" accept="image/*" class="hidden" @change="onFile" :disabled="uploading" />
          </label>
          <input
            v-model="slide.media_url"
            placeholder="или вставьте URL"
            class="min-w-0 flex-1 rounded-xs border border-line bg-surface px-3 py-2 text-[14px] text-content focus:border-accent focus:outline-none"
          />
        </div>
        <p v-if="uploadError" class="text-[13px] text-pink">{{ uploadError }}</p>
        <input
          v-model="slide.content"
          placeholder="Подпись (необязательно)"
          class="w-full rounded-xs border border-line bg-surface px-3 py-2 text-[14px] text-content focus:border-accent focus:outline-none"
        />
      </template>

      <!-- видео -->
      <template v-else>
        <input
          v-model="slide.media_url"
          placeholder="Ссылка на видео (YouTube, VK, mp4…)"
          class="w-full rounded-xs border border-line bg-surface px-3 py-2.5 text-[15px] text-content focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
        />
        <input
          v-model="slide.content"
          placeholder="Подпись (необязательно)"
          class="w-full rounded-xs border border-line bg-surface px-3 py-2 text-[14px] text-content focus:border-accent focus:outline-none"
        />
      </template>
    </div>
  </div>
</template>
