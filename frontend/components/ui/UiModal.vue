<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

defineProps<{
  title?: string
}>()

function close() {
  open.value = false
}

watch(open, (isOpen) => {
  if (!import.meta.client) return
  document.body.style.overflow = isOpen ? 'hidden' : ''
}, { immediate: true })

onBeforeUnmount(() => {
  if (!import.meta.client) return
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="ui-modal"
      role="dialog"
      aria-modal="true"
      @click.self="close"
    >
      <div class="ui-modal__panel">
        <header class="ui-modal__header">
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
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-4);
  padding-bottom: calc(var(--space-4) + env(safe-area-inset-bottom, 0px));
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.ui-modal__panel {
  width: min(100%, 28rem);
  max-height: min(92dvh, 100%);
  margin-block: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  padding: var(--space-5);
  overflow: hidden;
}

.ui-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  flex-shrink: 0;
}

.ui-modal__title {
  font-size: 1.15rem;
  margin: 0;
}

.ui-modal__body {
  margin-top: var(--space-4);
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.ui-modal__footer {
  margin-top: var(--space-5);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .ui-modal {
    padding: var(--space-3);
    padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom, 0px));
    align-items: stretch;
  }

  .ui-modal__panel {
    width: 100%;
    max-height: calc(100dvh - 1.5rem - env(safe-area-inset-bottom, 0px));
    margin-block: 0;
    border-radius: var(--radius-lg);
    padding: var(--space-4);
  }
}
</style>
