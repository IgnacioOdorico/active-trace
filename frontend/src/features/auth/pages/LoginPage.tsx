import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../hooks/useAuth'
import { loginSchema, type LoginFormData } from '../schemas'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

export default function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirectTo = searchParams.get('redirect') || '/'
  const { login } = useAuth()
  const [backendError, setBackendError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  async function onSubmit(data: LoginFormData) {
    setBackendError(null)
    try {
      const result = await login(data.email, data.password)
      if ('requires_2fa' in result && result.requires_2fa) {
        navigate(`/login/2fa?token=${result.ephemeral_token}`)
      } else {
        navigate(redirectTo, { replace: true })
      }
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message
          : 'Credenciales inválidas. Intente nuevamente.'
      setBackendError(message)
      setError('password', { message: '' })
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
      <div className="w-full max-w-md">
        <BentoCard>
          <div className="px-8 py-10">
            <h1 className="mb-2 text-center font-headline-lg text-headline-lg text-on-surface">
              Active Trace
            </h1>
            <h2 className="mb-8 text-center font-body-md text-body-md text-on-surface-variant">
              Iniciar Sesión
            </h2>

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
                  <p className="font-body-md text-[12px] text-on-error-container">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-1">
                <label
                  htmlFor="password"
                  className="block font-label-caps text-label-caps text-on-surface-variant uppercase"
                >
                  Contraseña
                </label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  {...register('password')}
                />
                {errors.password && (
                  <p className="font-body-md text-[12px] text-on-error-container">
                    {errors.password.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                variant="primary"
                className="w-full justify-center"
              >
                {isSubmitting ? 'Ingresando...' : 'Ingresar'}
              </Button>
            </form>

            <p className="mt-6 text-center font-body-md text-[12px]">
              <Link to="/forgot-password" className="text-primary hover:text-primary/80 transition-colors">
                ¿Olvidó su contraseña?
              </Link>
            </p>
          </div>
        </BentoCard>
      </div>
    </div>
  )
}
