import type { ApiClient } from '~/lib/api/types'

export function useApi(): ApiClient {
  const { $api } = useNuxtApp()
  return $api
}
