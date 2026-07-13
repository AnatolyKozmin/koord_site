<script setup>
// Маяк — маскот бренда. Чистый лёгкий SVG по мотивам Figma-брендборда.
const props = defineProps({
  glow: { type: Boolean, default: true },
  tower: { type: String, default: '#441766' },
})
const uid = Math.random().toString(36).slice(2, 8)
</script>

<template>
  <svg viewBox="0 0 120 300" fill="none" xmlns="http://www.w3.org/2000/svg" role="img"
       aria-label="Маяк">
    <defs>
      <radialGradient :id="`halo-${uid}`" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#dfabff" stop-opacity="0.85" />
        <stop offset="45%" stop-color="#dfabff" stop-opacity="0.4" />
        <stop offset="100%" stop-color="#dfabff" stop-opacity="0" />
      </radialGradient>
      <linearGradient :id="`lamp-${uid}`" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#fff6d8" />
        <stop offset="100%" stop-color="#fccf50" />
      </linearGradient>
      <clipPath :id="`tower-${uid}`">
        <path d="M39 83 L81 83 L99 289 L21 289 Z" />
      </clipPath>
    </defs>

    <!-- лиловый ореол свечения -->
    <ellipse v-if="glow" cx="60" cy="52" rx="58" ry="50" :fill="`url(#halo-${uid})`" />

    <!-- шпиль -->
    <path d="M60 4 L60 18" :stroke="tower" stroke-width="4" stroke-linecap="round" />
    <circle cx="60" cy="6" r="4" :fill="tower" />

    <!-- крыша фонаря -->
    <path d="M60 16 L88 46 L32 46 Z" :fill="tower" />

    <!-- фонарь (светится) -->
    <rect x="38" y="46" width="44" height="30" :fill="glow ? `url(#lamp-${uid})` : '#f3f2f2'" />
    <rect x="47.5" y="46" width="4" height="30" :fill="tower" />
    <rect x="58" y="46" width="4" height="30" :fill="tower" />
    <rect x="68.5" y="46" width="4" height="30" :fill="tower" />

    <!-- галерея под фонарём -->
    <rect x="30" y="76" width="60" height="9" :fill="tower" />

    <!-- корпус башни -->
    <path d="M39 83 L81 83 L99 289 L21 289 Z" :fill="tower" />

    <!-- белые полосы -->
    <g :clip-path="`url(#tower-${uid})`">
      <rect x="0" y="118" width="120" height="15" fill="#f3f2f2" />
      <rect x="0" y="196" width="120" height="17" fill="#f3f2f2" />
      <rect x="0" y="262" width="120" height="27" fill="#f3f2f2" />
    </g>

    <!-- арочное окно -->
    <path d="M52 168 a8 8 0 0 1 16 0 v13 h-16 Z"
          :fill="glow ? `url(#lamp-${uid})` : '#f3f2f2'" />

    <!-- дверь в основании -->
    <path d="M51 289 v-15 a9 9 0 0 1 18 0 v15 Z" :fill="tower" />
  </svg>
</template>
