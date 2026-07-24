<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const auth = useAuthStore()
const toast = useToast()

const email = ref('')
const password = ref('')
const displayName = ref('')
const organizationName = ref('')
const error = ref('')
const submitting = ref(false)

async function onSubmit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      displayName: displayName.value,
      organizationName: organizationName.value,
    })
    toast.success('Cuenta creada', 'Ya puedes empezar a usar WealthOS')
    await navigateTo('/app')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo registrar'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard title="Crear cuenta">
    <form class="stack" @submit.prevent="onSubmit">
      <UiAlert v-if="error" tone="danger" title="Error">
        {{ error }}
      </UiAlert>

      <UiInput v-model="displayName" label="Nombre" required autocomplete="name" />
      <UiInput
        v-model="organizationName"
        label="Organización"
        required
        autocomplete="organization"
      />
      <UiInput
        v-model="email"
        label="Correo"
        type="email"
        required
        autocomplete="email"
      />
      <UiInput
        v-model="password"
        label="Contraseña"
        type="password"
        required
        autocomplete="new-password"
      />

      <UiButton type="submit" block :disabled="submitting">
        {{ submitting ? 'Creando…' : 'Crear cuenta' }}
      </UiButton>
    </form>

    <template #footer>
      <p class="text-muted">
        ¿Ya tienes cuenta?
        <NuxtLink to="/login">Inicia sesión</NuxtLink>
      </p>
    </template>
  </UiCard>
</template>
