<script setup lang="ts">
import {
  SIMPLIFIED_ACCOUNT_TYPE_OPTIONS,
  type SimplifiedAccountType,
} from '~/utils/account-type-mapper'

const model = defineModel<SimplifiedAccountType>({ default: 'checking' })
</script>

<template>
  <fieldset class="account-type">
    <legend class="account-type__legend">Tipo de cuenta</legend>
    <div class="account-type__grid">
      <label
        v-for="option in SIMPLIFIED_ACCOUNT_TYPE_OPTIONS"
        :key="option.value"
        class="account-type__option"
        :data-selected="model === option.value"
      >
        <input
          v-model="model"
          class="sr-only"
          type="radio"
          name="account-type"
          :value="option.value"
        >
        <span class="account-type__label">{{ option.label }}</span>
        <span class="account-type__description">{{ option.description }}</span>
      </label>
    </div>
  </fieldset>
</template>

<style scoped>
.account-type {
  border: 0;
  margin: 0;
  padding: 0;
}

.account-type__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  margin-bottom: var(--space-2);
}

.account-type__grid {
  display: grid;
  gap: var(--space-2);
}

.account-type__option {
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
}

.account-type__option[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.account-type__label {
  font-weight: 600;
  color: var(--color-ink);
}

.account-type__description {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
</style>
