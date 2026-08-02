<script setup lang="ts">
import { createRecurringRepository } from '~/repositories/recurring.repository'
import type { RecurringOccurrenceView, RecurringRuleDetailView } from '~/types/recurring'
import { toUserMessage } from '~/lib/api/errors'
import { formatMoney } from '~/composables/use-money'
import { formatDate, todayLocalIsoDate } from '~/composables/use-date'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()
const { canWrite, canArchive } = useOrganizationPermissions()
const { openConfirm } = useRecurringConfirmation()

const ruleId = computed(() => String(route.params.ruleId || ''))
const detail = ref<RecurringRuleDetailView | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const actionLoading = ref(false)

async function load() {
  const orgId = organization.currentOrganizationId
  if (!orgId || !ruleId.value) {
    error.value = 'No se encontró la regla.'
    loading.value = false
    return
  }
  loading.value = true
  error.value = null
  try {
    detail.value = await createRecurringRepository($api).get(orgId, ruleId.value)
  }
  catch (e) {
    error.value = toUserMessage(e)
    detail.value = null
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(
  () => cache.recurringVersion.value,
  () => {
    void load()
  },
)

const nextOccurrence = computed(() => detail.value?.upcomingOccurrences?.[0] ?? null)

function directionLabel(direction: string) {
  if (direction === 'inflow') return 'Ingreso'
  if (direction === 'transfer') return 'Transferencia'
  return 'Gasto'
}

async function skipOccurrence(occurrence: RecurringOccurrenceView) {
  const orgId = organization.currentOrganizationId
  if (!orgId || !detail.value) return
  actionLoading.value = true
  try {
    await createRecurringRepository($api).createException(orgId, detail.value.id, {
      occurrenceKey: occurrence.occurrenceKey,
      exceptionType: 'skip',
      expectedVersion: detail.value.version,
      reason: 'Omitido desde detalle',
    })
    cache.invalidateRecurring()
    toast.success('Ocurrencia omitida')
    await load()
  }
  catch (e) {
    toast.error(toUserMessage(e))
  }
  finally {
    actionLoading.value = false
  }
}

async function pauseRule() {
  const orgId = organization.currentOrganizationId
  if (!orgId || !detail.value) return
  actionLoading.value = true
  try {
    await createRecurringRepository($api).pause(orgId, detail.value.id, {
      startsOn: todayLocalIsoDate(),
      expectedVersion: detail.value.version,
      reason: 'Pausa manual',
    })
    cache.invalidateRecurring()
    toast.success('Serie pausada')
    await load()
  }
  catch (e) {
    toast.error(toUserMessage(e))
  }
  finally {
    actionLoading.value = false
  }
}

async function resumeRule() {
  const orgId = organization.currentOrganizationId
  if (!orgId || !detail.value) return
  actionLoading.value = true
  try {
    await createRecurringRepository($api).resume(orgId, detail.value.id, {
      resumeOn: todayLocalIsoDate(),
      expectedVersion: detail.value.version,
    })
    cache.invalidateRecurring()
    toast.success('Serie reanudada')
    await load()
  }
  catch (e) {
    toast.error(toUserMessage(e))
  }
  finally {
    actionLoading.value = false
  }
}

async function archiveRule() {
  const orgId = organization.currentOrganizationId
  if (!orgId || !detail.value) return
  actionLoading.value = true
  try {
    await createRecurringRepository($api).archive(orgId, detail.value.id, detail.value.version)
    cache.invalidateRecurring()
    toast.success('Serie archivada')
    await navigateTo('/app/recurring')
  }
  catch (e) {
    toast.error(toUserMessage(e))
  }
  finally {
    actionLoading.value = false
  }
}
</script>

<template>
  <div data-testid="recurring-detail-page">
    <AppPageHeader
      :title="detail?.name || 'Recurrente'"
      description="Serie, próximas ocurrencias y acciones."
      back-to="/app/recurring"
      back-label="← Recurrentes"
    />

    <UiSkeleton v-if="loading" style="height: 10rem" />
    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar">
      {{ error }}
    </UiAlert>

    <template v-else-if="detail">
      <UiAlert
        v-if="detail.isManagedExternally"
        tone="warning"
        title="Administrado externamente"
      >
        Esta serie se gestiona desde otro módulo. Aquí solo puedes consultarla.
      </UiAlert>

      <section class="panel">
        <h2>Próxima ocurrencia</h2>
        <template v-if="nextOccurrence">
          <p>
            {{ formatDate(nextOccurrence.expectedOn) }} ·
            {{ formatMoney(nextOccurrence.expectedAmount, nextOccurrence.currency) }} ·
            {{ nextOccurrence.status }}
          </p>
          <div class="actions">
            <UiButton
              v-if="canWrite && nextOccurrence.canConfirm"
              type="button"
              :disabled="actionLoading"
              @click="openConfirm(nextOccurrence)"
            >
              Registrar movimiento
            </UiButton>
            <UiButton
              v-if="canWrite && nextOccurrence.canSkip"
              type="button"
              variant="secondary"
              :disabled="actionLoading"
              @click="skipOccurrence(nextOccurrence)"
            >
              Omitir esta
            </UiButton>
          </div>
        </template>
        <p v-else class="muted">No hay ocurrencias próximas.</p>
      </section>

      <section class="panel">
        <h2>Datos de la serie</h2>
        <dl class="meta">
          <div><dt>Tipo</dt><dd>{{ directionLabel(detail.direction) }}</dd></div>
          <div><dt>Monto</dt><dd>{{ formatMoney(detail.amount, detail.currency) }}</dd></div>
          <div><dt>Estado</dt><dd>{{ detail.status }}</dd></div>
          <div><dt>Cadencia</dt><dd>{{ detail.currentVersion.frequency }} / {{ detail.currentVersion.interval }}</dd></div>
          <div><dt>Versión</dt><dd>{{ detail.version }}</dd></div>
        </dl>
        <p v-if="detail.notes" class="muted">{{ detail.notes }}</p>
        <div v-if="canWrite && !detail.isManagedExternally" class="actions">
          <UiButton
            v-if="detail.status === 'active'"
            type="button"
            variant="secondary"
            :disabled="actionLoading"
            @click="pauseRule"
          >
            Pausar
          </UiButton>
          <UiButton
            v-if="detail.status === 'paused'"
            type="button"
            variant="secondary"
            :disabled="actionLoading"
            @click="resumeRule"
          >
            Reanudar
          </UiButton>
          <UiButton
            v-if="canArchive"
            type="button"
            variant="danger"
            :disabled="actionLoading"
            @click="archiveRule"
          >
            Archivar
          </UiButton>
        </div>
      </section>

      <section class="panel">
        <h2>Calendario de ocurrencias</h2>
        <ul class="rows">
          <li
            v-for="item in detail.upcomingOccurrences"
            :key="item.occurrenceKey"
            class="row"
          >
            <div>
              <strong>{{ formatDate(item.expectedOn) }}</strong>
              <p class="muted">
                {{ formatMoney(item.expectedAmount, item.currency) }} · {{ item.status }}
              </p>
            </div>
            <div class="actions">
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
                @click="skipOccurrence(item)"
              >
                Omitir
              </UiButton>
            </div>
          </li>
        </ul>
      </section>

      <section class="panel">
        <h2>Versiones</h2>
        <ul class="rows">
          <li v-for="version in detail.versions" :key="version.id" class="row">
            <div>
              <strong>{{ formatMoney(version.amount, version.currency) }}</strong>
              <p class="muted">
                Desde {{ formatDate(version.effectiveFrom) }}
                <template v-if="version.effectiveUntil">
                  · hasta {{ formatDate(version.effectiveUntil) }}
                </template>
              </p>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<style scoped>
.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
}
.meta {
  display: grid;
  gap: var(--space-2);
  grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
}
.meta dt {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.meta dd {
  margin: 0;
  font-weight: 600;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-3);
}
.rows {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}
.row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: center;
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-3);
}
.row:first-child {
  border-top: 0;
  padding-top: 0;
}
.muted {
  color: var(--color-text-muted);
  margin: 0.2rem 0 0;
}
</style>
