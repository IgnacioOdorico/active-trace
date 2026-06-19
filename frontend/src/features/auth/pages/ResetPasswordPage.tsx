import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import apiClient from '../../../shared/services/httpClient'
import { resetPasswordSchema, type ResetPasswordFormData } from '../schemas'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [backendError, setBackendError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  })

  async function onSubmit(data: ResetPasswordFormData) {
    if (!token) return
    setBackendError(null)
    try {
      await apiClient.post('/api/auth/reset', {
        token,
        password: data.password,
      })
      navigate('/login', { replace: true })
    } catch {
      setBackendError(
        'Error al restablecer la contraseña. El enlace puede haber expirado.',
      )
    }
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
        <div className="w-full max-w-md">
          <BentoCard>
            <div className="px-8 py-10 text-center">
              <h1 className="mb-4 font-headline-sm text-headline-sm text-on-surface">Enlace Inválido</h1>
              <p className="mb-8 font-body-md text-body-md text-on-surface-variant">
                El enlace para restablecer la contraseña no es válido o ha expirado.
              </p>
              <Link
                to="/forgot-password"
                className="text-primary hover:text-primary/80 transition-colors font-body-md text-body-md"
              >
                Solicitar nuevo enlace
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
            <h1 className="mb-8 text-center font-headline-sm text-headline-sm text-on-surface">
              Nueva Contraseña
            </h1>

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
              {backendError && (
                <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-[12px] text-on-error-container">
                  {backendError}
                </div>
              )}

              <div className="space-y-1">
                <label
                  htmlFor="password"
                  className="block font-label-caps text-label-caps text-on-surface-variant uppercase"
                >
                  Nueva contraseña
                </label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="font-body-md text-[12px] text-on-error-container mt-1">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="confirmPassword"
                  className="block font-label-caps text-label-caps text-on-surface-variant uppercase"
                >
                  Confirmar contraseña
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  {...register('confirmPassword')}
                />
                {errors.confirmPassword && (
                  <p className="font-body-md text-[12px] text-on-error-container mt-1">
                    {errors.confirmPassword.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                variant="primary"
                className="w-full justify-center"
              >
                {isSubmitting ? 'Restableciendo...' : 'Restablecer contraseña'}
              </Button>
            </form>
          </div>
        </BentoCard>
      </div>
    </div>
  )
}
