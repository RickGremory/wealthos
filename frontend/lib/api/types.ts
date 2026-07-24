export interface ApiRequestOptions {
  headers?: Record<string, string>
  query?: Record<string, string | number | boolean | undefined | null>
  body?: unknown
  /** Skip Authorization header */
  skipAuth?: boolean
}

export interface ApiClient {
  get<T>(path: string, options?: ApiRequestOptions): Promise<T>
  post<T>(path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>
  patch<T>(path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>
  delete<T>(path: string, options?: ApiRequestOptions): Promise<T>
}

export type { ApiError } from './errors'
