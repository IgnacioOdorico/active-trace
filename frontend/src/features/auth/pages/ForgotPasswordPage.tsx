import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import apiClient from '../../../shared/services/httpClient'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../schemas'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
      <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
        <div className="w-full max-w-md">
          <BentoCard>
            <div className="px-8 py-10 text-center">
              <h1 className="mb-4 font-headline-sm text-headline-sm text-on-surface">
                Solicitud Enviada
              </h1>
              <p className="mb-8 font-body-md text-body-md text-on-surface-variant">
                Si el email está registrado, recibirá instrucciones para restablecer
                su contraseña.
              </p>
              <Link
                to="/login"
                className="text-primary hover:text-primary/80 transition-colors font-body-md text-body-md"
              >
                Volver al inicio de sesión
              </Link>
            </div>
          </BentoCard>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
      <div className="w-full max-w-md">
        <BentoCard>
          <div className="px-8 py-10">
            <h1 className="mb-2 text-center font-headline-sm text-headline-sm text-on-surface">
              Restablecer Contraseña
            </h1>
            <p className="mb-8 text-center font-body-md text-body-md text-on-surface-variant">
              Ingrese su email y le enviaremos un enlace para restablecer su
              contraseña.
            </p>

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
              {backendError && (
                <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-[12px] text-on-error-container">
                  {backendError}
                </div>
              )}

              <div className="space-y-1">
                <label
                  htmlFor="email"
                  className="block font-label-caps text-label-caps text-on-surface-variant uppercase"
                >
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  {...register('email')}
                />
                {errors.email && (
                  <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.email.message}</p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                variant="primary"
                className="w-full justify-center"
              >
                {isSubmitting ? 'Enviando...' : 'Enviar solicitud'}
              </Button>
            </form>

            <p className="mt-6 text-center font-body-md text-[12px]">
              <Link
                to="/login"
                className="text-primary hover:text-primary/80 transition-colors"
              >
                Volver al inicio de sesión
              </Link>
            </p>
          </div>
        </BentoCard>
      </div>
    </div>
  )
}
