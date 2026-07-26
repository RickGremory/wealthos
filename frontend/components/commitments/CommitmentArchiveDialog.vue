<script setup lang="ts">
import type { CommitmentListItemView } from '~/types/commitments'

const open = defineModel<boolean>('open', { default: false })

defineProps<{
  commitment: CommitmentListItemView | null
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()
</script>

<template>
  <UiModal v-model:open="open" title="Archivar obligación">
    <div v-if="commitment" class="stack" data-testid="commitment-archive-dialog">
      <p>
        <strong>{{ commitment.name }}</strong> dejará de aparecer en el listado activo.
        El historial y la cuenta vinculada permanecerán.
      </p>
    </div>
    <template #footer>
      <UiButton type="button" variant="ghost" :disabled="loading" @click="open = false">
        Cancelar
      </UiButton>
      <UiButton
        type="button"
        variant="danger"
        :loading="loading"
        data-testid="commitment-archive-confirm"
        @click="emit('confirm')"
      >
        Archivar
      </UiButton>
    </template>
  </UiModal>
</template>
