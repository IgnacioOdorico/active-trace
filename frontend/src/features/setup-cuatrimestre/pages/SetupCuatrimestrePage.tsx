import { useState } from 'react'
import AsignacionMasivaForm from '../../equipos/components/AsignacionMasivaForm'
import ClonarEquipoForm from '../../equipos/components/ClonarEquipoForm'
import { VigenciaMasivaForm } from '../../equipos/components/VigenciaForm'
import AvisoForm from '../../avisos/components/AvisoForm'
import ProgramasStep from '../components/ProgramasStep'
import FechasAcademicasStep from '../components/FechasAcademicasStep'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

interface Step {
  id: string
  label: string
  description: string
  optional?: boolean
}

const STEPS: Step[] = [
  { id: 'clonar', label: '1. Clonar equipo', description: 'Clonar equipo docente del período anterior a la nueva cohorte.' },
  { id: 'asignacion', label: '2. Asignación masiva', description: 'Asignar docentes adicionales en bloque.', optional: true },
  { id: 'vigencias', label: '3. Vigencias', description: 'Ajustar las vigencias del equipo para el nuevo período.', optional: true },
  { id: 'programas', label: '4. Programas', description: 'Subir y asociar programas de materia para la cohorte.' },
  { id: 'fechas', label: '5. Fechas académicas', description: 'Registrar fechas de parciales, TPs y coloquios.' },
  { id: 'aviso', label: '6. Aviso de bienvenida', description: 'Publicar aviso de bienvenida para la nueva cohorte.', optional: true },
]

export default function SetupCuatrimestrePage() {
  const [pasoActual, setPasoActual] = useState(0)
  const [completados, setCompletados] = useState<Set<string>>(new Set())
  const [omitidos, setOmitidos] = useState<Set<string>>(new Set())

  const step = STEPS[pasoActual]
  const esUltimo = pasoActual === STEPS.length - 1

  const marcarCompletado = () => {
    setCompletados((prev) => new Set([...prev, step.id]))
    if (!esUltimo) setPasoActual((p) => p + 1)
  }

  const omitirPaso = () => {
    setOmitidos((prev) => new Set([...prev, step.id]))
    if (!esUltimo) setPasoActual((p) => p + 1)
  }

  const getEstadoPaso = (s: Step) => {
    if (completados.has(s.id)) return 'done'
    if (omitidos.has(s.id)) return 'skipped'
    return 'pending'
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="font-headline-md text-headline-md text-on-surface">Setup de Cuatrimestre</h1>
        <p className="mt-1 font-body-md text-on-surface-variant">
          Flujo guiado FL-03. Cada paso es independiente — podés omitir los opcionales y retomar
          más adelante. No hay transacción atómica: cada paso confirma su propio endpoint.
        </p>
      </div>

      {/* Barra de progreso */}
      <div className="flex items-center gap-2 overflow-x-auto pb-4">
        {STEPS.map((s, idx) => {
          const estado = getEstadoPaso(s)
          return (
            <div key={s.id} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPasoActual(idx)}
                className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                  idx === pasoActual
                    ? 'bg-primary text-on-primary'
                    : estado === 'done'
                    ? 'bg-success text-on-success'
                    : estado === 'skipped'
                    ? 'bg-surface-container-high text-on-surface-variant'
                    : 'bg-surface-container text-on-surface-variant'
                }`}
                title={s.label}
              >
                {estado === 'done' ? '✓' : estado === 'skipped' ? '–' : idx + 1}
              </button>
              {idx < STEPS.length - 1 && (
                <div className="h-[1px] w-8 flex-shrink-0 bg-outline-variant" />
              )}
            </div>
          )
        })}
      </div>

      {/* Paso actual */}
      <div className="rounded neo-latex-border bg-surface-container-lowest p-6">
        <div className="mb-6 flex items-start justify-between border-b border-outline-variant pb-4">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface">{step.label}</h2>
            <p className="mt-1 font-body-md text-on-surface-variant">{step.description}</p>
            {step.optional && (
              <div className="mt-2">
                <Badge variant="neutral">Opcional</Badge>
              </div>
            )}
          </div>
          {step.optional && (
            <Button
              onClick={omitirPaso}
              variant="ghost"
              className="text-on-surface-variant"
            >
              Omitir este paso →
            </Button>
          )}
        </div>

        {/* Contenido del paso */}
        {step.id === 'clonar' && (
          <ClonarEquipoForm onSuccess={marcarCompletado} />
        )}
        {step.id === 'asignacion' && (
          <AsignacionMasivaForm
            onSuccess={() => marcarCompletado()}
          />
        )}
        {step.id === 'vigencias' && (
          <VigenciaMasivaForm onSuccess={() => marcarCompletado()} />
        )}
        {step.id === 'programas' && (
          <div className="space-y-6">
            <ProgramasStep />
            <div className="flex justify-end pt-4 border-t border-outline-variant">
              <Button
                onClick={marcarCompletado}
                variant="primary"
              >
                Confirmar y continuar →
              </Button>
            </div>
          </div>
        )}
        {step.id === 'fechas' && (
          <div className="space-y-6">
            <FechasAcademicasStep />
            <div className="flex justify-end pt-4 border-t border-outline-variant">
              <Button
                onClick={marcarCompletado}
                variant="primary"
              >
                Confirmar y continuar →
              </Button>
            </div>
          </div>
        )}
        {step.id === 'aviso' && (
          <AvisoForm
            onSuccess={marcarCompletado}
            onCancel={omitirPaso}
          />
        )}
      </div>

      {/* Resumen final */}
      {(completados.size + omitidos.size === STEPS.length) && (
        <div className="rounded neo-latex-border bg-success-container p-6">
          <h3 className="font-headline-sm text-headline-sm text-on-success-container">Setup completado</h3>
          <p className="mt-2 font-body-md text-on-success-container">
            Completados: <span className="font-mono-data">{completados.size}</span> / <span className="font-mono-data">{STEPS.length}</span>. Omitidos: <span className="font-mono-data">{omitidos.size}</span>.
          </p>
          <p className="mt-1 font-body-md text-[12px] text-on-success-container/80">
            Podés volver a cualquier paso haciendo clic en los indicadores de progreso.
          </p>
        </div>
      )}
    </div>
  )
}
