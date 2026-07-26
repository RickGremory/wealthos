<script setup lang="ts">
const open = defineModel<boolean>('open', { default: false })

defineProps<{
  title?: string
}>()

const panelRef = ref<HTMLElement | null>(null)
let previouslyFocused: HTMLElement | null = null

function close() {
  open.value = false
}

function focusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(
    root.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
    ),
  ).filter(el => !el.hasAttribute('disabled') && el.tabIndex !== -1)
}

function onKeydown(event: KeyboardEvent) {
  if (!open.value || !panelRef.value) return

  if (event.key === 'Escape') {
    event.preventDefault()
    close()
    return
  }

  if (event.key !== 'Tab') return

  const nodes = focusableElements(panelRef.value)
  if (!nodes.length) {
    event.preventDefault()
    panelRef.value.focus()
    return
  }

  const first = nodes[0]!
  const last = nodes[nodes.length - 1]!
  const active = document.activeElement as HTMLElement | null

  if (event.shiftKey && (active === first || active === panelRef.value)) {
    event.preventDefault()
    last.focus()
  }
  else if (!event.shiftKey && active === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(open, async (isOpen) => {
  if (!import.meta.client) return
  document.body.style.overflow = isOpen ? 'hidden' : ''

  if (isOpen) {
    previouslyFocused = document.activeElement as HTMLElement | null
    await nextTick()
    const nodes = panelRef.value ? focusableElements(panelRef.value) : []
    ;(nodes[0] || panelRef.value)?.focus()
  }
  else if (previouslyFocused) {
    previouslyFocused.focus()
    previouslyFocused = null
  }
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
      :aria-label="title || 'Diálogo'"
      @click.self="close"
      @keydown="onKeydown"
    >
      <div
        ref="panelRef"
        class="ui-modal__panel"
        tabindex="-1"
      >
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
  outline: none;
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
