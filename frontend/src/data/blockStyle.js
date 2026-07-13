// Акценты и нумерация блоков — фронтовое оформление поверх данных API.
const ELECTIVE_ACCENTS = ['#ff87ab', '#f58414', '#fccf50', '#b1aaff']

export function blockAccent(block, electiveIndex = 0) {
  if (block.kind === 'theory') return '#5612be'
  return ELECTIVE_ACCENTS[electiveIndex % ELECTIVE_ACCENTS.length]
}

export function blockNumber(n) {
  return String(n).padStart(2, '0')
}

// Русское склонение: plural(3, ['слайд','слайда','слайдов']) → 'слайда'
export function plural(n, forms) {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return forms[0]
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return forms[1]
  return forms[2]
}

// Прогресс блока из API-формы {last_slide, viewed, test_status}
export function blockPercent(block) {
  const p = block.progress || {}
  if (p.viewed) return 100
  if (p.last_slide > 0 && block.slide_count) {
    return Math.min(100, Math.round(((p.last_slide + 1) / block.slide_count) * 100))
  }
  return 0
}

export function blockState(block) {
  const p = block.progress || {}
  const done = p.test_status === 'passed' || (!block.has_test && p.viewed)
  if (done) return 'done'
  if (p.viewed || p.last_slide > 0) return 'progress'
  return 'new'
}
