<script setup lang="ts">
import type { CategoryTabFilter } from '~/types/categories'

const model = defineModel<CategoryTabFilter>({ default: 'expense' })

const tabs: Array<{ value: CategoryTabFilter, label: string }> = [
  { value: 'expense', label: 'Gastos' },
  { value: 'income', label: 'Ingresos' },
  { value: 'system', label: 'Sistema' },
  { value: 'archived', label: 'Archivadas' },
]
</script>

<template>
  <div class="category-tabs" role="tablist" aria-label="Filtro de categorías">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      type="button"
      role="tab"
      class="category-tabs__tab"
      :aria-selected="model === tab.value"
      :data-active="model === tab.value"
      @click="model = tab.value"
    >
      {{ tab.label }}
    </button>
  </div>
</template>

<style scoped>
.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.category-tabs__tab {
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  color: var(--color-slate-700);
  border-radius: var(--radius-md);
  padding: 0.45rem 0.85rem;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.category-tabs__tab[data-active='true'] {
  background: var(--color-teal-50);
  border-color: var(--color-teal-700);
  color: var(--color-teal-900);
}
</style>
