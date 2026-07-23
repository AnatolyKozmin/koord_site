// Преобразует ссылку на видеоплатформу в URL для встраивания в <iframe>.
// Возвращает null, если это не распознанная платформа — тогда ссылку
// проигрываем как прямой файл через <video> (наши загруженные mp4/webm/mov).
export function videoEmbed(url) {
  if (!url) return null
  const u = url.trim()

  // YouTube: watch?v=, youtu.be/, embed/, shorts/, live/
  if (/youtu\.be|youtube\.com/.test(u)) {
    const m = u.match(/(?:youtu\.be\/|\/embed\/|\/shorts\/|\/live\/|[?&]v=)([\w-]{6,})/)
    if (m) return `https://www.youtube.com/embed/${m[1]}`
  }

  // VK Видео: готовый video_ext.php, либо vk.com/video-123_456 / vkvideo.ru/...
  const vkExt = u.match(/vk(?:video)?\.[a-z]+\/video_ext\.php\?([^#]+)/i)
  if (vkExt) return `https://vk.com/video_ext.php?${vkExt[1]}`
  const vk = u.match(/vk(?:video)?\.[a-z]+\/video(-?\d+)_(\d+)/i)
  if (vk) return `https://vk.com/video_ext.php?oid=${vk[1]}&id=${vk[2]}&hd=2`

  // Rutube: rutube.ru/video/HASH/ или уже /play/embed/HASH
  const rt = u.match(/rutube\.ru\/(?:video|play\/embed)\/(\w+)/i)
  if (rt) return `https://rutube.ru/play/embed/${rt[1]}`

  return null
}
