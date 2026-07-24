<script setup lang="ts">
import { GOAL_TEMPLATES } from '~/utils/goal-templates'

const model = defineModel<string | null>({ default: null })

const emit = defineEmits<{
  select: [templateId: string]
}>()

function onSelect(id: string) {
  model.value = id
  emit('select', id)
}
</script>

<template>
  <div class="template-picker" data-testid="goal-template-picker">
    <p class="template-picker__intro text-muted">
      Elige una plantilla para empezar más rápido. Solo rellena el formulario; puedes editarlo.
    </p>
    <div class="template-picker__grid">
      <button
        v-for="template in GOAL_TEMPLATES"
        :key="template.id"
        type="button"
        class="template-picker__item"
        :data-active="model === template.id"
        :data-testid="`goal-template-${template.id}`"
        @click="onSelect(template.id)"
      >
        <span class="template-picker__emoji" aria-hidden="true">{{ template.emoji }}</span>
        <span class="template-picker__name">{{ template.name }}</span>
        <span class="template-picker__desc text-muted">{{ template.description }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.template-picker {
  display: grid;
  gap: var(--space-3);
}

.template-picker__intro {
  margin: 0;
  font-size: 0.9rem;
}

.template-picker__grid {
  display: grid;
  gap: var(--space-2);
  grid-template-columns: repeat(auto-fill, minmax(10.5rem, 1fr));
}

.template-picker__item {
  display: grid;
  gap: 0.25rem;
  text-align: left;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font: inherit;
  cursor: pointer;
  transition: border-color 140ms ease, background 140ms ease;
}

.template-picker__item:hover {
  border-color: var(--color-teal-600);
}

.template-picker__item[data-active='true'] {
  background: var(--color-teal-50);
  border-color: var(--color-teal-700);
}

.template-picker__emoji {
  font-size: 1.25rem;
}

.template-picker__name {
  font-weight: 600;
  font-size: 0.9rem;
}

.template-picker__desc {
  font-size: 0.75rem;
  line-height: 1.35;
}
</style>
