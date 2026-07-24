<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const email = ref('')
const submitted = ref(false)
const submitting = ref(false)

async function onSubmit() {
  submitting.value = true
  // UI-only stub until password reset API exists.
  await new Promise(resolve => setTimeout(resolve, 400))
  submitted.value = true
  submitting.value = false
}
</script>

<template>
  <UiCard title="Recuperar contraseña">
    <form v-if="!submitted" class="stack" @submit.prevent="onSubmit">
      <p class="text-muted">
        Escribe el correo de tu cuenta. Si existe, te enviaremos instrucciones para restablecerla.
      </p>
      <UiInput
        v-model="email"
        label="Correo"
        type="email"
        autocomplete="email"
        required
      />
      <UiButton type="submit" block :loading="submitting">
        Enviar instrucciones
      </UiButton>
    </form>

    <UiAlert v-else tone="success" title="Revisa tu correo">
      Si existe una cuenta con ese correo, recibirás instrucciones para restablecer tu contraseña.
    </UiAlert>

    <template #footer>
      <p class="text-muted">
        <NuxtLink to="/login">Volver a iniciar sesión</NuxtLink>
      </p>
    </template>
  </UiCard>
</template>
