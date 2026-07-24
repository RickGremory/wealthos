<script setup lang="ts">
import type { PasswordRulesResult } from '~/composables/use-password-rules'

defineProps<{
  rules: PasswordRulesResult
  visible?: boolean
}>()
</script>

<template>
  <ul v-if="visible" class="password-requirements" aria-live="polite">
    <li :data-ok="rules.minLength">Al menos 8 caracteres</li>
    <li :data-ok="rules.hasLetter">Incluye una letra</li>
    <li :data-ok="rules.hasNumber">Incluye un número</li>
  </ul>
</template>

<style scoped>
.password-requirements {
  margin: 0;
  padding-left: 1.1rem;
  display: grid;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.password-requirements li[data-ok='true'] {
  color: var(--color-success);
}

.password-requirements li[data-ok='false'] {
  color: var(--color-text-muted);
}
</style>
