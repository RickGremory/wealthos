import { createRequestId } from '~/utils/id'

export function useTransactionIdempotency() {
  const key = ref(createRequestId())

  function renew() {
    key.value = createRequestId()
    return key.value
  }

  function current() {
    return key.value
  }

  return {
    key: readonly(key),
    renew,
    current,
  }
}
