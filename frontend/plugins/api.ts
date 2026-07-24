import { createApiClient } from '~/lib/api/client'
import type { ApiClient } from '~/lib/api/types'

declare module '#app' {
  interface NuxtApp {
    $api: ApiClient
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $api: ApiClient
  }
}

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const auth = useAuthStore()
  const organization = useOrganizationStore()

  const api = createApiClient({
    baseURL: String(config.public.apiBaseUrl),
    getAccessToken: () => auth.token,
    getOrganizationId: () => organization.currentOrganizationId,
    onUnauthorized: async () => {
      if (auth.token) {
        auth.setToken(null)
        auth.user = null
      }
    },
  })

  return {
    provide: {
      api,
    },
  }
})
