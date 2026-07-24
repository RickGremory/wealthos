<script setup lang="ts">
import type { CategoryTreeNodeView } from '~/types/categories'

defineProps<{
  node: CategoryTreeNodeView
  depth?: number
  canEdit?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  edit: [node: CategoryTreeNodeView]
  archive: [node: CategoryTreeNodeView]
}>()

const expanded = ref(true)
</script>

<template>
  <li class="tree-item" :style="{ '--depth': depth ?? 0 }">
    <div class="tree-item__row">
      <div class="tree-item__main">
        <button
          v-if="node.children?.length"
          type="button"
          class="tree-item__toggle"
          :aria-expanded="expanded"
          @click="expanded = !expanded"
        >
          {{ expanded ? '▾' : '▸' }}
        </button>
        <span v-else class="tree-item__spacer" />
        <CategoryBadge
          :name="node.name"
          :color="node.color"
          :icon="node.icon"
          :is-system="node.isSystem"
        />
      </div>
      <div
        v-if="(canEdit || canArchive) && !node.isSystem && !node.isArchived"
        class="tree-item__actions"
      >
        <UiButton
          v-if="canEdit"
          type="button"
          variant="ghost"
          size="sm"
          @click="emit('edit', node)"
        >
          Editar
        </UiButton>
        <UiButton
          v-if="canArchive"
          type="button"
          variant="ghost"
          size="sm"
          @click="emit('archive', node)"
        >
          Archivar
        </UiButton>
      </div>
    </div>
    <ul v-if="expanded && node.children?.length" class="tree-item__children">
      <CategoryTreeItem
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="(depth ?? 0) + 1"
        :can-edit="canEdit"
        :can-archive="canArchive"
        @edit="emit('edit', $event)"
        @archive="emit('archive', $event)"
      />
    </ul>
  </li>
</template>

<style scoped>
.tree-item {
  list-style: none;
  min-width: 0;
}

.tree-item__row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  padding: 0.55rem 0.35rem;
  padding-left: calc(var(--depth) * 1.1rem + 0.35rem);
  border-radius: var(--radius-md);
}

.tree-item__row:hover {
  background: var(--color-surface-muted);
}

.tree-item__main {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  flex: 1 1 auto;
}

.tree-item__toggle,
.tree-item__spacer {
  width: 1.25rem;
  flex-shrink: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  color: var(--color-slate-600);
}

.tree-item__children {
  margin: 0;
  padding: 0;
  min-width: 0;
}

.tree-item__actions {
  margin-left: auto;
  display: flex;
  flex-shrink: 0;
  gap: var(--space-1);
}

@media (max-width: 640px) {
  .tree-item__row {
    flex-wrap: wrap;
    align-items: flex-start;
    padding-left: calc(var(--depth) * 0.75rem + 0.25rem);
  }

  .tree-item__main {
    flex: 1 1 100%;
    max-width: 100%;
  }

  .tree-item__actions {
    margin-left: calc(1.25rem + var(--space-2));
    width: calc(100% - 1.25rem - var(--space-2));
    justify-content: flex-start;
  }
}
</style>
