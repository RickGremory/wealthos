<script setup lang="ts">
import type {
  CategoryParentOption,
  CreateCategoryFormModel,
  UpdateCategoryFormModel,
} from '~/types/categories'

const form = defineModel<CreateCategoryFormModel | UpdateCategoryFormModel>('form', {
  required: true,
})

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    parentOptions?: CategoryParentOption[]
    allowTypeChange?: boolean
    fieldError?: string
    submitting?: boolean
  }>(),
  {
    parentOptions: () => [],
    allowTypeChange: true,
    fieldError: undefined,
    submitting: false,
  },
)

const emit = defineEmits<{
  submit: []
}>()

const isCreate = computed(() => props.mode === 'create')

const createForm = computed(() => form.value as CreateCategoryFormModel)

const nameModel = computed({
  get: () => form.value.name,
  set: (value: string) => {
    form.value.name = value
  },
})

const iconModel = computed({
  get: () => form.value.icon,
  set: (value: string) => {
    form.value.icon = value
  },
})

const colorModel = computed({
  get: () => form.value.color,
  set: (value: string) => {
    form.value.color = value
  },
})

const typeModel = computed({
  get: () => (isCreate.value ? createForm.value.categoryType : 'expense'),
  set: (value: 'income' | 'expense') => {
    if (isCreate.value) {
      createForm.value.categoryType = value
    }
  },
})

const parentSelectOptions = computed(() => [
  { label: 'Sin padre (categoría raíz)', value: '' },
  ...props.parentOptions.map(p => ({ label: p.label, value: p.id })),
])

const parentIdModel = computed({
  get: () => (isCreate.value ? (createForm.value.parentId ?? '') : ''),
  set: (value: string) => {
    if (isCreate.value) {
      createForm.value.parentId = value || null
    }
  },
})
</script>

<template>
  <form class="category-form stack" @submit.prevent="emit('submit')">
    <UiInput
      v-model="nameModel"
      label="Nombre"
      required
      :error="fieldError"
      :disabled="submitting"
      placeholder="Ej. Comida"
    />

    <CategoryTypeSelector
      v-if="mode === 'create' && allowTypeChange"
      v-model="typeModel"
      :disabled="submitting"
    />

    <UiSelect
      v-if="mode === 'create'"
      v-model="parentIdModel"
      label="Categoría padre (opcional)"
      :options="parentSelectOptions"
      :disabled="submitting"
    />

    <CategoryIconPicker v-model="iconModel" />
    <CategoryColorPicker v-model="colorModel" />

    <div class="category-form__actions">
      <slot name="actions" />
    </div>
  </form>
</template>

<style scoped>
.category-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
</style>
