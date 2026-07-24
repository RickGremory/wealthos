<script setup lang="ts">
import type { GoalListItemView } from '~/types/goals'
import { createGoalsRepository } from '~/repositories/goals.repository'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite, canArchive } = useOrganizationPermissions()
const {
  visibleGoals,
  summary,
  listLoading,
  listError,
  includeArchived,
  hasAnyGoals,
  hasActiveGoals,
  load,
} = useGoals()
const cache = useFinanceCache()
const toast = useToast()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()

const archiveTarget = ref<GoalListItemView | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)

onMounted(() => {
  void load()
})

function goNew() {
  return navigateTo('/app/goals/new')
}

function goDetail(id: string) {
  return navigateTo(`/app/goals/${id}`)
}

function goEdit(id: string) {
  return navigateTo(`/app/goals/${id}/edit`)
}

function openArchive(goal: GoalListItemView) {
  archiveTarget.value = goal
  archiveOpen.value = true
}

async function confirmArchive() {
  if (!archiveTarget.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  archiveLoading.value = true
  try {
    const repo = createGoalsRepository($api)
    await repo.archive(orgId, archiveTarget.value.id)
    cache.invalidateGoals()
    toast.success('Meta archivada', archiveTarget.value.name)
    archiveOpen.value = false
    archiveTarget.value = null
    await load()
  }
  catch (e) {
    toast.error('No se pudo archivar', toUserMessage(e))
  }
  finally {
    archiveLoading.value = false
  }
}
</script>

<template>
  <div data-testid="goals-page">
    <AppPageHeader
      title="Metas"
      description="Convierte tus ingresos en patrimonio."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" data-testid="goal-new-button" @click="goNew()">
          Nueva meta
        </UiButton>
      </template>
    </AppPageHeader>

    <GoalSummary
      class="goals-summary"
      :summary="summary"
      :loading="listLoading"
    />

    <section class="goals-toolbar cluster" aria-label="Filtros">
      <button
        type="button"
        class="chip"
        :data-active="!includeArchived"
        @click="includeArchived = false"
      >
        Activas
      </button>
      <button
        type="button"
        class="chip"
        :data-active="includeArchived"
        data-testid="goals-show-archived"
        @click="includeArchived = true"
      >
        Incluir archivadas
      </button>
    </section>

    <section class="goals-list" aria-label="Listado de metas">
      <div v-if="listLoading" class="goals-grid">
        <UiSkeleton height="10rem" />
        <UiSkeleton height="10rem" />
        <UiSkeleton height="10rem" />
      </div>
      <UiAlert v-else-if="listError" tone="danger" title="No se pudieron cargar las metas">
        {{ listError }}
      </UiAlert>
      <GoalEmptyState
        v-else-if="!hasAnyGoals || (!hasActiveGoals && !includeArchived)"
        :can-write="canWrite"
      />
      <UiEmptyState
        v-else-if="!visibleGoals.length"
        title="Sin resultados"
        description="No hay metas archivadas todavía."
      />
      <div v-else class="goals-grid">
        <GoalCard
          v-for="goal in visibleGoals"
          :key="goal.id"
          :goal="goal"
          :can-write="canWrite"
          :can-archive="canArchive"
          @view="goDetail(goal.id)"
          @edit="goEdit(goal.id)"
          @archive="openArchive(goal)"
        />
      </div>
    </section>

    <GoalArchiveDialog
      v-model:open="archiveOpen"
      :goal="archiveTarget"
      :loading="archiveLoading"
      @confirm="confirmArchive"
    />
  </div>
</template>

<style scoped>
.goals-summary {
  margin-bottom: var(--space-5);
}

.goals-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
}

.chip {
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  color: var(--color-slate-700);
  border-radius: var(--radius-md);
  padding: 0.4rem 0.75rem;
  font: inherit;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.chip[data-active='true'] {
  background: var(--color-teal-50);
  border-color: var(--color-teal-700);
  color: var(--color-teal-900);
}

.goals-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 800px) {
  .goals-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
