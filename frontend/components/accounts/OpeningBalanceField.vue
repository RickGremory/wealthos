<script setup lang="ts">
defineProps<{
  label: string
  hint?: string
  error?: string
  disabled?: boolean
}>()

const model = defineModel<string>({ default: '0.00' })
</script>

<template>
  <div class="opening-balance stack-sm">
    <UiInput
      v-model="model"
      :label="label"
      inputmode="decimal"
      placeholder="0.00"
      :disabled="disabled"
      :error="error"
      required
    />
    <p v-if="hint" class="opening-balance__hint text-muted">
      {{ hint }}
    </p>
  </div>
</template>

<style scoped>
.opening-balance__hint {
  margin: 0;
  font-size: 0.8rem;
}
</style>
