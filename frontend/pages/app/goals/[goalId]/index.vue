<script setup lang="ts">
import { createGoalsRepository } from '~/repositories/goals.repository'
import type { GoalDetailView } from '~/types/goals'
import { toUserMessage } from '~/lib/api/errors'
import { applyGoalPriorities } from '~/composables/use-goals'
import { compareDecimalStrings } from '~/utils/decimal-string'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const goalId = computed(() => String(route.params.goalId))
const organization = useOrganizationStore()
const preferences = usePreferencesStore()
const { canWrite, canArchive } = useOrganizationPermissions()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()

const goal = ref<GoalDetailView | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)

const manualAmount = ref('')
const manualSubmitting = ref(false)
const manualError = ref<string | null>(null)

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
    const repo = createGoalsRepository($api)
    const raw = await repo.get(orgId, goalId.value)
    const [withPriority] = applyGoalPriorities(
      [raw],
      id => preferences.getGoalPriority(id),
    )
    goal.value = withPriority ?? raw
    manualAmount.value = goal.value.currentAmount
  }
  catch (e) {
    error.value = toUserMessage(e)
    goal.value = null
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(goalId, () => {
  void load()
})

async function confirmArchive() {
  if (!goal.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  archiveLoading.value = true
  try {
    const repo = createGoalsRepository($api)
    await repo.archive(orgId, goal.value.id)
    cache.invalidateGoals()
    toast.success('Meta archivada')
    archiveOpen.value = false
    await navigateTo('/app/goals')
  }
  catch (e) {
    toast.error('No se pudo archivar', toUserMessage(e))
  }
  finally {
    archiveLoading.value = false
  }
}

async function submitManualProgress() {
  if (!goal.value || goal.value.strategy !== 'manual') return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  const amount = manualAmount.value.trim().replace(/,/g, '')
  if (!/^\d+(\.\d{1,2})?$/.test(amount) || compareDecimalStrings(amount, '0') < 0) {
    manualError.value = 'Ingresa un monto válido.'
    return
  }

  manualSubmitting.value = true
  manualError.value = null
  try {
    const repo = createGoalsRepository($api)
    const updated = await repo.updateManualProgress(orgId, goal.value.id, amount)
    const [withPriority] = applyGoalPriorities(
      [updated],
      id => preferences.getGoalPriority(id),
    )
    goal.value = withPriority ?? updated
    cache.invalidateGoals()
    toast.success('Progreso actualizado')
  }
  catch (e) {
    manualError.value = toUserMessage(e)
  }
  finally {
    manualSubmitting.value = false
  }
}
</script>

<template>
  <div data-testid="goal-detail-page">
    <div v-if="loading" class="stack">
      <UiSkeleton height="6rem" />
      <UiSkeleton height="10rem" />
    </div>

    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar la meta">
      <p>{{ error }}</p>
      <div class="cluster" style="margin-top: 0.75rem">
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/goals')">
          Volver a metas
        </UiButton>
      </div>
    </UiAlert>

    <template v-else-if="goal">
      <GoalDetailHeader
        :goal="goal"
        :can-write="canWrite"
        :can-archive="canArchive"
        @edit="navigateTo(`/app/goals/${goal.id}/edit`)"
        @archive="archiveOpen = true"
      />

      <div class="detail-grid">
        <UiCard title="Progreso">
          <GoalProgressBar
            :completion-percentage="goal.completionPercentage"
            :remaining-amount="goal.remainingAmount"
            :currency="goal.currency"
            :current-amount="goal.currentAmount"
            :target-amount="goal.targetAmount"
          />
        </UiCard>

        <UiCard title="Resumen">
          <dl class="info-list">
            <div>
              <dt>Actual</dt>
              <dd>
                <MoneyValue
                  :amount="goal.currentAmount"
                  :currency="goal.currency"
                  :emphasize-sign="false"
                />
              </dd>
            </div>
            <div>
              <dt>Objetivo</dt>
              <dd>
                <MoneyValue
                  :amount="goal.targetAmount"
                  :currency="goal.currency"
                  :emphasize-sign="false"
                />
              </dd>
            </div>
            <div>
              <dt>Restante</dt>
              <dd>
                <MoneyValue
                  :amount="goal.remainingAmount"
                  :currency="goal.currency"
                  :emphasize-sign="false"
                />
              </dd>
            </div>
            <div v-if="goal.estimatedCompletionDate">
              <dt>Estimación de cierre</dt>
              <dd>{{ goal.estimatedCompletionDate }}</dd>
            </div>
          </dl>
        </UiCard>

        <UiCard
          v-if="goal.strategy === 'manual' && canWrite && goal.status === 'active'"
          title="Actualizar progreso"
        >
          <form class="stack" data-testid="goal-manual-progress" @submit.prevent="submitManualProgress">
            <UiAlert v-if="manualError" tone="danger" title="No se pudo actualizar">
              {{ manualError }}
            </UiAlert>
            <MoneyInput
              v-model="manualAmount"
              label="Monto actual"
              :currency="goal.currency"
              :disabled="manualSubmitting"
            />
            <div class="cluster" style="justify-content: flex-end">
              <UiButton type="submit" :loading="manualSubmitting">
                Guardar progreso
              </UiButton>
            </div>
          </form>
        </UiCard>

        <UiCard title="Historial">
          <GoalHistory :goal="goal" />
        </UiCard>
      </div>

      <GoalArchiveDialog
        v-model:open="archiveOpen"
        :goal="goal"
        :loading="archiveLoading"
        @confirm="confirmArchive"
      />
    </template>
  </div>
</template>

<style scoped>
.detail-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 900px) {
  .detail-grid {
    grid-template-columns: 1.2fr 1fr;
  }
}

.info-list {
  margin: 0;
  display: grid;
  gap: var(--space-3);
}

.info-list dt {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.info-list dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
}
</style>
