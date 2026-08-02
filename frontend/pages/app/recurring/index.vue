<script setup lang="ts">
import type { RecurringOccurrenceView, RecurringRuleListItemView } from '~/types/recurring'
import { createRecurringRepository } from '~/repositories/recurring.repository'
import { toUserMessage } from '~/lib/api/errors'
import { formatMoney } from '~/composables/use-money'
import { formatDate } from '~/composables/use-date'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite } = useOrganizationPermissions()
const {
  visibleRules,
  attentionOccurrences,
  upcomingOccurrences,
  summaryByCurrency,
  listLoading,
  occurrencesLoading,
  listError,
  occurrencesError,
  statusFilter,
  directionFilter,
  includeArchived,
  hasAny,
  load,
} = useRecurring()
const { openConfirm } = useRecurringConfirmation()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()

const skipTarget = ref<RecurringOccurrenceView | null>(null)
const skipLoading = ref(false)

onMounted(() => {
  void load()
})

function goNew() {
  return navigateTo('/app/recurring/new')
}

function goDetail(id: string) {
  return navigateTo(`/app/recurring/${id}`)
}

function directionLabel(direction: string) {
  if (direction === 'inflow') return 'Ingreso'
  if (direction === 'transfer') return 'Transferencia'
  return 'Gasto'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    active: 'Activo',
    paused: 'Pausado',
    ended: 'Finalizado',
    archived: 'Archivado',
    upcoming: 'Próximo',
    due: 'Por confirmar',
    overdue: 'Pendiente de confirmar',
    settled: 'Confirmado',
    partially_settled: 'Parcial',
    skipped: 'Omitido',
    cancelled: 'Cancelado',
  }
  return map[status] ?? status
}

async function confirmSkip(occurrence: RecurringOccurrenceView) {
  skipTarget.value = occurrence
}

async function doSkip() {
  const occurrence = skipTarget.value
  const orgId = organization.currentOrganizationId
  if (!occurrence || !orgId) return
  skipLoading.value = true
  try {
    const repo = createRecurringRepository($api)
    const detail = await repo.get(orgId, occurrence.recurringRuleId)
    await repo.createException(orgId, occurrence.recurringRuleId, {
      occurrenceKey: occurrence.occurrenceKey,
      exceptionType: 'skip',
      expectedVersion: detail.version,
      reason: 'Omitido desde Recurrentes',
    })
    cache.invalidateRecurring()
    toast.success('Ocurrencia omitida', occurrence.name)
    skipTarget.value = null
    await load()
  }
  catch (e) {
    toast.error('No se pudo omitir', toUserMessage(e))
  }
  finally {
    skipLoading.value = false
  }
}

function ruleCardMeta(item: RecurringRuleListItemView) {
  return [
    item.scheduleLabel,
    `${formatMoney(item.amount, item.currency)}`,
    directionLabel(item.direction),
  ].join(' · ')
}
</script>

