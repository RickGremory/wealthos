<script setup lang="ts">
import { createCommitmentsRepository } from '~/repositories/commitments.repository'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const organization = useOrganizationStore()
const { $api } = useNuxtApp()
const cache = useFinanceCache()

const loading = ref(true)
const error = ref<string | null>(null)
const events = ref<Array<{
  id: string
  commitmentId: string
  name: string
  eventType: string
  eventDate: string
  severity: string
  currency: string
  amount: string | null
}>>([])

const eventTypeLabel: Record<string, string> = {
  payment_due: 'Pago',
  statement_date: 'Corte',
  maturity_date: 'Vencimiento',
  review_date: 'Revisión',
}

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
    const today = new Date()
    const from = today.toISOString().slice(0, 10)
    const toDate = new Date(today)
    toDate.setDate(toDate.getDate() + 60)
    const to = toDate.toISOString().slice(0, 10)
    const repo = createCommitmentsRepository($api)
    const result = await repo.calendarEvents(orgId, { dateFrom: from, dateTo: to })
    events.value = result
  }
  catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo cargar el calendario.'
    events.value = []
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(
  () => cache.commitmentsVersion.value,
  () => {
    void load()
  },
)

watch(
  () => cache.calendarVersion.value,
  () => {
    void load()
  },
)

const grouped = computed(() => {
  const map = new Map<string, typeof events.value>()
  for (const event of events.value) {
    const list = map.get(event.eventDate) ?? []
    list.push(event)
    map.set(event.eventDate, list)
  }
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]))
})
</script>

<template>
  <div data-testid="calendar-page">
    <AppPageHeader
      title="Calendario"
      description="Pagos, cortes y vencimientos de tus obligaciones."
    >
      <template #actions>
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/commitments')">
          Ver obligaciones
        </UiButton>
      </template>
    </AppPageHeader>

    <div v-if="loading" class="stack">
      <UiSkeleton height="4rem" />
      <UiSkeleton height="8rem" />
    </div>
    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar">
      {{ error }}
    </UiAlert>
    <UiCard v-else-if="!events.length">
      <UiEmptyState
        title="Sin eventos próximos"
        description="Cuando registres obligaciones con día de pago o corte, aparecerán aquí."
      >
        <template #actions>
          <UiButton type="button" @click="navigateTo('/app/commitments/new')">
            Nueva obligación
          </UiButton>
        </template>
      </UiEmptyState>
    </UiCard>
    <div v-else class="calendar-groups">
      <section
        v-for="[day, dayEvents] in grouped"
        :key="day"
        class="calendar-day"
      >
        <h2 class="calendar-day__title">{{ day }}</h2>
        <ul class="calendar-day__list">
          <li
            v-for="event in dayEvents"
            :key="event.id"
            class="calendar-event"
            :data-severity="event.severity"
          >
            <div>
              <UiBadge
                :tone="event.severity === 'overdue'
                  ? 'danger'
                  : event.severity === 'attention'
                    ? 'warning'
                    : 'neutral'"
              >
                {{ eventTypeLabel[event.eventType] || event.eventType }}
              </UiBadge>
              <button
                type="button"
                class="calendar-event__name"
                @click="navigateTo(`/app/commitments/${event.commitmentId}`)"
              >
                {{ event.name }}
              </button>
            </div>
            <MoneyValue
              v-if="event.amount"
              :amount="event.amount"
              :currency="event.currency"
              :emphasize-sign="false"
            />
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.calendar-groups {
  display: grid;
  gap: var(--space-5);
}

.calendar-day__title {
  margin: 0 0 var(--space-3);
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.calendar-day__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.calendar-event {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.calendar-event[data-severity='overdue'] {
  border-color: color-mix(in srgb, var(--color-danger, #b42318) 40%, var(--color-border));
}

.calendar-event__name {
  display: block;
  margin-top: var(--space-2);
  border: 0;
  background: transparent;
  color: var(--color-teal-900);
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  padding: 0;
  text-align: left;
}

.calendar-event__name:hover {
  text-decoration: underline;
}
</style>
