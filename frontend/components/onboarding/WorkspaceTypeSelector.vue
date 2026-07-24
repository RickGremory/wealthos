<script setup lang="ts">
export type WorkspaceType = 'personal' | 'freelance' | 'business' | 'family'

const model = defineModel<WorkspaceType>({ default: 'freelance' })

const options: Array<{ value: WorkspaceType; label: string; description: string }> = [
  {
    value: 'personal',
    label: 'Personal',
    description: 'Finanzas personales o del hogar',
  },
  {
    value: 'freelance',
    label: 'Profesional independiente',
    description: 'Ingresos independientes o por proyecto',
  },
  {
    value: 'business',
    label: 'Negocio',
    description: 'Empresa o actividad comercial',
  },
  {
    value: 'family',
    label: 'Familiar',
    description: 'Presupuesto compartido en familia',
  },
]
</script>

<template>
  <fieldset class="workspace-type">
    <legend class="workspace-type__legend">Tipo de espacio</legend>
    <div class="workspace-type__grid">
      <label
        v-for="option in options"
        :key="option.value"
        class="workspace-type__option"
        :data-selected="model === option.value"
      >
        <input
          v-model="model"
          class="sr-only"
          type="radio"
          name="workspace-type"
          :value="option.value"
        >
        <span class="workspace-type__label">{{ option.label }}</span>
        <span class="workspace-type__description">{{ option.description }}</span>
      </label>
    </div>
  </fieldset>
</template>

<style scoped>
.workspace-type {
  border: 0;
  margin: 0;
  padding: 0;
}

.workspace-type__legend {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
  margin-bottom: var(--space-2);
}

.workspace-type__grid {
  display: grid;
  gap: var(--space-2);
}

.workspace-type__option {
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
}

.workspace-type__option[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.workspace-type__label {
  font-weight: 600;
  color: var(--color-ink);
}

.workspace-type__description {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
</style>
