<script setup lang="ts">
import type { CategoryTreeNodeView } from '~/types/categories'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite } = useOrganizationPermissions()
const {
  form,
  accounts,
  categories,
  currencyOptions,
  submitting,
  previewLoading,
  error,
  fieldErrors,
  preview,
  reset,
  loadLookups,
  runPreview,
  submitCreate,
} = useRecurringForm()

const weekdayOptions = [
  { value: 0, label: 'Dom' },
  { value: 1, label: 'Lun' },
  { value: 2, label: 'Mar' },
  { value: 3, label: 'Mié' },
  { value: 4, label: 'Jue' },
  { value: 5, label: 'Vie' },
  { value: 6, label: 'Sáb' },
]

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo('/app/recurring')
    return
  }
  reset()
  await loadLookups()
})

watch(
  () => [
    form.value.frequency,
    form.value.interval,
    form.value.dayOfMonth,
    form.value.endOfMonth,
    form.value.daysOfWeek.join(','),
    form.value.startsOn,
    form.value.amount,
  ],
  () => {
    void runPreview()
  },
)

function toggleWeekday(day: number) {
  const set = new Set(form.value.daysOfWeek)
  if (set.has(day)) set.delete(day)
  else set.add(day)
  form.value.daysOfWeek = [...set].sort((a, b) => a - b)
}

function applyCadence(kind: 'weekly' | 'biweekly' | 'monthly' | 'quarterly' | 'yearly') {
  if (kind === 'weekly') {
    form.value.frequency = 'weekly'
    form.value.interval = 1
  } else if (kind === 'biweekly') {
    form.value.frequency = 'weekly'
    form.value.interval = 2
  } else if (kind === 'monthly') {
    form.value.frequency = 'monthly'
    form.value.interval = 1
  } else if (kind === 'quarterly') {
    form.value.frequency = 'monthly'
    form.value.interval = 3
  } else {
    form.value.frequency = 'yearly'
    form.value.interval = 1
  }
  void runPreview()
}

const activeCadence = computed(() => {
  const { frequency, interval } = form.value
  if (frequency === 'weekly' && interval === 1) return 'weekly'
  if (frequency === 'weekly' && interval === 2) return 'biweekly'
  if (frequency === 'monthly' && interval === 1) return 'monthly'
  if (frequency === 'monthly' && interval === 3) return 'quarterly'
  if (frequency === 'yearly' && interval === 1) return 'yearly'
  return null
})

async function onSubmit() {
  const id = await submitCreate()
  if (id) await navigateTo(`/app/recurring/${id}`)
}

const expenseCategories = computed(() => flattenCategories(categories.value, 'expense'))
const incomeCategories = computed(() => flattenCategories(categories.value, 'income'))

function flattenCategories(
  nodes: CategoryTreeNodeView[],
  type: string,
): Array<{ id: string, name: string }> {
  const out: Array<{ id: string, name: string }> = []
  const walk = (list: CategoryTreeNodeView[]) => {
    for (const node of list) {
      if (node.type === type) {
        out.push({ id: node.id, name: node.name })
      }
      if (node.children?.length) walk(node.children)
    }
  }
  walk(nodes)
  return out
}

const categoryOptions = computed(() =>
  form.value.direction === 'inflow' ? incomeCategories.value : expenseCategories.value,
)
</script>

