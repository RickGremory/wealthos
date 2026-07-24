<script setup lang="ts">
import type { CategoryType } from '~/types/categories'

const model = defineModel<CategoryType>({ default: 'expense' })

withDefaults(
  defineProps<{
    disabled?: boolean
  }>(),
  { disabled: false },
)

const options: Array<{ value: CategoryType, label: string, description: string }> = [
  {
    value: 'expense',
    label: 'Gasto',
    description: 'Clasifica egresos y compras.',
  },
  {
    value: 'income',
    label: 'Ingreso',
    description: 'Clasifica cobros y entradas.',
  },
]
</script>

<template>
  <fieldset class="type-selector" :disabled="disabled">
    <legend class="type-selector__legend">Tipo</legend>
    <div class="type-selector__grid">
      <label
        v-for="option in options"
        :key="option.value"
        class="type-selector__option"
        :data-selected="model === option.value"
      >
        <input
          v-model="model"
          class="sr-only"
          type="radio"
          name="category-type"
          :value="option.value"
        >
        <span class="type-selector__label">{{ option.label }}</span>
        <span class="type-selector__description">{{ option.description }}</span>
      </label>
    </div>
  </fieldset>
</template>

<style scoped>
.type-selector {
  border: 0;
  margin: 0;
  padding: 0;
}

.type-selector__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  margin-bottom: var(--space-2);
}

.type-selector__grid {
  display: grid;
  gap: var(--space-2);
  grid-template-columns: 1fr 1fr;
}

.type-selector__option {
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.type-selector__option[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.type-selector__label {
  font-weight: 600;
}

.type-selector__description {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
</style>
