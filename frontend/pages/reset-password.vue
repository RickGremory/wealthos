<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const done = ref(false)
const submitting = ref(false)
const passwordTouched = ref(false)

const { rules } = usePasswordRules(password)

async function onSubmit() {
  error.value = ''
  passwordTouched.value = true

  if (!rules.value.isValid) {
    error.value = 'La contraseña no cumple los requisitos'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  submitting.value = true
  // UI-only stub until password reset API exists.
  await new Promise(resolve => setTimeout(resolve, 400))
  done.value = true
  submitting.value = false
}
</script>

<template>
  <UiCard title="Restablecer contraseña">
    <form v-if="!done" class="stack" @submit.prevent="onSubmit">
      <UiAlert v-if="error" tone="danger" title="Error">
        {{ error }}
      </UiAlert>

      <p class="text-muted">
        Elige una contraseña nueva para tu cuenta.
      </p>

      <PasswordInput
        v-model="password"
        label="Nueva contraseña"
        autocomplete="new-password"
        required
        @update:model-value="passwordTouched = true"
      />
      <PasswordRequirements :rules="rules" :visible="passwordTouched" />
      <PasswordInput
        v-model="confirmPassword"
        label="Confirmar contraseña"
        autocomplete="new-password"
        required
      />

      <UiButton type="submit" block :loading="submitting" :disabled="!rules.isValid">
        Guardar contraseña
      </UiButton>
    </form>

    <div v-else class="stack">
      <UiAlert tone="success" title="Contraseña actualizada">
        Ya puedes iniciar sesión con tu nueva contraseña.
      </UiAlert>
      <UiButton block type="button" @click="navigateTo('/login')">
        Ir a iniciar sesión
      </UiButton>
    </div>
  </UiCard>
</template>
