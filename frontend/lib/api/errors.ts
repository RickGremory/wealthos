export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: unknown
  readonly requestId?: string

  constructor(params: {
    message: string
    status: number
    code?: string
    details?: unknown
    requestId?: string
  }) {
    super(params.message)
    this.name = 'ApiError'
    this.status = params.status
    this.code = params.code ?? 'unknown_error'
    this.details = params.details ?? null
    this.requestId = params.requestId
  }
}

const USER_MESSAGES: Record<string, string> = {
  invalid_credentials: 'Correo o contraseña incorrectos.',
  unauthorized: 'Tu sesión expiró. Vuelve a iniciar sesión.',
  forbidden: 'No tienes permiso para esta acción.',
  not_found: 'No se encontró el recurso solicitado.',
  validation_error: 'Revisa los datos del formulario.',
  conflict: 'Ya existe un registro con esos datos.',
  rate_limited: 'Demasiadas solicitudes. Intenta de nuevo en un momento.',
  network_error: 'No se pudo conectar con el servidor.',
  unknown_error: 'Ocurrió un error inesperado.',
}

export function toUserMessage(codeOrError: string | ApiError | unknown): string {
  if (codeOrError instanceof ApiError) {
    return USER_MESSAGES[codeOrError.code] ?? codeOrError.message ?? USER_MESSAGES.unknown_error
  }
  if (typeof codeOrError === 'string') {
    return USER_MESSAGES[codeOrError] ?? USER_MESSAGES.unknown_error
  }
  return USER_MESSAGES.unknown_error
}

function pickCode(status: number, body: Record<string, unknown> | null): string {
  const raw = body?.code ?? body?.error_code ?? body?.detail
  if (typeof raw === 'string' && raw.length > 0 && !raw.includes(' ')) {
    return raw
  }
  if (status === 401) return 'unauthorized'
  if (status === 403) return 'forbidden'
  if (status === 404) return 'not_found'
  if (status === 409) return 'conflict'
  if (status === 422) return 'validation_error'
  if (status === 429) return 'rate_limited'
  return 'unknown_error'
}

function pickMessage(status: number, body: Record<string, unknown> | null, code: string): string {
  if (body) {
    const detail = body.detail ?? body.message ?? body.error
    if (typeof detail === 'string' && detail.trim()) return detail
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string }
      if (first?.msg) return first.msg
    }
  }
  return toUserMessage(code) || `Error HTTP ${status}`
}

export async function normalizeError(
  error: unknown,
  requestId?: string,
): Promise<ApiError> {
  if (error instanceof ApiError) return error

  // ofetch FetchError shape
  const fetchLike = error as {
    statusCode?: number
    status?: number
    data?: unknown
    response?: Response
    message?: string
    cause?: unknown
  }

  const status = fetchLike.statusCode ?? fetchLike.status ?? 0

  if (!status || status === 0) {
    return new ApiError({
      message: toUserMessage('network_error'),
      status: 0,
      code: 'network_error',
      details: error,
      requestId,
    })
  }

  let body: Record<string, unknown> | null = null
  if (fetchLike.data && typeof fetchLike.data === 'object') {
    body = fetchLike.data as Record<string, unknown>
  } else if (fetchLike.response) {
    try {
      body = (await fetchLike.response.clone().json()) as Record<string, unknown>
    } catch {
      body = null
    }
  }

  const code = pickCode(status, body)
  return new ApiError({
    message: pickMessage(status, body, code),
    status,
    code,
    details: body,
    requestId,
  })
}
