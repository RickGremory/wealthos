<script setup lang="ts">
import type { CommitmentListItemView, PaymentStrategy } from '~/types/commitments'
import { createCommitmentsRepository } from '~/repositories/commitments.repository'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite, canArchive } = useOrganizationPermissions()
const {
  visibleItems,
  attentionItems,
  summary,
  strategy,
  listLoading,
  summaryLoading,
  strategyLoading,
  listError,
  strategyError,
  statusFilter,
  includeArchived,
  hasAny,
  hasActive,
  load,
  loadStrategy,
} = useCommitments()
const cache = useFinanceCache()
const toast = useToast()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()
const { openPayment } = useCommitmentPayment()

const archiveTarget = ref<CommitmentListItemView | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)
const strategyUpdating = ref(false)

onMounted(() => {
  void load()
})

function goNew() {
  return navigateTo('/app/commitments/new')
}

function goDetail(id: string) {
  return navigateTo(`/app/commitments/${id}`)
}

function goEdit(id: string) {
  return navigateTo(`/app/commitments/${id}/edit`)
}

function openArchive(item: CommitmentListItemView) {
  archiveTarget.value = item
  archiveOpen.value = true
}

async function confirmArchive() {
  if (!archiveTarget.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  archiveLoading.value = true
  try {
    const repo = createCommitmentsRepository($api)
    await repo.archive(orgId, archiveTarget.value.id)
    cache.invalidateCommitments()
    toast.success('Obligación archivada', archiveTarget.value.name)
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

async function onStrategyChange(next: PaymentStrategy) {
  const orgId = organization.currentOrganizationId
  if (!orgId || !canArchive.value) return
  strategyUpdating.value = true
  try {
    const repo = createCommitmentsRepository($api)
    await repo.updateStrategy(orgId, next)
    cache.invalidateCommitments()
    toast.success('Estrategia actualizada')
    await loadStrategy()
  }
  catch (e) {
    toast.error('No se pudo cambiar la estrategia', toUserMessage(e))
  }
  finally {
    strategyUpdating.value = false
  }
}
</script>

<template>
  <div data-testid="commitments-page">
    <AppPageHeader
      title="Obligaciones"
      description="Lo que ya compromete tu dinero futuro."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" data-testid="commitment-new-button" @click="goNew()">
          Nueva obligación
        </UiButton>
      </template>
    </AppPageHeader>

    <CommitmentSummary
      class="commitments-summary"
      :summary="summary"
      :loading="summaryLoading"
    />

    <div class="commitments-layout">
      <div class="commitments-main">
        <section
          v-if="attentionItems.length && statusFilter !== 'attention'"
          class="commitments-attention"
          aria-label="Requieren atención"
        >
          <h2 class="commitments-attention__title">Requieren atención</h2>
          <div class="commitments-grid">
            <CommitmentCard
              v-for="item in attentionItems.slice(0, 3)"
              :key="`att-${item.id}`"
              :commitment="item"
              :can-write="canWrite"
              :can-archive="canArchive"
              @view="goDetail(item.id)"
              @edit="goEdit(item.id)"
              @archive="openArchive(item)"
              @pay="openPayment(item)"
            />
          </div>
        </section>

        <section class="commitments-toolbar cluster" aria-label="Filtros">
          <button
            v-for="opt in [
              { id: 'all', label: 'Todas' },
              { id: 'attention', label: 'Atención' },
              { id: 'active', label: 'Activas' },
              { id: 'paused', label: 'Pausadas' },
              { id: 'closed', label: 'Cerradas' },
            ]"
            :key="opt.id"
            type="button"
            class="chip"
            :data-active="statusFilter === opt.id"
            @click="statusFilter = opt.id as typeof statusFilter"
          >
            {{ opt.label }}
          </button>
          <button
            type="button"
            class="chip"
            :data-active="includeArchived"
            @click="includeArchived = !includeArchived"
          >
            Incluir archivadas
          </button>
        </section>

        <section class="commitments-list" aria-label="Listado de obligaciones">
          <div v-if="listLoading" class="commitments-grid">
            <UiSkeleton height="12rem" />
            <UiSkeleton height="12rem" />
          </div>
          <UiAlert
            v-else-if="listError"
            tone="danger"
            title="No se pudieron cargar las obligaciones"
          >
            {{ listError }}
          </UiAlert>
          <CommitmentEmptyState
            v-else-if="!hasAny || (!hasActive && !includeArchived && statusFilter === 'all')"
            :can-write="canWrite"
          />
          <UiEmptyState
            v-else-if="!visibleItems.length"
            title="Sin resultados"
            description="Prueba otro filtro o incluye archivadas."
          />
          <div v-else class="commitments-grid">
            <CommitmentCard
              v-for="item in visibleItems"
              :key="item.id"
              :commitment="item"
              :can-write="canWrite"
              :can-archive="canArchive"
              @view="goDetail(item.id)"
              @edit="goEdit(item.id)"
              @archive="openArchive(item)"
              @pay="openPayment(item)"
            />
          </div>
        </section>
      </div>

      <aside class="commitments-side">
        <CommitmentStrategyPanel
          :strategy="strategy"
          :loading="strategyLoading"
          :error="strategyError"
          :can-manage="canArchive"
          :updating="strategyUpdating"
          @change="onStrategyChange"
          @open="goDetail"
        />
      </aside>
    </div>

    <CommitmentArchiveDialog
      v-model:open="archiveOpen"
      :commitment="archiveTarget"
      :loading="archiveLoading"
      @confirm="confirmArchive"
    />
  </div>
</template>

<style scoped>
.commitments-summary {
  margin-bottom: var(--space-5);
}

.commitments-layout {
  display: grid;
  gap: var(--space-5);
}

@media (min-width: 1100px) {
  .commitments-layout {
    grid-template-columns: minmax(0, 1fr) minmax(16rem, 22rem);
    align-items: start;
  }
}

.commitments-attention {
  margin-bottom: var(--space-5);
}

.commitments-attention__title {
  margin: 0 0 var(--space-3);
  font-size: 1rem;
}

.commitments-toolbar {
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

.commitments-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 800px) {
  .commitments-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
