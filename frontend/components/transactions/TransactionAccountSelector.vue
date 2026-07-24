<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'
import { getAccountCapabilities } from '~/utils/transaction-capabilities'
import type { TransactionType } from '~/types/transactions'

const model = defineModel<string>({ default: '' })

const props = defineProps<{
  accounts: AccountSummary[]
  transactionType: TransactionType
  role?: 'source' | 'destination' | 'primary'
  currency?: string | null
  label?: string
  error?: string
  disabled?: boolean
}>()

const filtered = computed(() => {
  return props.accounts.filter((account) => {
    if (!account.isActive) return false
    if (props.currency && account.currency !== props.currency) return false
    const caps = getAccountCapabilities(account.accountType)
    const role = props.role ?? 'primary'
    if (props.transactionType === 'income') return caps.canReceiveIncome
    if (props.transactionType === 'expense') return caps.canPayExpense
    if (props.transactionType === 'adjustment') return caps.canAdjust
    if (props.transactionType === 'transfer') {
      if (role === 'source') return caps.canTransferFrom
      if (role === 'destination') return caps.canTransferTo
      return caps.canTransferFrom || caps.canTransferTo
    }
    return true
  })
})

const options = computed(() => [
  { label: 'Selecciona una cuenta', value: '' },
  ...filtered.value.map(a => ({
    label: `${a.name} · ${a.currency}`,
    value: a.id,
  })),
])
</script>

<template>
  <UiSelect
    v-model="model"
    :label="label || 'Cuenta'"
    :options="options"
    :disabled="disabled"
    :required="true"
    data-testid="transaction-account-selector"
  />
  <p v-if="error" class="field-error">{{ error }}</p>
</template>

<style scoped>
.field-error {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: var(--color-danger);
}
</style>
