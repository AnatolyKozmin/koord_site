<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary | glow | outline | ghost
  size: { type: String, default: 'md' }, // sm | md | lg
  loading: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const base =
  'relative inline-flex items-center justify-center gap-2 font-medium select-none ' +
  'transition-[transform,background,box-shadow] duration-150 active:scale-[0.97] ' +
  'disabled:opacity-50 disabled:pointer-events-none rounded-xs'

const sizes = {
  sm: 'text-sm px-3.5 py-2',
  md: 'text-[15px] px-5 py-3',
  lg: 'text-base px-6 py-3.5',
}

const variants = {
  primary:
    'bg-accent text-on-accent hover:brightness-110 shadow-[0_6px_20px_-6px] shadow-purple/50',
  glow:
    'text-white font-display font-semibold tracking-wide glow-text ' +
    'bg-gradient-to-br from-lavender via-pink to-orange hover:brightness-105',
  outline:
    'border border-line text-content hover:bg-surface-2 bg-transparent',
  ghost: 'text-content hover:bg-surface-2 bg-transparent',
}

const classes = computed(() => [
  base,
  sizes[props.size],
  variants[props.variant],
  props.block ? 'w-full' : '',
])

function onClick(e) {
  if (props.loading) return
  if (navigator.vibrate) navigator.vibrate(8)
  emit('click', e)
}
</script>

<template>
  <button :class="classes" :disabled="loading" @click="onClick">
    <span
      v-if="loading"
      class="absolute inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
    />
    <span :class="['inline-flex items-center gap-2', loading && 'opacity-0']">
      <slot />
    </span>
  </button>
</template>
