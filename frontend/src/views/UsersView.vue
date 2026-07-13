<script setup>
import { computed, onMounted, ref } from 'vue'
import { UserPlus, Ban, RotateCcw, Trash2, ShieldCheck, X } from '@lucide/vue'
import { api } from '../api/client'
import { useAuthStore } from '../stores/auth'
import { ROLES, ROLE_LABELS } from '../constants/roles'
import AppButton from '../components/ui/AppButton.vue'
import AppField from '../components/ui/AppField.vue'

const auth = useAuthStore()

const users = ref([])
const loading = ref(true)
const error = ref('')
const showForm = ref(false)
const form = ref({ email: '', full_name: '', password: '', role: ROLES.COORDINATOR })

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/users')
    users.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось загрузить'
  } finally {
    loading.value = false
  }
}

async function createUser() {
  error.value = ''
  try {
    await api.post('/users', form.value)
    form.value = { email: '', full_name: '', password: '', role: ROLES.COORDINATOR }
    showForm.value = false
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка при создании'
  }
}

async function toggleActive(u) {
  try {
    await api.patch(`/users/${u.id}`, { is_active: !u.is_active })
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

async function removeUser(u) {
  if (!confirm(`Удалить пользователя ${u.email}?`)) return
  try {
    await api.delete(`/users/${u.id}`)
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка'
  }
}

const roleTone = {
  [ROLES.SUPERADMIN]: 'border-pink text-pink',
  [ROLES.TRAINING_COORDINATOR]: 'border-orange text-orange',
  [ROLES.COORDINATOR]: 'border-accent text-accent',
}

function initials(name) {
  const p = (name || '').split(' ').filter(Boolean)
  return (p[0]?.[0] || '') + (p[1]?.[0] || '') || '?'
}

onMounted(load)
</script>

<template>
  <div class="rise flex flex-col gap-5">
    <header class="flex items-end justify-between gap-3">
      <div>
        <p class="font-display text-[12px] font-semibold uppercase tracking-[0.2em] text-accent">
          Управление
        </p>
        <h1 class="mt-1.5 text-[26px]">Люди</h1>
      </div>
      <AppButton
        v-if="auth.isSuperadmin"
        :variant="showForm ? 'ghost' : 'primary'"
        size="sm"
        @click="showForm = !showForm"
      >
        <component :is="showForm ? X : UserPlus" :size="18" />
        {{ showForm ? 'Отмена' : 'Добавить' }}
      </AppButton>
    </header>

    <p v-if="error" class="border-l-2 border-pink bg-pink/10 px-3 py-2 text-[13px] text-pink">
      {{ error }}
    </p>

    <!-- форма создания -->
    <form
      v-if="showForm"
      class="rise flex flex-col gap-3 border border-line bg-surface p-4"
      @submit.prevent="createUser"
    >
      <div class="grid gap-3 sm:grid-cols-2">
        <AppField v-model="form.full_name" label="ФИО" placeholder="Иван Иванов" />
        <AppField v-model="form.email" label="Email" type="email" placeholder="you@koord.ru" />
        <AppField v-model="form.password" label="Пароль" type="password" placeholder="мин. 6 символов" />
        <label class="flex flex-col gap-1.5">
          <span class="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted">Роль</span>
          <select
            v-model="form.role"
            class="w-full rounded-xs border border-line bg-surface px-3.5 py-3 text-[15px] text-content focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/30"
          >
            <option v-for="(label, value) in ROLE_LABELS" :key="value" :value="value">{{ label }}</option>
          </select>
        </label>
      </div>
      <AppButton type="submit" variant="primary" size="md" block>Создать пользователя</AppButton>
    </form>

    <!-- скелетоны -->
    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 3" :key="i" class="skeleton h-[76px] border border-line"></div>
    </div>

    <!-- список -->
    <div v-else class="flex flex-col gap-3">
      <div
        v-for="u in users"
        :key="u.id"
        class="flex items-center gap-3 border border-line bg-surface p-3.5"
        :class="!u.is_active && 'opacity-60'"
      >
        <div
          class="flex h-11 w-11 flex-none items-center justify-center bg-surface-2 font-display text-[15px] font-bold text-accent"
        >
          {{ initials(u.full_name) }}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <p class="truncate font-semibold">{{ u.full_name }}</p>
            <ShieldCheck v-if="u.id === auth.user?.id" :size="15" class="flex-none text-accent" />
          </div>
          <p class="truncate text-[13px] text-muted">{{ u.email }}</p>
        </div>
        <span
          class="hidden flex-none border-l-2 bg-surface-2 px-2 py-0.5 text-[12px] font-semibold sm:inline-block"
          :class="roleTone[u.role]"
        >{{ ROLE_LABELS[u.role] }}</span>

        <div v-if="auth.isSuperadmin && u.id !== auth.user?.id" class="flex flex-none items-center gap-1">
          <button
            class="flex h-9 w-9 items-center justify-center text-muted transition-colors hover:bg-surface-2 hover:text-content"
            :title="u.is_active ? 'Заблокировать' : 'Разблокировать'"
            @click="toggleActive(u)"
          >
            <component :is="u.is_active ? Ban : RotateCcw" :size="17" />
          </button>
          <button
            class="flex h-9 w-9 items-center justify-center text-muted transition-colors hover:bg-pink/10 hover:text-pink"
            title="Удалить"
            @click="removeUser(u)"
          >
            <Trash2 :size="17" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
