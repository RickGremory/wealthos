<script setup lang="ts">
import type { CommitmentDisplayStatus, CommitmentStatus } from '~/types/commitments'
import { getCommitmentDisplayMeta } from '~/utils/commitment-status'

const props = defineProps<{
  status: CommitmentStatus
  displayStatus?: CommitmentDisplayStatus | string | null
}>()

const meta = computed(() =>
  getCommitmentDisplayMeta(props.displayStatus, props.status),
)
</script>

<template>
  <UiBadge
    :tone="meta.tone"
    data-testid="commitment-status-badge"
    :title="meta.hint"
  >
    {{ meta.label }}
  </UiBadge>
</template>
