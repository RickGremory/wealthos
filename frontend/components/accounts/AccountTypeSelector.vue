<script setup lang="ts">
import { ACCOUNT_TYPE_OPTIONS, type BackendAccountType } from '~/utils/account-type-mapper'

const model = defineModel<BackendAccountType>({ default: 'checking' })

withDefaults(
  defineProps<{
    disabled?: boolean
  }>(),
  {
    disabled: false,
  },
)
</script>

<template>
  <fieldset class="type-selector" :disabled="disabled">
    <legend class="type-selector__legend">Tipo de cuenta</legend>
    <div class="type-selector__grid">
      <label
        v-for="option in ACCOUNT_TYPE_OPTIONS"
        :key="option.value"
        class="type-selector__option"
        :data-selected="model === option.value"
      >
        <input
          v-model="model"
          class="sr-only"
          type="radio"
          name="account-type-full"
          :value="option.value"
          :disabled="disabled"
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
}

@media (min-width: 720px) {
  .type-selector__grid {
    grid-template-columns: 1fr 1fr;
  }
}

.type-selector__option {
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
}

.type-selector__option[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.type-selector__label {
  font-weight: 600;
  color: var(--color-ink);
}

.type-selector__description {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
</style>
