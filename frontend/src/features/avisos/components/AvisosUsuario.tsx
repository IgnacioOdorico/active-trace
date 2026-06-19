import { useAvisosUsuario, useAckAviso } from '../hooks/useAvisosApi'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'

const SEVERIDAD_STYLES: Record<string, string> = {
  Info: 'border-l-4 border-l-primary bg-primary/10',
  Advertencia: 'border-l-4 border-l-[#F2C94C] bg-[#F2C94C]/10',
  'Crítico': 'border-l-4 border-l-error bg-error-container/20',
}

export default function AvisosUsuario() {
  const { data, isLoading } = useAvisosUsuario()
  const ack = useAckAviso()

  if (isLoading) return <div className="py-4 font-body-md text-on-surface-variant">Cargando avisos...</div>

  const avisos = data?.items ?? []

  if (avisos.length === 0) return null

  return (
    <div className="mb-6 space-y-4">
      {avisos.map((aviso) => (
        <BentoCard
          key={aviso.id}
          className={`${SEVERIDAD_STYLES[aviso.severidad] ?? 'border-l-4 border-l-outline bg-surface-container-high'}`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-headline-sm text-headline-sm text-on-surface">{aviso.titulo}</p>
              <p className="mt-1 font-body-md text-body-md text-on-surface-variant">{aviso.cuerpo}</p>
            </div>
            {aviso.requiere_ack && (
              <Button
                onClick={() => ack.mutate(aviso.id)}
                disabled={ack.isPending}
                variant="secondary"
                size="sm"
                className="ml-4 flex-shrink-0"
              >
                {ack.isPending ? 'Confirmando...' : 'Confirmar lectura'}
              </Button>
            )}
          </div>
        </BentoCard>
      ))}
    </div>
  )
}
