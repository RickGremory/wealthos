import type { ToastTone } from '~/stores/notifications'

export function useToast() {
  const notifications = useNotificationsStore()

  function toast(input: {
    title: string
    message?: string
    tone?: ToastTone
    timeoutMs?: number
  }) {
    return notifications.push(input)
  }

  function success(title: string, message?: string) {
    return toast({ title, message, tone: 'success' })
  }

  function error(title: string, message?: string) {
    return toast({ title, message, tone: 'danger' })
  }

  function info(title: string, message?: string) {
    return toast({ title, message, tone: 'info' })
  }

  function warning(title: string, message?: string) {
    return toast({ title, message, tone: 'warning' })
  }

  return { toast, success, error, info, warning, dismiss: notifications.dismiss }
}
