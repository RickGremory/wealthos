<script setup lang="ts">
import type { CommitmentListItemView } from '~/types/commitments'
import { getCommitmentPriorityLabel, getCommitmentTypeLabel } from '~/utils/commitment-types'

defineProps<{
  commitment: CommitmentListItemView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  view: []
  edit: []
  archive: []
}>()
</script>

<template>
  <article
    class="commitment-card"
    :class="{ 'commitment-card--archived': commitment.status === 'archived' }"
    data-testid="commitment-card"
    @click="emit('view')"
  >
    <div class="commitment-card__top">
      <div class="stack-sm">
        <div class="commitment-card__title-row">
          <h3 class="commitment-card__name">{{ commitment.name }}</h3>
          <CommitmentStatusBadge
            :status="commitment.status"
            :display-status="commitment.displayStatus"
          />
        </div>
        <p class="commitment-card__meta text-muted">
          {{ getCommitmentTypeLabel(commitment.debtType) }}
          <template v-if="commitment.creditor"> · {{ commitment.creditor }}</template>
          · Prioridad {{ getCommitmentPriorityLabel(commitment.priority) }}
        </p>
      </div>
      <CurrencyBadge :currency="commitment.currency" />
    </div>

    <div class="commitment-card__balance">
      <span class="text-muted">Saldo</span>
      <strong>
        <MoneyValue
          :amount="commitment.currentBalance"
          :currency="commitment.currency"
          :emphasize-sign="false"
        />
      </strong>
      <span
        v-if="commitment.utilizationPercentage != null"
        class="text-muted commitment-card__util"
      >
        {{ commitment.utilizationPercentage }}% utilización
      </span>
    </div>

    <CommitmentNextAction
      compact
      :action="commitment.nextAction"
      :currency="commitment.currency"
    />

    <footer class="commitment-card__footer">
      <span class="text-muted commitment-card__footer-meta">
        <template v-if="commitment.nextDueDate">
          Próximo pago {{ commitment.nextDueDate }}
        </template>
        <template v-else>Sin fecha de pago</template>
      </span>
      <div class="commitment-card__actions" @click.stop>
        <UiButton
          v-if="canWrite && commitment.status !== 'archived'"
          type="button"
          size="sm"
          variant="ghost"
          @click="emit('edit')"
        >
          Editar
        </UiButton>
        <UiButton
          v-if="canArchive && commitment.status !== 'archived'"
          type="button"
          size="sm"
          variant="ghost"
          @click="emit('archive')"
        >
          Archivar
        </UiButton>
      </div>
    </footer>
  </article>
</template>

<style scoped>
.commitment-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  display: grid;
  gap: var(--space-3);
  min-width: 0;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.commitment-card:hover {
  border-color: var(--color-teal-600);
  box-shadow: var(--shadow-sm);
}

.commitment-card--archived {
  opacity: 0.75;
}

.commitment-card__top {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: flex-start;
  min-width: 0;
}

.commitment-card__top > .stack-sm {
  min-width: 0;
  flex: 1 1 auto;
}

.commitment-card__title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.commitment-card__name {
  margin: 0;
  font-size: 1.05rem;
  overflow-wrap: anywhere;
}

.commitment-card__meta {
  margin: 0;
  font-size: 0.82rem;
}

.commitment-card__balance {
  display: grid;
  gap: 0.15rem;
}

.commitment-card__balance strong {
  font-size: 1.25rem;
  color: var(--color-teal-900);
}

.commitment-card__util {
  font-size: 0.8rem;
}

.commitment-card__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-2);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.commitment-card__footer-meta {
  font-size: 0.8rem;
}

.commitment-card__actions {
  display: flex;
  gap: var(--space-1);
}
</style>
