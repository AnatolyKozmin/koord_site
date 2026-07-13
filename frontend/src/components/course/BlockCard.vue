<script setup>
import { computed } from 'vue'
import { BookOpen, FileCheck2, Award, Play, Pencil, EyeOff } from '@lucide/vue'
import { blockPercent, blockState, plural } from '../../data/blockStyle'

const props = defineProps({
  block: { type: Object, required: true },
  accent: { type: String, default: '#5612be' },
  number: { type: String, default: '01' },
  featured: { type: Boolean, default: false },
  editable: { type: Boolean, default: false },
})

const pct = computed(() => blockPercent(props.block))
const to = computed(() =>
  props.editable ? `/editor/${props.block.id}` : `/course/${props.block.id}`,
)

const state = computed(() => {
  const s = blockState(props.block)
  if (s === 'done') return { label: 'Завершён', icon: Award, cls: 'bg-gold/15 text-[#8a6b12]' }
  if (s === 'progress') return { label: 'В процессе', icon: Play, cls: 'text-accent' }
  return { label: 'Не начат', icon: null, cls: 'text-muted' }
})
</script>

<template>
  <RouterLink
    :to="to"
    class="group block border border-line bg-surface p-5 transition-[transform,box-shadow,border-color] duration-200 hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-[0_16px_40px_-24px_rgba(21,12,28,0.55)] active:scale-[0.99]"
    :style="{ '--c': accent }"
  >
    <div v-if="featured" class="mesh grain relative mb-4 -mx-5 -mt-5 h-20 overflow-hidden">
      <span
        class="absolute left-5 top-4 border-l-2 border-white/70 bg-black/15 px-2 py-1 font-display text-[11px] font-semibold uppercase tracking-[0.14em] text-white backdrop-blur-sm"
      >Обязательно для всех</span>
    </div>

    <div class="flex items-start justify-between gap-3">
      <span class="font-display text-[30px] font-bold leading-none" :style="{ color: 'var(--c)' }">
        {{ number }}
      </span>

      <div class="flex items-center gap-2">
        <span
          v-if="editable && !block.is_published"
          class="inline-flex items-center gap-1 border-l-2 border-muted bg-surface-2 px-2 py-1 text-[12px] font-semibold text-muted"
        >
          <EyeOff :size="13" /> Черновик
        </span>
        <span
          v-else
          class="inline-flex items-center gap-1.5 px-2.5 py-1 text-[12px] font-semibold"
          :class="state.cls"
        >
          <component :is="state.icon" v-if="state.icon" :size="14" />
          {{ state.label }}
        </span>
        <Pencil v-if="editable" :size="16" class="text-muted transition-colors group-hover:text-accent" />
      </div>
    </div>

    <h3 class="mt-3 text-[19px] leading-tight">{{ block.title }}</h3>
    <p class="mt-1.5 line-clamp-2 text-[14px] leading-snug text-muted">{{ block.description }}</p>

    <div class="mt-4 h-1.5 w-full overflow-hidden bg-surface-2">
      <div class="h-full transition-[width] duration-500" :style="{ width: pct + '%', background: 'var(--c)' }"></div>
    </div>

    <div class="mt-3 flex items-center gap-4 text-[13px] text-muted">
      <span class="inline-flex items-center gap-1.5">
        <BookOpen :size="15" /> {{ block.slide_count }} {{ plural(block.slide_count, ['слайд', 'слайда', 'слайдов']) }}
      </span>
      <span v-if="block.has_test" class="inline-flex items-center gap-1.5">
        <FileCheck2 :size="15" /> тест
      </span>
      <span class="ml-auto font-semibold tabular-nums" :style="{ color: 'var(--c)' }">{{ pct }}%</span>
    </div>
  </RouterLink>
</template>
