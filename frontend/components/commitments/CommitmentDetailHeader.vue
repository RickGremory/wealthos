<script setup lang="ts">
import type { CommitmentDetailView } from '~/types/commitments'
import { getCommitmentPriorityLabel, getCommitmentTypeLabel } from '~/utils/commitment-types'

defineProps<{
  commitment: CommitmentDetailView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  edit: []
  archive: []
  pause: []
  resume: []
  close: []
  pay: []
}>()
</script>

<template>
  <header class="detail-header" data-testid="commitment-detail-header">
    <div class="stack-sm">
      <div class="detail-header__badges">
        <CommitmentStatusBadge
          :status="commitment.status"
          :display-status="commitment.displayStatus"
        />
        <CurrencyBadge :currency="commitment.currency" />
        <UiBadge tone="neutral">
          Prioridad {{ getCommitmentPriorityLabel(commitment.priority) }}
        </UiBadge>
      </div>
      <h1 class="detail-header__title">{{ commitment.name }}</h1>
      <p class="text-muted detail-header__subtitle">
        {{ getCommitmentTypeLabel(commitment.debtType) }}
        <template v-if="commitment.creditor"> · {{ commitment.creditor }}</template>
      </p>
    </div>

    <div class="detail-header__actions">
      <UiButton
        v-if="canWrite && commitment.status === 'active' && Number(commitment.currentBalance) > 0"
        type="button"
        data-testid="commitment-pay-button"
        @click="emit('pay')"
      >
        Registrar pago
      </UiButton>
      <UiButton
        v-if="canWrite && commitment.status === 'active'"
        type="button"
        variant="ghost"
        @click="emit('pause')"
      >
        Pausar
      </UiButton>
      <UiButton
        v-if="canWrite && commitment.status === 'paused'"
        type="button"
        variant="secondary"
        @click="emit('resume')"
      >
        Reanudar
      </UiButton>
      <UiButton
        v-if="canWrite && commitment.status !== 'archived' && commitment.status !== 'closed'"
        type="button"
        variant="secondary"
        @click="emit('edit')"
      >
        Editar
      </UiButton>
      <UiButton
        v-if="canArchive && commitment.status === 'active'"
        type="button"
        variant="ghost"
        @click="emit('close')"
      >
        Cerrar
      </UiButton>
      <UiButton
        v-if="canArchive && commitment.status !== 'archived'"
        type="button"
        variant="ghost"
        @click="emit('archive')"
      >
        Archivar
      </UiButton>
    </div>
  </header>
</template>

<style scoped>
.detail-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.detail-header__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.detail-header__title {
  margin: 0;
  font-size: clamp(1.4rem, 4vw, 1.85rem);
}

.detail-header__subtitle {
  margin: 0;
}

.detail-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: flex-start;
}
</style>
