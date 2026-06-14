import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import apiClient from '../../../shared/services/httpClient'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../schemas'

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false)
  const [backendError, setBackendError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  async function onSubmit(data: ForgotPasswordFormData) {
    setBackendError(null)
    try {
      await apiClient.post('/api/auth/forgot', { email: data.email })
      setSubmitted(true)
    } catch {
      setBackendError('Error al enviar la solicitud. Intente nuevamente.')
    }
  }

  if (submitted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-md">
          <h1 className="mb-4 text-2xl font-bold text-gray-900">
            Solicitud Enviada
          </h1>
          <p className="mb-6 text-gray-600">
            Si el email está registrado, recibirá instrucciones para restablecer
            su contraseña.
          </p>
          <Link
            to="/login"
            className="text-blue-600 hover:text-blue-800"
          >
            Volver al inicio de sesión
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          Restablecer Contraseña
        </h1>
        <p className="mb-4 text-center text-sm text-gray-600">
          Ingrese su email y le enviaremos un enlace para restablecer su
          contraseña.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          {backendError && (
            <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
              {backendError}
            </div>
          )}

          <div className="mb-4">
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              {...register('email')}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? 'Enviando...' : 'Enviar solicitud'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-600">
          <Link
            to="/login"
            className="text-blue-600 hover:text-blue-800"
          >
            Volver al inicio de sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
