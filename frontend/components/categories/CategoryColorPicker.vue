<script setup lang="ts">
const model = defineModel<string>({ default: '' })

const SWATCHES = [
  '#0f524e',
  '#1a8a82',
  '#0a1628',
  '#334155',
  '#b42318',
  '#b54708',
  '#067647',
  '#175cd3',
  '#6941c6',
  '#c11574',
  '#875a00',
  '#3f3f46',
]
</script>

<template>
  <fieldset class="color-picker">
    <legend class="color-picker__legend">Color</legend>
    <div class="color-picker__grid">
      <button
        v-for="swatch in SWATCHES"
        :key="swatch"
        type="button"
        class="color-picker__swatch"
        :style="{ background: swatch }"
        :data-selected="model === swatch"
        :aria-label="`Color ${swatch}`"
        @click="model = swatch"
      />
    </div>
  </fieldset>
</template>

<style scoped>
.color-picker {
  border: 0;
  margin: 0;
  padding: 0;
}

.color-picker__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  margin-bottom: var(--space-2);
}

.color-picker__grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.color-picker__swatch {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 999px;
  border: 2px solid transparent;
  cursor: pointer;
}

.color-picker__swatch[data-selected='true'] {
  border-color: var(--color-ink);
  outline: 2px solid var(--color-teal-100);
}
</style>
