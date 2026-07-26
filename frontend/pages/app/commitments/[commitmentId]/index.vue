<script setup lang="ts">
import { createCommitmentsRepository } from '~/repositories/commitments.repository'
import type { CommitmentDetailView } from '~/types/commitments'
import { toUserMessage } from '~/lib/api/errors'
import { getCommitmentTypeLabel } from '~/utils/commitment-types'
import { formatDate } from '~/composables/use-date'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const commitmentId = computed(() => String(route.params.commitmentId))
const organization = useOrganizationStore()
const { canWrite, canArchive } = useOrganizationPermissions()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()

const commitment = ref<CommitmentDetailView | null>(null)
const activity = ref<Array<Record<string, unknown>>>([])
const loading = ref(true)
const error = ref<string | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)
const actionLoading = ref(false)

async function load() {
  const orgId = organization.currentOrganizationId
  if (!orgId) {
    error.value = 'Selecciona una organización.'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null
  try {
    const repo = createCommitmentsRepository($api)
    commitment.value = await repo.get(orgId, commitmentId.value)
    const act = await repo.activity(orgId, commitmentId.value, { limit: 20 })
    activity.value = act.items ?? []
  }
  catch (e) {
    error.value = toUserMessage(e)
    commitment.value = null
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(commitmentId, () => {
  void load()
})

async function runAction(kind: 'pause' | 'resume' | 'close' | 'archive') {
  if (!commitment.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  actionLoading.value = true
  try {
    const repo = createCommitmentsRepository($api)
    if (kind === 'pause') await repo.pause(orgId, commitment.value.id)
    if (kind === 'resume') await repo.resume(orgId, commitment.value.id)
    if (kind === 'close') await repo.close(orgId, commitment.value.id)
    if (kind === 'archive') {
      await repo.archive(orgId, commitment.value.id)
      cache.invalidateCommitments()
      toast.success('Obligación archivada')
      archiveOpen.value = false
      await navigateTo('/app/commitments')
      return
    }
    cache.invalidateCommitments()
    toast.success('Actualizado')
    await load()
  }
  catch (e) {
    toast.error('No se pudo completar', toUserMessage(e))
  }
  finally {
    actionLoading.value = false
    archiveLoading.value = false
  }
}
</script>

<template>
  <div data-testid="commitment-detail-page">
    <div v-if="loading" class="stack">
      <UiSkeleton height="6rem" />
      <UiSkeleton height="10rem" />
    </div>

    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar la obligación">
      <p>{{ error }}</p>
      <div class="cluster" style="margin-top: 0.75rem">
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/commitments')">
          Volver a obligaciones
        </UiButton>
      </div>
    </UiAlert>

    <template v-else-if="commitment">
      <p class="back-link">
        <NuxtLink to="/app/commitments">← Todas las obligaciones</NuxtLink>
      </p>

      <CommitmentDetailHeader
        :commitment="commitment"
        :can-write="canWrite && !actionLoading"
        :can-archive="canArchive && !actionLoading"
        @edit="navigateTo(`/app/commitments/${commitment.id}/edit`)"
        @archive="archiveOpen = true"
        @pause="runAction('pause')"
        @resume="runAction('resume')"
        @close="runAction('close')"
      />

      <div class="detail-grid">
        <UiCard title="¿Qué debo hacer ahora?">
          <CommitmentNextAction
            :action="commitment.nextAction"
            :currency="commitment.currency"
          />
        </UiCard>

        <UiCard title="Saldo">
          <dl class="info-list">
            <div>
              <dt>Adeudo actual</dt>
              <dd>
                <MoneyValue
                  :amount="commitment.currentBalance"
                  :currency="commitment.currency"
                  :emphasize-sign="false"
                />
              </dd>
            </div>
            <div v-if="commitment.utilizationPercentage != null">
              <dt>Utilización</dt>
              <dd>{{ commitment.utilizationPercentage }}%</dd>
            </div>
            <div v-if="commitment.minimumPayment">
              <dt>Pago mínimo</dt>
              <dd>
                <MoneyValue
                  :amount="commitment.minimumPayment"
                  :currency="commitment.currency"
                  :emphasize-sign="false"
                />
              </dd>
            </div>
            <div v-if="commitment.interestRate">
              <dt>Tasa anual</dt>
              <dd>{{ commitment.interestRate }}%</dd>
            </div>
            <div v-if="commitment.nextDueDate">
              <dt>Próximo pago</dt>
              <dd>{{ commitment.nextDueDate }}</dd>
            </div>
            <div>
              <dt>Tipo</dt>
              <dd>{{ getCommitmentTypeLabel(commitment.debtType) }}</dd>
            </div>
          </dl>
        </UiCard>

        <UiCard title="Actividad">
          <ul v-if="activity.length" class="activity-list">
            <li v-for="tx in activity" :key="String(tx.id)" class="activity-item">
              <div>
                <strong>{{ String(tx.description ?? tx.transaction_type ?? 'Movimiento') }}</strong>
                <p class="text-muted">
                  {{ tx.occurred_at ? formatDate(String(tx.occurred_at).slice(0, 10)) : '—' }}
                  · {{ String(tx.transaction_type ?? '') }}
                </p>
              </div>
              <MoneyValue
                v-if="tx.amount != null"
                :amount="String(tx.amount)"
                :currency="commitment.currency"
                :emphasize-sign="false"
              />
            </li>
          </ul>
          <UiEmptyState
            v-else
            title="Sin actividad"
            description="Los pagos y movimientos de la cuenta vinculada aparecerán aquí."
          />
        </UiCard>
      </div>

      <CommitmentArchiveDialog
        v-model:open="archiveOpen"
        :commitment="commitment"
        :loading="archiveLoading"
        @confirm="() => { archiveLoading = true; runAction('archive') }"
      />
    </template>
  </div>
</template>

<style scoped>
.back-link {
  margin: 0 0 var(--space-4);
}

.back-link a {
  color: var(--color-teal-800);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}

.detail-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 900px) {
  .detail-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .detail-grid > :last-child {
    grid-column: 1 / -1;
  }
}

.info-list {
  margin: 0;
  display: grid;
  gap: var(--space-3);
}

.info-list dt {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.info-list dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
}

.activity-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.activity-item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.activity-item p {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
}
</style>
