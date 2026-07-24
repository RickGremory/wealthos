<script setup lang="ts">
import { GOAL_TEMPLATES } from '~/utils/goal-templates'

defineProps<{
  canWrite?: boolean
}>()

function goNew(templateId?: string) {
  const query = templateId ? `?template=${templateId}` : ''
  return navigateTo(`/app/goals/new${query}`)
}

const quick = GOAL_TEMPLATES.slice(0, 4)
</script>

<template>
  <UiCard data-testid="goal-empty-state">
    <UiEmptyState
      title="Sin metas todavía"
      description="Convierte tus ingresos en patrimonio con un objetivo claro. Empieza con una plantilla o crea una meta a tu medida."
    >
      <template v-if="canWrite" #actions>
        <div class="goal-empty">
          <div class="goal-empty__quick">
            <UiButton
              v-for="item in quick"
              :key="item.id"
              type="button"
              variant="secondary"
              @click="goNew(item.id)"
            >
              {{ item.emoji }} {{ item.name }}
            </UiButton>
          </div>
          <UiButton type="button" @click="goNew()">
            Nueva meta
          </UiButton>
        </div>
      </template>
    </UiEmptyState>
  </UiCard>
</template>

<style scoped>
.goal-empty {
  display: grid;
  gap: var(--space-3);
  justify-items: center;
}

.goal-empty__quick {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}
</style>
