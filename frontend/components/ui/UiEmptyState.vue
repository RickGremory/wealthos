<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="ui-empty">
    <h3 class="ui-empty__title">{{ title }}</h3>
    <p v-if="description" class="ui-empty__desc text-muted">{{ description }}</p>
    <div v-if="$slots.actions" class="ui-empty__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.ui-empty {
  text-align: center;
  padding: var(--space-10) var(--space-4);
}

.ui-empty__title {
  font-size: 1.1rem;
  margin: 0 0 var(--space-2);
}

.ui-empty__desc {
  margin: 0 auto;
  max-width: 28rem;
}

.ui-empty__actions {
  margin-top: var(--space-5);
}
</style>