<template>
  <div data-testid="recurring-new-page">
    <AppPageHeader
      title="Nuevo recurrente"
      description="Define qué se repite y cómo se programará."
      back-to="/app/recurring"
      back-label="← Recurrentes"
    />

    <UiAlert v-if="error" tone="danger" title="No se pudo crear">
      {{ error }}
    </UiAlert>

    <form class="form" @submit.prevent="onSubmit">
      <UiCard>
        <h2>Tipo</h2>
        <div class="chips">
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': form.direction === 'outflow' }"
            @click="form.direction = 'outflow'"
          >
            Gasto
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': form.direction === 'inflow' }"
            @click="form.direction = 'inflow'"
          >
            Ingreso
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': form.direction === 'transfer' }"
            @click="form.direction = 'transfer'"
          >
            Transferencia
          </button>
        </div>

        <h2>Cadencia</h2>
        <div class="chips">
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': activeCadence === 'weekly' }"
            @click="applyCadence('weekly')"
          >
            Cada semana
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': activeCadence === 'biweekly' }"
            @click="applyCadence('biweekly')"
          >
            Cada 2 semanas
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': activeCadence === 'monthly' }"
            @click="applyCadence('monthly')"
          >
            Cada mes
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': activeCadence === 'quarterly' }"
            @click="applyCadence('quarterly')"
          >
            Cada 3 meses
          </button>
          <button
            type="button"
            class="chip"
            :class="{ 'chip--on': activeCadence === 'yearly' }"
            @click="applyCadence('yearly')"
          >
            Cada año
          </button>
        </div>

        <label>
          Nombre
          <input v-model="form.name" required maxlength="120" data-testid="recurring-name">
          <span v-if="fieldErrors.name" class="err">{{ fieldErrors.name }}</span>
        </label>

        <div class="grid2">
          <label>
            Monto esperado
            <input v-model="form.amount" inputmode="decimal" required data-testid="recurring-amount">
            <span v-if="fieldErrors.amount" class="err">{{ fieldErrors.amount }}</span>
          </label>
          <label>
            Moneda
            <select v-model="form.currency">
              <option v-for="c in currencyOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
        </div>

        <div class="grid2">
          <label>
            Frecuencia
            <select v-model="form.frequency">
              <option value="daily">Diaria</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensual</option>
              <option value="yearly">Anual</option>
            </select>
          </label>
          <label>
            Intervalo
            <input v-model.number="form.interval" type="number" min="1">
          </label>
        </div>

        <div v-if="form.frequency === 'weekly'" class="weekdays">
          <button
            v-for="day in weekdayOptions"
            :key="day.value"
            type="button"
            class="chip"
            :class="{ 'chip--on': form.daysOfWeek.includes(day.value) }"
            @click="toggleWeekday(day.value)"
          >
            {{ day.label }}
          </button>
        </div>

        <div v-if="form.frequency === 'monthly' || form.frequency === 'yearly'" class="grid2">
          <label v-if="form.frequency === 'yearly'">
            Mes
            <input v-model.number="form.monthOfYear" type="number" min="1" max="12">
          </label>
          <label>
            Día del mes
            <input
              v-model.number="form.dayOfMonth"
              type="number"
              min="1"
              max="31"
              :disabled="form.endOfMonth"
            >
          </label>
          <label class="check">
            <input v-model="form.endOfMonth" type="checkbox">
            Último día del mes
          </label>
        </div>

        <div class="grid2">
          <label>
            Empieza el
            <input v-model="form.startsOn" type="date" required>
          </label>
          <label>
            Termina el (opcional)
            <input v-model="form.endsOn" type="date">
          </label>
        </div>

        <div v-if="form.direction === 'transfer'" class="grid2">
          <label>
            Cuenta origen
            <select v-model="form.accountId">
              <option value="">Selecciona…</option>
              <option v-for="a in accounts" :key="a.id" :value="a.id">
                {{ a.name }} ({{ a.currency }})
              </option>
            </select>
          </label>
          <label>
            Cuenta destino
            <select v-model="form.destinationAccountId">
              <option value="">Selecciona…</option>
              <option v-for="a in accounts" :key="a.id" :value="a.id">
                {{ a.name }} ({{ a.currency }})
              </option>
            </select>
          </label>
        </div>

        <div v-else class="grid2">
          <label>
            Cuenta (opcional)
            <select v-model="form.accountId">
              <option value="">Sin cuenta</option>
              <option v-for="a in accounts" :key="a.id" :value="a.id">
                {{ a.name }} ({{ a.currency }})
              </option>
            </select>
          </label>
          <label>
            Categoría (opcional)
            <select v-model="form.categoryId">
              <option value="">Sin categoría</option>
              <option v-for="c in categoryOptions" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </label>
        </div>

        <label>
          Notas
          <textarea v-model="form.notes" rows="3" />
        </label>
      </UiCard>

      <UiCard>
        <h2>Así se programará</h2>
        <p v-if="previewLoading" class="muted">Calculando vista previa…</p>
        <ul v-else-if="preview?.dates?.length" class="preview">
          <li v-for="date in preview.dates.slice(0, 6)" :key="date">{{ date }}</li>
        </ul>
        <p v-else class="muted">Ajusta la cadencia para ver las próximas fechas.</p>
      </UiCard>

      <div class="actions">
        <UiButton type="button" variant="ghost" :disabled="submitting" @click="navigateTo('/app/recurring')">
          Cancelar
        </UiButton>
        <UiButton type="submit" :loading="submitting" data-testid="recurring-create-submit">
          Crear recurrente
        </UiButton>
      </div>
    </form>
  </div>
</template>

<style scoped>
.form {
  display: grid;
  gap: var(--space-4);
}
.chips,
.weekdays {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}
.chip {
  border: 1px solid var(--color-border);
  background: transparent;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  cursor: pointer;
}
.chip--on {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: transparent;
}
label {
  display: grid;
  gap: 0.35rem;
  margin-bottom: var(--space-3);
  font-size: 0.9rem;
}
input,
select,
textarea {
  padding: 0.55rem 0.7rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.grid2 {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
}
.check {
  align-content: end;
}
.err {
  color: var(--color-danger, #b91c1c);
  font-size: 0.8rem;
}
.preview {
  margin: 0;
  padding-left: 1.1rem;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
.muted {
  color: var(--color-text-muted);
}
</style>
