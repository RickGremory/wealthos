<script setup lang="ts">
const model = defineModel<string>({ default: '' })

const ICONS = [
  '🛒', '🍔', '🏠', '🚗', '💼', '✈️',
  '💡', '🏥', '📚', '🎮', '💰', '📦',
]
</script>

<template>
  <fieldset class="icon-picker">
    <legend class="icon-picker__legend">Ícono</legend>
    <div class="icon-picker__grid">
      <button
        v-for="icon in ICONS"
        :key="icon"
        type="button"
        class="icon-picker__item"
        :data-selected="model === icon"
        @click="model = icon"
      >
        {{ icon }}
      </button>
    </div>
  </fieldset>
</template>

<style scoped>
.icon-picker {
  border: 0;
  margin: 0;
  padding: 0;
}

.icon-picker__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  margin-bottom: var(--space-2);
}

.icon-picker__grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.icon-picker__item {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 1.15rem;
}

.icon-picker__item[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}
</style>
