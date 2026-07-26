<script setup lang="ts">
import type { PlanningAlert } from '~/types/planning'

defineProps<{
  alerts: PlanningAlert[]
}>()

const { format } = useMoney()

const ALERT_COPY: Record<string, string> = {
  projected_deficit: 'Hay un déficit de efectivo proyectado en el horizonte.',
  reserve_shortfall: 'El saldo mínimo queda por debajo de tu reserva de seguridad.',
  safety_reserve_not_configured: 'Todavía no configuraste una reserva de seguridad.',
  low_projection_confidence: 'La proyección tiene baja confianza por datos incompletos.',
  no_eligible_accounts: 'No hay cuentas líquidas elegibles para calcular Disponible.',
  source_unavailable: 'Una fuente de datos no está disponible.',
  source_partial: 'Una fuente de datos está parcial.',
  tax_reservation_incomplete: 'La proyección fiscal usa solo reservas registradas.',
  stale_account_balance: 'Algunos saldos de cuenta pueden estar desactualizados.',
  possible_duplicate_cash_flow: 'Hay posibles movimientos duplicados; no se eliminaron automáticamente.',
}

function message(alert: PlanningAlert): string {
  return ALERT_COPY[alert.code] || alert.messageKey
}
</script>

<template>
  <section v-if="alerts.length" class="alerts" aria-label="Alertas de planeación">
    <h2>Alertas</h2>
    <ul>
      <li
        v-for="(alert, index) in alerts"
        :key="`${alert.code}-${index}`"
        :data-severity="alert.severity"
      >
        <strong>{{ message(alert) }}</strong>
        <span v-if="alert.amount && alert.currency" class="text-muted">
          {{ format(alert.amount, alert.currency) }}
        </span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.alerts h2 {
  margin: 0 0 0.6rem;
  font-size: 1.05rem;
}
.alerts ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}
.alerts li {
  padding: 0.7rem 0.85rem;
  border-radius: 0.5rem;
  border-left: 3px solid var(--color-warning, #b54708);
  background: color-mix(in srgb, var(--color-warning, #b54708) 8%, transparent);
  display: grid;
  gap: 0.2rem;
}
.alerts li[data-severity='critical'] {
  border-left-color: var(--color-danger, #b42318);
  background: color-mix(in srgb, var(--color-danger, #b42318) 8%, transparent);
}
.alerts li[data-severity='info'] {
  border-left-color: var(--color-info, #175cd3);
  background: color-mix(in srgb, var(--color-info, #175cd3) 8%, transparent);
}
</style>
