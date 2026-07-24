<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const auth = useAuthStore()
const toast = useToast()
const { resolveDestination } = useSessionEntry()

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function onSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    const organization = useOrganizationStore()
    await organization.loadMemberships()
    toast.success('Bienvenido', 'Sesión iniciada correctamente')
    const destination = await resolveDestination()
    await navigateTo(destination)
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
      <PasswordInput
        v-model="password"
        label="Contraseña"
        autocomplete="current-password"
        required
      />

      <p class="login-forgot">
        <NuxtLink to="/forgot-password">¿Olvidaste tu contraseña?</NuxtLink>
      </p>

      <UiButton type="submit" block :loading="submitting">
        Entrar
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

<style scoped>
.login-forgot {
  margin: calc(var(--space-2) * -1) 0 0;
  font-size: 0.875rem;
  text-align: right;
  overflow-wrap: anywhere;
}

.login-forgot a {
  display: inline-block;
  max-width: 100%;
}
</style>
