<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

defineProps<{
  title?: string
}>()

function close() {
  open.value = false
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="ui-modal" role="dialog" aria-modal="true" @click.self="close">
      <div class="ui-modal__panel">
        <header class="ui-modal__header cluster" style="justify-content: space-between">
          <h2 v-if="title" class="ui-modal__title">{{ title }}</h2>
          <UiButton variant="ghost" size="sm" type="button" @click="close">
            Cerrar
          </UiButton>
        </header>
        <div class="ui-modal__body">
          <slot />
        </div>
        <footer v-if="$slots.footer" class="ui-modal__footer">
          <slot name="footer" />
        </footer>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.ui-modal {
  position: fixed;
  inset: 0;
  z-index: 80;
  background: rgba(10, 22, 40, 0.5);
  display: grid;
  place-items: center;
  padding: var(--space-4);
}

.ui-modal__panel {
  width: min(100%, 28rem);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: var(--space-5);
}

.ui-modal__title {
  font-size: 1.15rem;
  margin: 0;
}

.ui-modal__body {
  margin-top: var(--space-4);
}

.ui-modal__footer {
  margin-top: var(--space-5);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
</style>
