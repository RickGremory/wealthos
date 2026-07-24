<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    id?: string
    label?: string
    autocomplete?: string
    disabled?: boolean
    required?: boolean
    error?: string
    placeholder?: string
  }>(),
  {
    id: undefined,
    label: 'Contraseña',
    autocomplete: 'current-password',
    disabled: false,
    required: false,
    error: undefined,
    placeholder: undefined,
  },
)

const visible = ref(false)
</script>

<template>
  <label class="password-input stack-sm">
    <span v-if="label" class="password-input__label">{{ label }}</span>
    <div class="password-input__row">
      <input
        :id="id"
        v-model="model"
        class="password-input__control"
        :type="visible ? 'text' : 'password'"
        :autocomplete="autocomplete"
        :disabled="disabled"
        :required="required"
        :placeholder="placeholder"
        :aria-invalid="Boolean(error) || undefined"
      >
      <button
        type="button"
        class="password-input__toggle"
        :aria-pressed="visible"
        :aria-label="visible ? 'Ocultar contraseña' : 'Mostrar contraseña'"
        :disabled="disabled"
        @click="visible = !visible"
      >
        {{ visible ? 'Ocultar' : 'Mostrar' }}
      </button>
    </div>
    <span v-if="error" class="password-input__error">{{ error }}</span>
  </label>
</template>

<style scoped>
.password-input {
  min-width: 0;
  width: 100%;
}

.password-input__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
}

.password-input__row {
  display: flex;
  gap: var(--space-2);
  align-items: stretch;
  min-width: 0;
  width: 100%;
}

.password-input__control {
  flex: 1 1 auto;
  min-width: 0;
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.password-input__control:disabled {
  background: var(--color-surface-muted);
  cursor: not-allowed;
}

.password-input__toggle {
  flex: 0 0 auto;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
  color: var(--color-slate-700);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0 0.65rem;
  cursor: pointer;
  white-space: nowrap;
}

.password-input__toggle:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.password-input__error {
  font-size: 0.8rem;
  color: var(--color-danger);
}

@media (max-width: 380px) {
  .password-input__toggle {
    padding: 0 0.5rem;
    font-size: 0.75rem;
  }
}
</style>
