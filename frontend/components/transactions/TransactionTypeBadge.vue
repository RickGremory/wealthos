<script setup lang="ts">
import type { TransactionType } from '~/types/transactions'
import { presentTransactionType } from '~/utils/transaction-presentation'

const props = defineProps<{
  type: TransactionType | string
}>()

const label = computed(() => presentTransactionType(props.type))
const tone = computed(() => {
  if (props.type === 'income') return 'success'
  if (props.type === 'expense') return 'warning'
  if (props.type === 'transfer') return 'teal'
  return 'neutral'
})
</script>

<template>
  <UiBadge :tone="tone">{{ label }}</UiBadge>
</template>
