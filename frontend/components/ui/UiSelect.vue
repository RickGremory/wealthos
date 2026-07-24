<script setup lang="ts">
export interface UiSelectOption {
  label: string
  value: string
}

const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    id?: string
    label?: string
    options: UiSelectOption[]
    disabled?: boolean
    required?: boolean
  }>(),
  {
    id: undefined,
    label: undefined,
    disabled: false,
    required: false,
  },
)
</script>

<template>
  <label class="ui-select stack-sm">
    <span v-if="label" class="ui-select__label">{{ label }}</span>
    <select
      :id="id"
      v-model="model"
      class="ui-select__control"
      :disabled="disabled"
      :required="required"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>

<style scoped>
.ui-select__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
}

.ui-select__control {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}
</style>
