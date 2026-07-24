<script setup lang="ts">
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    id?: string
    label?: string
    type?: string
    placeholder?: string
    autocomplete?: string
    disabled?: boolean
    required?: boolean
    error?: string
  }>(),
  {
    id: undefined,
    label: undefined,
    type: 'text',
    placeholder: undefined,
    autocomplete: undefined,
    disabled: false,
    required: false,
    error: undefined,
  },
)
</script>

<template>
  <label class="ui-input stack-sm">
    <span v-if="label" class="ui-input__label">{{ label }}</span>
    <input
      :id="id"
      v-model="model"
      class="ui-input__control"
      :type="type"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :disabled="disabled"
      :required="required"
      :aria-invalid="Boolean(error) || undefined"
    >
    <span v-if="error" class="ui-input__error">{{ error }}</span>
  </label>
</template>

<style scoped>
.ui-input__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
}

.ui-input__control {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.ui-input__control:disabled {
  background: var(--color-surface-muted);
  cursor: not-allowed;
}

.ui-input__error {
  font-size: 0.8rem;
  color: var(--color-danger);
}
</style>
