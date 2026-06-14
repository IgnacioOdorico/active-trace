import { useState } from 'react'
import AsignacionMasivaForm from '../../equipos/components/AsignacionMasivaForm'
import ClonarEquipoForm from '../../equipos/components/ClonarEquipoForm'
import { VigenciaMasivaForm } from '../../equipos/components/VigenciaForm'
import AvisoForm from '../../avisos/components/AvisoForm'
import ProgramasStep from '../components/ProgramasStep'
import FechasAcademicasStep from '../components/FechasAcademicasStep'

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
    <div className="mx-auto max-w-4xl py-8">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">Setup de Cuatrimestre</h1>
      <p className="mb-6 text-sm text-gray-500">
        Flujo guiado FL-03. Cada paso es independiente — podés omitir los opcionales y retomar
        más adelante. No hay transacción atómica: cada paso confirma su propio endpoint.
      </p>

      {/* Barra de progreso */}
      <div className="mb-8 flex items-center gap-2 overflow-x-auto pb-2">
        {STEPS.map((s, idx) => {
          const estado = getEstadoPaso(s)
          return (
            <div key={s.id} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setPasoActual(idx)}
                className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                  idx === pasoActual
                    ? 'bg-blue-600 text-white'
                    : estado === 'done'
                    ? 'bg-green-500 text-white'
                    : estado === 'skipped'
                    ? 'bg-gray-300 text-gray-600'
                    : 'bg-gray-100 text-gray-500'
                }`}
                title={s.label}
              >
                {estado === 'done' ? '✓' : estado === 'skipped' ? '–' : idx + 1}
              </button>
              {idx < STEPS.length - 1 && (
                <div className="h-0.5 w-6 flex-shrink-0 bg-gray-200" />
              )}
            </div>
          )
        })}
      </div>

      {/* Paso actual */}
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{step.label}</h2>
            <p className="mt-1 text-sm text-gray-500">{step.description}</p>
            {step.optional && (
              <span className="mt-1 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                Opcional
              </span>
            )}
          </div>
          {step.optional && (
            <button
              type="button"
              onClick={omitirPaso}
              className="text-sm text-gray-400 hover:text-gray-600 hover:underline"
            >
              Omitir este paso →
            </button>
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
          <div>
            <ProgramasStep />
            <div className="mt-4">
              <button
                type="button"
                onClick={marcarCompletado}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Confirmar y continuar →
              </button>
            </div>
          </div>
        )}
        {step.id === 'fechas' && (
          <div>
            <FechasAcademicasStep />
            <div className="mt-4">
              <button
                type="button"
                onClick={marcarCompletado}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Confirmar y continuar →
              </button>
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
        <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-6">
          <h3 className="font-semibold text-green-900">Setup completado</h3>
          <p className="mt-1 text-sm text-green-700">
            Completados: {completados.size} / {STEPS.length}. Omitidos: {omitidos.size}.
          </p>
          <p className="mt-1 text-xs text-green-600">
            Podés volver a cualquier paso haciendo clic en los indicadores de progreso.
          </p>
        </div>
      )}
    </div>
  )
}
