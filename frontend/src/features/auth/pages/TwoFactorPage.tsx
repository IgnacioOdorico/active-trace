import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../hooks/useAuth'
import { totpSchema, type TotpFormData } from '../schemas'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
    <div className="flex min-h-screen items-center justify-center bg-surface-container-lowest p-4">
      <div className="w-full max-w-md">
        <BentoCard>
          <div className="px-8 py-10">
            <h1 className="mb-8 text-center font-headline-sm text-headline-sm text-on-surface">
              Verificación en Dos Pasos
            </h1>

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-6">
              {backendError && (
                <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-[12px] text-on-error-container">
                  {backendError}
                </div>
              )}

              <div className="space-y-1">
                <label
                  htmlFor="totp_code"
                  className="block font-label-caps text-label-caps text-on-surface-variant uppercase text-center"
                >
                  Código de verificación
                </label>
                <Input
                  id="totp_code"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  placeholder="000000"
                  className="text-center font-mono-data text-2xl tracking-[0.5em]"
                  {...register('totp_code')}
                />
                {errors.totp_code && (
                  <p className="font-body-md text-[12px] text-on-error-container text-center mt-1">
                    {errors.totp_code.message}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                variant="primary"
                className="w-full justify-center"
              >
                {isSubmitting ? 'Verificando...' : 'Verificar'}
              </Button>
            </form>
          </div>
        </BentoCard>
      </div>
    </div>
  )
}
