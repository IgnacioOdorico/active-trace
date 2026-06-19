import { useMemo, useState } from 'react'
import { useAvisosGestion, useEliminarAviso } from '../hooks/useAvisosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import AvisoForm from './AvisoForm'
import type { Aviso } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

function severidadVariant(severidad: string): 'success' | 'warning' | 'error' | 'neutral' {
  switch (severidad) {
    case 'Info':
      return 'success'
    case 'Advertencia':
      return 'warning'
    case 'Crítico':
      return 'error'
    default:
      return 'neutral'
  }
}

export default function GestionAvisos() {
  const { data, isLoading, isError } = useAvisosGestion()
  const eliminar = useEliminarAviso()
  const [editando, setEditando] = useState<Aviso | null>(null)
  const [creando, setCreando] = useState(false)
  const { data: materias } = useMaterias()
  const { data: cohortes } = useCohortes()

  const nombreMateria = useMemo(() => {
    const mapa = new Map(materias?.map((m) => [m.id, m.nombre]))
    return (id: string) => mapa.get(id) ?? id
  }, [materias])

  const nombreCohorte = useMemo(() => {
    const mapa = new Map(cohortes?.map((c) => [c.id, c.nombre]))
    return (id: string) => mapa.get(id) ?? id
  }, [cohortes])

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant">Cargando avisos...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-error">Error al cargar avisos.</div>

  const avisos = data?.items ?? []

  if (creando || editando) {
    return (
      <BentoCard>
        <h2 className="mb-6 font-headline-sm text-headline-sm text-on-surface">
          {editando ? 'Editar aviso' : 'Nuevo aviso'}
        </h2>
        <AvisoForm
          aviso={editando ?? undefined}
          onSuccess={() => {
            setEditando(null)
            setCreando(false)
          }}
          onCancel={() => {
            setEditando(null)
            setCreando(false)
          }}
        />
      </BentoCard>
    )
  }

  return (
    <div>
      <div className="mb-6 flex justify-end">
        <Button
          onClick={() => setCreando(true)}
          variant="primary"
        >
          + Nuevo aviso
        </Button>
      </div>

      {avisos.length === 0 ? (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No hay avisos publicados.
        </div>
      ) : (
        <div className="space-y-4">
          {[...avisos]
            .sort((a, b) => a.orden - b.orden)
            .map((aviso) => (
              <BentoCard
                key={aviso.id}
                className="flex items-start justify-between"
              >
                <div className="flex-1">
                  <div className="mb-2 flex items-center gap-2">
                    <Badge variant={severidadVariant(aviso.severidad)}>
                      {aviso.severidad}
                    </Badge>
                    <span className="font-body-md text-[12px] text-on-surface-variant">
                      {aviso.alcance === 'PorMateria' && aviso.materia_id
                        ? nombreMateria(aviso.materia_id)
                        : aviso.alcance === 'PorCohorte' && aviso.cohorte_id
                          ? nombreCohorte(aviso.cohorte_id)
                          : aviso.alcance === 'PorRol' && aviso.rol_destino
                            ? aviso.rol_destino
                            : aviso.alcance}
                    </span>
                    {aviso.requiere_ack && (
                      <span className="inline-flex rounded-full bg-[#E5D5F5] px-2 py-0.5 font-body-md text-[12px] font-medium text-[#4A148C]">
                        req. ack
                      </span>
                    )}
                    <span className="font-mono-data text-mono-data text-on-surface-variant">
                      acks: {aviso.total_acks}
                    </span>
                  </div>
                  <p className="font-headline-sm text-headline-sm text-on-surface">{aviso.titulo}</p>
                  <p className="mt-1 font-body-md text-body-md text-on-surface-variant">{aviso.cuerpo}</p>
                  <p className="mt-2 font-mono-data text-[12px] text-on-surface-variant">
                    {new Date(aviso.inicio_en).toLocaleString('es-AR')} →{' '}
                    {new Date(aviso.fin_en).toLocaleString('es-AR')}
                  </p>
                </div>
                <div className="ml-4 flex gap-2">
                  <Button
                    onClick={() => setEditando(aviso)}
                    variant="ghost"
                    size="sm"
                  >
                    Editar
                  </Button>
                  <Button
                    onClick={() => {
                      if (confirm('¿Eliminar este aviso?')) eliminar.mutate(aviso.id)
                    }}
                    variant="ghost"
                    size="sm"
                    className="!text-error hover:!bg-error/10"
                  >
                    Eliminar
                  </Button>
                </div>
              </BentoCard>
            ))}
        </div>
      )}
    </div>
  )
}
