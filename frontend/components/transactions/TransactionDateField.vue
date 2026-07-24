<script setup lang="ts">
import { todayDateInputValue } from '~/utils/transaction-payload'

const model = defineModel<string>({ default: '' })

defineProps<{
  label?: string
  error?: string
  disabled?: boolean
}>()

onMounted(() => {
  if (!model.value) {
    model.value = todayDateInputValue()
  }
})
</script>

<template>
  <UiInput
    v-model="model"
    type="date"
    :label="label || 'Fecha'"
    :error="error"
    :disabled="disabled"
    required
    data-testid="transaction-date-field"
  />
</template>
