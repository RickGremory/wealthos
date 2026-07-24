import { defineStore } from 'pinia'

export type ToastTone = 'info' | 'success' | 'warning' | 'danger'

export interface ToastItem {
  id: string
  title: string
  message?: string
  tone: ToastTone
  timeoutMs: number
}

export const useNotificationsStore = defineStore('notifications', () => {
  const toasts = ref<ToastItem[]>([])

  function push(input: {
    title: string
    message?: string
    tone?: ToastTone
    timeoutMs?: number
  }) {
    const id = createRequestId()
    const toast: ToastItem = {
      id,
      title: input.title,
      message: input.message,
      tone: input.tone ?? 'info',
      timeoutMs: input.timeoutMs ?? 4000,
    }
    toasts.value = [...toasts.value, toast]

    if (import.meta.client && toast.timeoutMs > 0) {
      window.setTimeout(() => dismiss(id), toast.timeoutMs)
    }

    return id
  }

  function dismiss(id: string) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  function clear() {
    toasts.value = []
  }

  return { toasts, push, dismiss, clear }
})
