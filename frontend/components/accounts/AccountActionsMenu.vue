<script setup lang="ts">
import type { AccountListItemView } from '~/types/accounts'

defineProps<{
  account: AccountListItemView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  view: []
  edit: []
  archive: []
}>()

const open = ref(false)

function goView() {
  open.value = false
  emit('view')
}

function goEdit() {
  open.value = false
  emit('edit')
}

function goArchive() {
  open.value = false
  emit('archive')
}
</script>

<template>
  <div class="actions-menu" @keydown.escape="open = false">
    <UiButton
      type="button"
      variant="ghost"
      size="sm"
      :aria-expanded="open"
      aria-haspopup="menu"
      @click.stop="open = !open"
    >
      Más
    </UiButton>
    <div
      v-if="open"
      class="actions-menu__panel"
      role="menu"
      @click.stop
    >
      <button type="button" role="menuitem" @click="goView">
        Ver detalle
      </button>
      <button
        v-if="canWrite && !account.isArchived"
        type="button"
        role="menuitem"
        @click="goEdit"
      >
        Editar
      </button>
      <button
        type="button"
        role="menuitem"
        disabled
        title="Próximamente"
      >
        Registrar movimiento
      </button>
      <button
        type="button"
        role="menuitem"
        disabled
        title="Próximamente"
      >
        Transferir
      </button>
      <button
        v-if="canArchive && !account.isArchived"
        type="button"
        role="menuitem"
        class="actions-menu__danger"
        @click="goArchive"
      >
        Archivar
      </button>
    </div>
  </div>
</template>

<style scoped>
.actions-menu {
  position: relative;
}

.actions-menu__panel {
  position: absolute;
  right: 0;
  top: calc(100% + 0.25rem);
  z-index: 20;
  min-width: 12rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: var(--space-1);
  display: grid;
}

.actions-menu__panel button {
  text-align: left;
  background: transparent;
  border: 0;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-ink);
  font: inherit;
}

.actions-menu__panel button:hover:not(:disabled) {
  background: var(--color-teal-50);
}

.actions-menu__panel button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.actions-menu__danger {
  color: var(--color-danger) !important;
}
</style>
