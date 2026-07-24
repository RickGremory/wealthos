<script setup lang="ts">
import type { CategoryTreeNodeView } from '~/types/categories'
import { hasActiveChildren } from '~/utils/category-tree'

const open = defineModel<boolean>('open', { default: false })

const props = defineProps<{
  category: CategoryTreeNodeView | null
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()

const blocked = computed(() =>
  props.category ? hasActiveChildren(props.category) : false,
)
</script>

<template>
  <UiModal v-model:open="open" title="Archivar categoría">
    <div v-if="category" class="stack">
      <UiAlert v-if="blocked" tone="warning" title="Tiene subcategorías activas">
        Archiva primero las subcategorías activas de
        <strong>{{ category.name }}</strong> antes de archivar el padre.
      </UiAlert>
      <template v-else>
        <p>
          La categoría <strong>{{ category.name }}</strong> dejará de estar disponible
          al registrar movimientos. El historial se conserva.
        </p>
      </template>
    </div>
    <template #footer>
      <UiButton type="button" variant="ghost" :disabled="loading" @click="open = false">
        Cancelar
      </UiButton>
      <UiButton
        type="button"
        variant="danger"
        :loading="loading"
        :disabled="blocked"
        @click="emit('confirm')"
      >
        Archivar
      </UiButton>
    </template>
  </UiModal>
</template>
