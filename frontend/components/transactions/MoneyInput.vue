<script setup lang="ts">
import { displayAmountMagnitude } from '~/utils/transaction-presentation'

const props = withDefaults(
  defineProps<{
    label?: string
    currency?: string
    error?: string
    disabled?: boolean
    /** When true, strip leading minus and disallow negatives */
    unsigned?: boolean
    dominant?: boolean
  }>(),
  {
    label: 'Monto',
    currency: 'MXN',
    error: undefined,
    disabled: false,
    unsigned: true,
    dominant: true,
  },
)

const model = defineModel<string>({ default: '' })
const focused = ref(false)

function sanitize(raw: string): string {
  let value = raw.replace(/[^\d.,-]/g, '').replace(/,/g, '.')
  if (props.unsigned) {
    value = value.replace(/-/g, '')
  } else {
    // allow a single leading minus
    const neg = value.startsWith('-')
    value = value.replace(/-/g, '')
    if (neg) value = `-${value}`
  }
  const parts = value.replace(/^\./, '0.').split('.')
  if (parts.length > 2) {
    value = `${parts[0]}.${parts.slice(1).join('')}`
  }
  const [intPart = '', frac = ''] = value.replace(/^-/, '').split('.')
  const sign = value.startsWith('-') ? '-' : ''
  const clippedFrac = frac.slice(0, 2)
  if (value.includes('.')) {
    return `${sign}${intPart}.${clippedFrac}`
  }
  return `${sign}${intPart}`
}

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  model.value = sanitize(target.value)
}

function onBlur() {
  focused.value = false
  if (!model.value.trim()) {
    model.value = ''
    return
  }
  const mag = displayAmountMagnitude(model.value)
  const [whole = '0', frac = ''] = mag.split('.')
  const formatted = `${whole}.${(frac + '00').slice(0, 2)}`
  model.value = props.unsigned
    ? formatted
    : model.value.trim().startsWith('-')
      ? `-${formatted}`
      : formatted
}

function onFocus() {
  focused.value = true
}
</script>

<template>
  <label
    class="money-input stack-sm"
    :class="{ 'money-input--dominant': dominant }"
    data-testid="money-input"
  >
    <span v-if="label" class="money-input__label">{{ label }}</span>
    <div class="money-input__row">
      <span class="money-input__currency">{{ currency }}</span>
      <input
        class="money-input__control"
        inputmode="decimal"
        :value="model"
        :disabled="disabled"
        :aria-invalid="Boolean(error) || undefined"
        placeholder="0.00"
        @input="onInput"
        @blur="onBlur"
        @focus="onFocus"
      >
    </div>
    <span v-if="error" class="money-input__error">{{ error }}</span>
  </label>
</template>

<style scoped>
.money-input__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
}

.money-input--dominant .money-input__control {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.money-input__row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  padding: 0.35rem 0.75rem;
}

.money-input__currency {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-teal-800);
}

.money-input__control {
  flex: 1;
  border: 0;
  background: transparent;
  padding: 0.55rem 0;
  outline: none;
  min-width: 0;
  font-variant-numeric: tabular-nums;
}

.money-input__error {
  font-size: 0.8rem;
  color: var(--color-danger);
}
</style>
