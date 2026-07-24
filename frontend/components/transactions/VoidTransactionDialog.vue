<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: [reason: string]
}>()

const reason = ref('')
const localError = ref<string | null>(null)

watch(open, (v) => {
  if (v) {
    reason.value = ''
    localError.value = null
  }
})

function onConfirm() {
  if (reason.value.trim().length < 2) {
    localError.value = 'Indica el motivo de la anulación (mínimo 2 caracteres).'
    return
  }
  emit('confirm', reason.value.trim())
}
</script>

<template>
  <UiModal v-model:open="open" title="Anular transacción">
    <div class="stack">
      <p>
        La anulación no borra el historial: marca el movimiento como anulado y revierte
        su efecto en los saldos.
      </p>
      <UiInput
        v-model="reason"
        label="Motivo"
        placeholder="Ej. Duplicado por error"
        :error="localError || undefined"
        required
        data-testid="void-reason-input"
      />
    </div>
    <template #footer>
      <UiButton type="button" variant="ghost" :disabled="loading" @click="open = false">
        Cancelar
      </UiButton>
      <UiButton
        type="button"
        variant="danger"
        :loading="loading"
        data-testid="void-confirm-button"
        @click="onConfirm"
      >
        Anular
      </UiButton>
    </template>
  </UiModal>
</template>
