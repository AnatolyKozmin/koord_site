<script setup>
defineProps({
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  autocomplete: { type: String, default: 'off' },
  placeholder: { type: String, default: '' },
  error: { type: String, default: '' },
})
const model = defineModel({ type: String, default: '' })
</script>

<template>
  <label class="flex flex-col gap-1.5">
    <span
      v-if="label"
      class="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted"
    >{{ label }}</span>
    <input
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :class="[
        'w-full rounded-xs border bg-surface px-3.5 py-3 text-[15px] text-content',
        'placeholder:text-muted/60 transition-colors duration-150',
        'focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30',
        error ? 'border-pink' : 'border-line',
      ]"
    />
    <span v-if="error" class="text-[13px] text-pink">{{ error }}</span>
  </label>
</template>
