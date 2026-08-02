<script setup lang="ts">
import type { TimelineEventView, TimelineSourceType } from '~/types/timeline'
import { timelineResourcePath } from '~/composables/use-timeline'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { formatDate } = useDate()
const {
  groupedByDay,
  loading,
  loadingMore,
  error,
  sourceFilter,
  nextCursor,
  load,
  loadMore,
} = useTimeline()

const sourceOptions: Array<{ value: '' | TimelineSourceType, label: string }> = [
  { value: '', label: 'Todo' },
  { value: 'transaction', label: 'Movimientos' },
  { value: 'commitment', label: 'Obligaciones' },
  { value: 'recurring', label: 'Recurrentes' },
  { value: 'goal', label: 'Metas' },
]

onMounted(() => {
  void load()
})

watch(sourceFilter, () => {
  void load()
})

function sourceLabel(event: TimelineEventView): string {
  const map: Record<string, string> = {
    transaction: 'Movimiento',
    goal: 'Meta',
    commitment: 'Obligación',
    recurring: 'Recurrente',
    planning: 'Planeación',
    tax: 'Impuestos',
    system: 'Sistema',
  }
  return map[event.sourceType] || event.sourceType
}

function go(event: TimelineEventView) {
  const path = timelineResourcePath(event)
  if (path) return navigateTo(path)
}
</script>

<template>
  <div class="timeline-page stack">
    <header class="timeline-page__header">
      <div>
        <h1>Historia</h1>
        <p class="text-muted">
          ¿Qué ha pasado en tu vida financiera?
        </p>
      </div>
      <div class="timeline-page__filters">
        <label class="filter">
          <span class="text-muted">Origen</span>
          <select v-model="sourceFilter">
            <option
              v-for="opt in sourceOptions"
              :key="String(opt.value)"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>
        </label>
      </div>
    </header>

    <p v-if="error" class="timeline-page__error">
      {{ error }}
    </p>

    <div v-if="loading" class="stack">
      <UiSkeleton v-for="i in 5" :key="i" height="3.5rem" />
    </div>

    <UiEmptyState
      v-else-if="!groupedByDay.length"
      title="Aún no hay historia"
      description="Cuando registres movimientos, metas u obligaciones significativas, aparecerán aquí."
    />

    <div v-else class="timeline-feed stack">
      <section
        v-for="group in groupedByDay"
        :key="group.day"
        class="timeline-day"
      >
        <h2 class="timeline-day__title">
          {{ formatDate(group.day) }}
        </h2>
        <ul class="timeline-day__list">
          <li
            v-for="event in group.events"
            :key="event.id"
            class="timeline-event"
            :data-source="event.sourceType"
            :data-importance="event.importance"
            role="button"
            tabindex="0"
            @click="go(event)"
            @keydown.enter="go(event)"
          >
            <div class="timeline-event__badge" aria-hidden="true">
              {{ sourceLabel(event).slice(0, 1) }}
            </div>
            <div class="timeline-event__body">
              <p class="timeline-event__title">
                {{ event.title }}
              </p>
              <p class="timeline-event__desc text-muted">
                {{ event.description }}
              </p>
              <p class="timeline-event__meta text-muted">
                <span>{{ sourceLabel(event) }}</span>
                <span>·</span>
                <span>{{ event.importance }}</span>
              </p>
            </div>
            <p
              v-if="event.amount != null && event.currency"
              class="timeline-event__amount"
            >
              <MoneyValue :amount="event.amount" :currency="event.currency" />
            </p>
          </li>
        </ul>
      </section>

      <div v-if="nextCursor" class="timeline-page__more">
        <UiButton
          type="button"
          variant="secondary"
          :disabled="loadingMore"
          @click="loadMore"
        >
          {{ loadingMore ? 'Cargando…' : 'Cargar más' }}
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-page__header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: flex-end;
}

.timeline-page__header h1 {
  margin: 0 0 var(--space-1);
}

.timeline-page__header p {
  margin: 0;
}

.timeline-page__filters {
  display: flex;
  gap: var(--space-3);
}

.filter {
  display: grid;
  gap: 0.25rem;
  font-size: 0.85rem;
}

.filter select {
  min-width: 10rem;
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
}

.timeline-page__error {
  color: var(--color-danger, #b42318);
}

.timeline-day__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.timeline-day__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.timeline-event {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-3);
  align-items: start;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
}

.timeline-event:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.timeline-event__badge {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 0.85rem;
  background: color-mix(in srgb, var(--color-primary) 14%, transparent);
  color: var(--color-primary);
}

.timeline-event[data-source='commitment'] .timeline-event__badge {
  background: color-mix(in srgb, #b54708 16%, transparent);
  color: #b54708;
}

.timeline-event[data-source='goal'] .timeline-event__badge {
  background: color-mix(in srgb, #027a48 16%, transparent);
  color: #027a48;
}

.timeline-event__title {
  margin: 0;
  font-weight: 650;
}

.timeline-event__desc,
.timeline-event__meta {
  margin: 0.15rem 0 0;
  font-size: 0.85rem;
}

.timeline-event__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.timeline-event__amount {
  margin: 0;
  font-family: var(--font-display);
  white-space: nowrap;
}

.timeline-page__more {
  display: flex;
  justify-content: center;
  padding: var(--space-4) 0;
}
</style>
