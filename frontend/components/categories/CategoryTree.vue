<script setup lang="ts">
import type { CategoryTreeNodeView } from '~/types/categories'

defineProps<{
  nodes: CategoryTreeNodeView[]
  canEdit?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  edit: [node: CategoryTreeNodeView]
  archive: [node: CategoryTreeNodeView]
}>()
</script>

<template>
  <ul v-if="nodes.length" class="category-tree" data-testid="category-tree">
    <CategoryTreeItem
      v-for="node in nodes"
      :key="node.id"
      :node="node"
      :can-edit="canEdit"
      :can-archive="canArchive"
      @edit="emit('edit', $event)"
      @archive="emit('archive', $event)"
    />
  </ul>
  <UiEmptyState
    v-else
    title="Sin categorías en esta vista"
    description="Crea una categoría o cambia de pestaña."
  />
</template>

<style scoped>
.category-tree {
  margin: 0;
  padding: 0;
}
</style>
