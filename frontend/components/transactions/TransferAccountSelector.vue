<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'

const sourceId = defineModel<string>('sourceId', { default: '' })
const destinationId = defineModel<string>('destinationId', { default: '' })

defineProps<{
  accounts: AccountSummary[]
  sourceError?: string
  destinationError?: string
  currencyMismatch?: boolean
  disabled?: boolean
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
    <UiAlert v-if="currencyMismatch" tone="warning" title="Monedas distintas">
      Solo puedes transferir entre cuentas con la misma moneda.
    </UiAlert>
  </div>
</template>