<template>
  <div data-testid="recurring-page">
    <AppPageHeader
      title="Movimientos recurrentes"
      description="Organiza ingresos, pagos y transferencias que se repiten."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" data-testid="recurring-new-button" @click="goNew()">
          Nuevo recurrente
        </UiButton>
      </template>
    </AppPageHeader>

    <UiAlert v-if="listError || occurrencesError" tone="danger" title="No se pudo cargar">
      {{ listError || occurrencesError }}
    </UiAlert>

    <section v-if="summaryByCurrency.length" class="summary" data-testid="recurring-summary">
      <article
        v-for="group in summaryByCurrency"
        :key="group.currency"
        class="summary__card"
      >
        <h2>{{ group.currency }}</h2>
        <p>Ingresos previstos: {{ formatMoney(String(group.inflow), group.currency) }}</p>
        <p>Gastos previstos: {{ formatMoney(String(group.outflow), group.currency) }}</p>
        <p>Próximas: {{ group.upcoming }} · Pendientes: {{ group.pending }}</p>
      </article>
    </section>

    <section class="filters">
      <label>
        Estado
        <select v-model="statusFilter" data-testid="recurring-status-filter">
          <option value="all">Todos</option>
          <option value="attention">Pendientes de confirmar</option>
          <option value="active">Activos</option>
          <option value="paused">Pausados</option>
          <option value="ended">Finalizados</option>
          <option value="archived">Archivados</option>
        </select>
      </label>
      <label>
        Tipo
        <select v-model="directionFilter">
          <option value="all">Todos</option>
          <option value="inflow">Ingresos</option>
          <option value="outflow">Gastos</option>
          <option value="transfer">Transferencias</option>
        </select>
      </label>
      <label class="filters__check">
        <input v-model="includeArchived" type="checkbox">
        Incluir archivados
      </label>
    </section>

    <section v-if="attentionOccurrences.length" class="panel" data-testid="recurring-attention">
      <h2>Requiere atención</h2>
      <p class="muted">Pendientes de confirmar — no son vencimientos contractuales.</p>
      <ul class="rows">
        <li v-for="item in attentionOccurrences" :key="item.occurrenceKey" class="row">
          <div>
            <strong>{{ item.name }}</strong>
            <p class="muted">
              {{ formatDate(item.expectedOn) }} · {{ formatMoney(item.expectedAmount, item.currency) }}
              · {{ statusLabel(item.status) }}
            </p>
          </div>
          <div class="row__actions">
            <UiButton
              v-if="canWrite && item.canConfirm"
              size="sm"
              type="button"
              @click="openConfirm(item)"
            >
              Confirmar
            </UiButton>
            <UiButton
              v-if="canWrite && item.canSkip"
              size="sm"
              variant="secondary"
              type="button"
              @click="confirmSkip(item)"
            >
              Omitir
            </UiButton>
            <UiButton size="sm" variant="ghost" type="button" @click="goDetail(item.recurringRuleId)">
              Ver serie
            </UiButton>
          </div>
        </li>
      </ul>
    </section>

    <section class="panel">
      <h2>Próximas ocurrencias</h2>
      <UiSkeleton v-if="occurrencesLoading" style="height: 4rem" />
      <p v-else-if="!upcomingOccurrences.length" class="muted">
        No hay ocurrencias próximas en el horizonte.
      </p>
      <ul v-else class="rows">
        <li v-for="item in upcomingOccurrences.slice(0, 8)" :key="item.occurrenceKey" class="row">
          <div>
            <strong>{{ item.name }}</strong>
            <p class="muted">
              {{ formatDate(item.expectedOn) }} · {{ directionLabel(item.direction) }} ·
              {{ formatMoney(item.expectedAmount, item.currency) }}
            </p>
          </div>
          <div class="row__actions">
            <UiButton
              v-if="canWrite && item.canConfirm"
              size="sm"
              type="button"
              @click="openConfirm(item)"
            >
              Registrar
            </UiButton>
            <UiButton size="sm" variant="ghost" type="button" @click="goDetail(item.recurringRuleId)">
              Ver
            </UiButton>
          </div>
        </li>
      </ul>
    </section>

    <section class="panel" data-testid="recurring-rules">
      <h2>Reglas recurrentes</h2>
      <UiSkeleton v-if="listLoading" style="height: 6rem" />
      <div v-else-if="!hasAny" class="empty">
        <p>Todavía no tienes movimientos recurrentes.</p>
        <UiButton v-if="canWrite" type="button" @click="goNew()">
          Nuevo recurrente
        </UiButton>
      </div>
      <ul v-else class="rules">
        <li
          v-for="item in visibleRules"
          :key="item.id"
          class="rule"
          role="button"
          tabindex="0"
          @click="goDetail(item.id)"
          @keydown.enter="goDetail(item.id)"
        >
          <div>
            <strong>{{ item.name }}</strong>
            <p class="muted">{{ ruleCardMeta(item) }}</p>
            <p v-if="item.isManagedExternally" class="muted">
              Administrado desde otro módulo
            </p>
            <p v-if="item.nextOccurrence" class="muted">
              Próxima: {{ formatDate(item.nextOccurrence.expectedOn) }}
            </p>
          </div>
          <span class="badge">{{ statusLabel(item.status) }}</span>
        </li>
      </ul>
    </section>

    <Teleport to="body">
      <div v-if="skipTarget" class="dialog" role="dialog" aria-modal="true">
        <div class="dialog__card">
          <h3>¿Omitir esta ocurrencia?</h3>
          <p>
            {{ skipTarget.name }} del {{ formatDate(skipTarget.expectedOn) }} no se esperará
            en Planeación ni en el calendario.
          </p>
          <div class="dialog__actions">
            <UiButton variant="ghost" type="button" :disabled="skipLoading" @click="skipTarget = null">
              Cancelar
            </UiButton>
            <UiButton type="button" :loading="skipLoading" @click="doSkip">
              Omitir
            </UiButton>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.summary {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  margin-bottom: var(--space-5);
}
.summary__card,
.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}
.filters label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.85rem;
}
.filters__check {
  align-content: end;
}
.rows,
.rules {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}
.row,
.rule {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: center;
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-3);
}
.row:first-child,
.rule:first-child {
  border-top: 0;
  padding-top: 0;
}
.row__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
.rule {
  cursor: pointer;
}
.badge {
  font-size: 0.75rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: var(--color-surface-muted, #f3f4f6);
}
.muted {
  color: var(--color-text-muted);
  margin: 0.15rem 0 0;
}
.empty {
  display: grid;
  gap: var(--space-3);
  justify-items: start;
}
.dialog {
  position: fixed;
  inset: 0;
  background: rgb(0 0 0 / 0.35);
  display: grid;
  place-items: center;
  z-index: 60;
  padding: var(--space-4);
}
.dialog__card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  max-width: 26rem;
  width: 100%;
}
.dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-4);
}
</style>
