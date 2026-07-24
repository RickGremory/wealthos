<script setup lang="ts">
import type { GoalListItemView } from '~/types/goals'

const open = defineModel<boolean>('open', { default: false })

defineProps<{
  goal: GoalListItemView | null
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()
</script>

<template>
  <UiModal v-model:open="open" title="Archivar meta">
    <div v-if="goal" class="stack" data-testid="goal-archive-dialog">
      <p>
        La meta <strong>{{ goal.name }}</strong> dejará de aparecer entre las activas.
        El historial permanecerá disponible.
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
        data-testid="goal-archive-confirm"
        @click="emit('confirm')"
      >
        Archivar
      </UiButton>
    </template>
  </UiModal>
</template>
