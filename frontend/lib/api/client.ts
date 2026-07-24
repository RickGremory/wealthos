import { ofetch, type FetchOptions } from 'ofetch'
import { createRequestId } from '~/utils/id'
import { ApiError, normalizeError } from './errors'
import type { ApiClient, ApiRequestOptions } from './types'

export interface CreateApiClientOptions {
  baseURL: string
  getAccessToken: () => string | null | undefined
  getOrganizationId: () => string | null | undefined
  onUnauthorized?: () => void | Promise<void>
}

function buildQuery(query?: ApiRequestOptions['query']): Record<string, string> | undefined {
  if (!query) return undefined
  const out: Record<string, string> = {}
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue
    out[key] = String(value)
  }
  return Object.keys(out).length ? out : undefined
}

export function createApiClient(options: CreateApiClientOptions): ApiClient {
  const request = async <T>(
    method: string,
    path: string,
    opts: ApiRequestOptions = {},
  ): Promise<T> => {
    const requestId = createRequestId()
    const headers: Record<string, string> = {
      Accept: 'application/json',
      'X-Request-Id': requestId,
      ...opts.headers,
    }

    if (!opts.skipAuth) {
      const token = options.getAccessToken()
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }

    const orgId = options.getOrganizationId()
    if (orgId) {
      headers['X-Organization-Id'] = orgId
    }

    const fetchOptions: FetchOptions<'json'> = {
      baseURL: options.baseURL,
      method,
      headers,
      query: buildQuery(opts.query),
      body: opts.body as FetchOptions['body'],
    }

    try {
      return await ofetch<T>(path, fetchOptions)
    } catch (error) {
      const apiError = await normalizeError(error, requestId)
      if (apiError.status === 401 && options.onUnauthorized) {
        await options.onUnauthorized()
      }
      throw apiError
    }
  }

  return {
    get: <T>(path: string, options?: ApiRequestOptions) =>
      request<T>('GET', path, options),
    post: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
      request<T>('POST', path, { ...options, body }),
    patch: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
      request<T>('PATCH', path, { ...options, body }),
    delete: <T>(path: string, options?: ApiRequestOptions) =>
      request<T>('DELETE', path, options),
  }
}

export { ApiError }
