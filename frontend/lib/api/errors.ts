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

  // Accounts
  ACCOUNT_NAME_ALREADY_EXISTS: 'Ya existe una cuenta con ese nombre.',
  ACCOUNT_HAS_TRANSACTIONS: 'Esta cuenta tiene movimientos y no admite ese cambio.',
  ACCOUNT_TYPE_CHANGE_NOT_ALLOWED: 'No se puede cambiar el tipo de esta cuenta.',
  ACCOUNT_CURRENCY_CHANGE_NOT_ALLOWED: 'No se puede cambiar la moneda de esta cuenta.',
  ACCOUNT_NOT_FOUND: 'No se encontró la cuenta.',
  ACCOUNT_ARCHIVE_RESTRICTED: 'No se puede archivar esta cuenta en este momento.',
  ACCOUNT_ALREADY_ARCHIVED: 'Esta cuenta ya está archivada.',
  INVALID_OPENING_BALANCE: 'El saldo inicial no es válido.',
  INVALID_ACCOUNT_TYPE: 'El tipo de cuenta no es válido.',
  INVALID_LAST_FOUR: 'Los últimos cuatro dígitos deben ser exactamente 4 números.',

  // Categories
  CATEGORY_NAME_ALREADY_EXISTS: 'Ya existe una categoría con ese nombre en este nivel.',
  CATEGORY_PARENT_NOT_FOUND: 'No se encontró la categoría padre.',
  CATEGORY_TYPE_MISMATCH: 'El tipo de la subcategoría debe coincidir con el del padre.',
  CATEGORY_CYCLE_DETECTED: 'No se puede crear una jerarquía circular.',
  CATEGORY_HAS_ACTIVE_CHILDREN: 'Archiva primero las subcategorías activas.',
  CATEGORY_TYPE_CHANGE_NOT_ALLOWED: 'No se puede cambiar el tipo de esta categoría.',
  SYSTEM_CATEGORY_RESTRICTED: 'Las categorías del sistema no se pueden modificar ni archivar.',
  CATEGORY_NOT_FOUND: 'No se encontró la categoría.',
  CATEGORY_ALREADY_ARCHIVED: 'Esta categoría ya está archivada.',
  CATEGORY_DEPTH_EXCEEDED: 'Solo se permiten dos niveles de categorías.',

  // Transactions
  TRANSACTION_NOT_FOUND: 'No se encontró la transacción.',
  TRANSACTION_ALREADY_VOIDED: 'Esta transacción ya está anulada.',
  TRANSACTION_VOID_RESTRICTED: 'No tienes permiso para anular esta transacción.',
  INSUFFICIENT_BALANCE: 'Saldo insuficiente en la cuenta.',
  INVALID_TRANSACTION_AMOUNT: 'El monto de la transacción no es válido.',
  INVALID_TRANSFER_ACCOUNTS: 'Las cuentas de la transferencia no son válidas.',
  CURRENCY_MISMATCH: 'Las cuentas deben compartir la misma moneda.',
  ACCOUNT_TYPE_NOT_ALLOWED: 'Este tipo de cuenta no admite esa operación.',
  CATEGORY_REQUIRED: 'Selecciona una categoría.',
  SAME_ACCOUNT_TRANSFER: 'Origen y destino deben ser cuentas distintas.',
  IDEMPOTENCY_CONFLICT: 'Esta operación ya se procesó. Revisa tus movimientos.',
}

/** Match backend English detail strings when no structured code is present. */
const DETAIL_PATTERNS: Array<{ pattern: RegExp, code: string }> = [
  { pattern: /invalid email or password|incorrect (email|password)|invalid credentials/i, code: 'invalid_credentials' },
  { pattern: /account.*already exists|name already exists.*account/i, code: 'ACCOUNT_NAME_ALREADY_EXISTS' },
  { pattern: /account is already archived/i, code: 'ACCOUNT_ALREADY_ARCHIVED' },
  { pattern: /account not found/i, code: 'ACCOUNT_NOT_FOUND' },
  { pattern: /category with this name already exists/i, code: 'CATEGORY_NAME_ALREADY_EXISTS' },
  { pattern: /archive active child/i, code: 'CATEGORY_HAS_ACTIVE_CHILDREN' },
  { pattern: /system categor(?:y|ies) cannot/i, code: 'SYSTEM_CATEGORY_RESTRICTED' },
  { pattern: /parent category.*not found|parent.*does not exist/i, code: 'CATEGORY_PARENT_NOT_FOUND' },
  { pattern: /type differs|type mismatch/i, code: 'CATEGORY_TYPE_MISMATCH' },
  { pattern: /nest beyond|depth/i, code: 'CATEGORY_DEPTH_EXCEEDED' },
  { pattern: /category not found/i, code: 'CATEGORY_NOT_FOUND' },
  { pattern: /already archived/i, code: 'CATEGORY_ALREADY_ARCHIVED' },
  { pattern: /last.?four|4-digit/i, code: 'INVALID_LAST_FOUR' },
  { pattern: /invalid.*account type|account type.*not supported/i, code: 'INVALID_ACCOUNT_TYPE' },
  { pattern: /transaction not found/i, code: 'TRANSACTION_NOT_FOUND' },
  { pattern: /already voided|already cancelled/i, code: 'TRANSACTION_ALREADY_VOIDED' },
  { pattern: /insufficient (funds|balance)/i, code: 'INSUFFICIENT_BALANCE' },
  { pattern: /currency mismatch|same currency/i, code: 'CURRENCY_MISMATCH' },
  { pattern: /same account|source and destination/i, code: 'SAME_ACCOUNT_TRANSFER' },
]

function messageFromDetail(detail: string): string | null {
  for (const { pattern, code } of DETAIL_PATTERNS) {
    if (pattern.test(detail)) {
      return USER_MESSAGES[code] ?? null
    }
  }
  return null
}

export function toUserMessage(codeOrError: string | ApiError | unknown): string {
  if (codeOrError instanceof ApiError) {
    const fromDetail = messageFromDetail(codeOrError.message)
    const genericCodes = new Set([
      'unknown_error',
      'validation_error',
      'conflict',
      'not_found',
      'forbidden',
      'unauthorized',
    ])
    // Prefer structured codes when they are domain-specific.
    if (USER_MESSAGES[codeOrError.code] && !genericCodes.has(codeOrError.code)) {
      return USER_MESSAGES[codeOrError.code]
    }
    if (fromDetail) return fromDetail
    if (USER_MESSAGES[codeOrError.code]) return USER_MESSAGES[codeOrError.code]
    return codeOrError.message || USER_MESSAGES.unknown_error
  }
  if (typeof codeOrError === 'string') {
    if (USER_MESSAGES[codeOrError]) return USER_MESSAGES[codeOrError]
    const fromDetail = messageFromDetail(codeOrError)
    if (fromDetail) return fromDetail
    return USER_MESSAGES.unknown_error
  }
  return USER_MESSAGES.unknown_error
}

function pickCode(status: number, body: Record<string, unknown> | null): string {
  const detail = body?.detail ?? body?.message ?? body?.error
  if (typeof detail === 'string') {
    if (/invalid email or password|incorrect (email|password)|invalid credentials/i.test(detail)) {
      return 'invalid_credentials'
    }
    // Prefer structured code embedded in detail only when it's a slug (no spaces).
    if (detail.length > 0 && !detail.includes(' ')) {
      return detail
    }
  }

  const raw = body?.code ?? body?.error_code
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
