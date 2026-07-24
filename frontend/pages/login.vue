<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const auth = useAuthStore()
const toast = useToast()

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function onSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    toast.success('Bienvenido', 'Sesión iniciada correctamente')
    await navigateTo('/app')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo iniciar sesión'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard title="Iniciar sesión">
    <form class="stack" @submit.prevent="onSubmit">
      <UiAlert v-if="error" tone="danger" title="Error">
        {{ error }}
      </UiAlert>

      <UiInput
        v-model="email"
        label="Correo"
        type="email"
        autocomplete="email"
        required
      />
      <UiInput
        v-model="password"
        label="Contraseña"
        type="password"
        autocomplete="current-password"
        required
      />

      <UiButton type="submit" block :disabled="submitting">
        {{ submitting ? 'Entrando…' : 'Entrar' }}
      </UiButton>
    </form>

    <template #footer>
      <p class="text-muted">
        ¿No tienes cuenta?
        <NuxtLink to="/register">Regístrate</NuxtLink>
      </p>
    </template>
  </UiCard>
</template>
