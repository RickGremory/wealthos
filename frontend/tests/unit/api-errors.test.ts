import { describe, expect, it } from 'vitest'
import { ApiError, normalizeError, toUserMessage } from '../../lib/api/errors'

describe('ApiError', () => {
  it('stores status and code', () => {
    const err = new ApiError({
      message: 'boom',
      status: 400,
      code: 'validation_error',
    })
    expect(err.name).toBe('ApiError')
    expect(err.status).toBe(400)
    expect(err.code).toBe('validation_error')
  })
})

describe('toUserMessage', () => {
  it('maps known codes', () => {
    expect(toUserMessage('unauthorized')).toMatch(/sesión/i)
    expect(toUserMessage('invalid_credentials')).toMatch(/incorrectos/i)
  })

  it('uses ApiError message when code unknown', () => {
    const err = new ApiError({
      message: 'Detalle custom',
      status: 500,
      code: 'weird_code',
    })
    expect(toUserMessage(err)).toBe('Detalle custom')
  })
})

describe('normalizeError', () => {
  it('normalizes ofetch-like errors', async () => {
    const err = await normalizeError({
      statusCode: 401,
      data: { detail: 'Not authenticated' },
    }, 'req-1')

    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(401)
    expect(err.code).toBe('unauthorized')
    expect(err.requestId).toBe('req-1')
  })

  it('maps network failures', async () => {
    const err = await normalizeError(new Error('fetch failed'))
    expect(err.code).toBe('network_error')
    expect(err.status).toBe(0)
  })

  it('maps 422 to validation_error', async () => {
    const err = await normalizeError({
      statusCode: 422,
      data: {
        detail: [{ msg: 'Field required' }],
      },
    })
    expect(err.code).toBe('validation_error')
    expect(err.message).toBe('Field required')
  })
})
