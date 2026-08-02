<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'

const sourceId = defineModel<string>('sourceId', { default: '' })
const destinationId = defineModel<string>('destinationId', { default: '' })

defineProps<{
  accounts: AccountSummary[]
  sourceError?: string
  destinationError?: string
  currencyMismatch?: boolean
  fxConversion?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  enableFx: []
  disableFx: []
}>()
</script>

<template>
  <div class="transfer-accounts stack" data-testid="transfer-account-selector">
    <TransactionAccountSelector
      v-model="sourceId"
      :accounts="accounts"
      transaction-type="transfer"
      role="source"
      label="Cuenta origen"
      :error="sourceError"
      :disabled="disabled"
    />
    <TransactionAccountSelector
      v-model="destinationId"
      :accounts="accounts"
      transaction-type="transfer"
      role="destination"
      label="Cuenta destino"
      :error="destinationError"
      :disabled="disabled"
    />
    <UiAlert
      v-if="currencyMismatch && !fxConversion"
      tone="warning"
      title="Las cuentas usan monedas diferentes"
    >
      <p class="transfer-accounts__hint">
        Una transferencia normal asume el mismo monto en ambas monedas.
        Para este caso registra una conversión con monto enviado y recibido.
      </p>
      <UiButton
        type="button"
        variant="secondary"
        size="sm"
        data-testid="enable-fx-conversion"
        :disabled="disabled"
        @click="emit('enableFx')"
      >
        Registrar conversión
      </UiButton>
    </UiAlert>
    <UiAlert
      v-else-if="currencyMismatch && fxConversion"
      tone="info"
      title="Transferencia con conversión"
    >
      <p class="transfer-accounts__hint">
        Captura el monto enviado y el monto realmente acreditado.
        El tipo de cambio efectivo se calcula con esos importes.
      </p>
      <UiButton
        type="button"
        variant="ghost"
        size="sm"
        data-testid="disable-fx-conversion"
        :disabled="disabled"
        @click="emit('disableFx')"
      >
        Cancelar conversión
      </UiButton>
    </UiAlert>
  </div>
</template>

<style scoped>
.transfer-accounts__hint {
  margin: 0 0 var(--space-3);
  font-size: 0.9rem;
}
</style>
