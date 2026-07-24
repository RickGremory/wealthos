<script setup lang="ts">
import type { AccountListItemView } from '~/types/accounts'

const open = defineModel<boolean>('open', { default: false })

const props = defineProps<{
  account: AccountListItemView | null
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
}>()

const hasBalance = computed(() => {
  if (!props.account) return false
  return props.account.balance !== '0' && props.account.balance !== '0.00'
})
</script>

<template>
  <UiModal v-model:open="open" title="Archivar cuenta">
    <div v-if="account" class="stack">
      <p>
        La cuenta <strong>{{ account.name }}</strong> ya no aparecerá para registrar movimientos,
        pero su historial y saldos anteriores se conservarán.
      </p>
      <UiAlert v-if="hasBalance" tone="warning" title="Saldo pendiente">
        Esta cuenta todavía tiene un saldo de
        <MoneyValue :amount="account.balance" :currency="account.currency" />.
        Puedes archivarla, pero seguirá formando parte de reportes históricos.
      </UiAlert>
    </div>
    <template #footer>
      <UiButton type="button" variant="ghost" :disabled="loading" @click="open = false">
        Cancelar
      </UiButton>
      <UiButton
        type="button"
        variant="danger"
        :loading="loading"
        @click="emit('confirm')"
      >
        Archivar
      </UiButton>
    </template>
  </UiModal>
</template>
