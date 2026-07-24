<script setup lang="ts">
import type { TransactionStatus } from '~/types/transactions'
import { presentTransactionStatus } from '~/utils/transaction-presentation'

const props = defineProps<{
  status: TransactionStatus | string
}>()

const label = computed(() => presentTransactionStatus(props.status))
const tone = computed(() => (props.status === 'voided' ? 'danger' : 'success'))
</script>

<template>
  <UiBadge :tone="tone">{{ label }}</UiBadge>
</template>
