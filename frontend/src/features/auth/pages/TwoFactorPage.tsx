import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../hooks/useAuth'
import { totpSchema, type TotpFormData } from '../schemas'

export default function TwoFactorPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const ephemeralToken = searchParams.get('token')
  const { verify2fa } = useAuth()
  const [backendError, setBackendError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TotpFormData>({
    resolver: zodResolver(totpSchema),
  })

  async function onSubmit(data: TotpFormData) {
    if (!ephemeralToken) return
    setBackendError(null)
    try {
      await verify2fa(ephemeralToken, data.totp_code)
      navigate('/', { replace: true })
    } catch {
      setBackendError('Código inválido. Intente nuevamente.')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          Verificación en Dos Pasos
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          {backendError && (
            <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {backendError}
            </div>
          )}

          <div className="mb-4">
            <label
              htmlFor="totp_code"
              className="block text-sm font-medium text-gray-700"
            >
              Código de verificación
            </label>
            <input
              id="totp_code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              placeholder="000000"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-center text-2xl tracking-widest shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              {...register('totp_code')}
            />
            {errors.totp_code && (
              <p className="mt-1 text-sm text-red-600">
                {errors.totp_code.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? 'Verificando...' : 'Verificar'}
          </button>
        </form>
      </div>
    </div>
  )
}
