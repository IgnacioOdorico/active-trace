import { useState } from 'react'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCalificacionesApi } from '../hooks/useCalificacionesApi'
import PreviewTable from '../components/PreviewTable'
import type { CalificacionPreviewResponse, ImportarResultado } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

type WizardStep = 'select' | 'loading' | 'preview' | 'importing' | 'result' | 'error' | 'empty'

export default function CalificacionesImportarPage() {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { preview, importar } = useCalificacionesApi()

  const [step, setStep] = useState<WizardStep>('select')
  const [materiaId, setMateriaId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [previewData, setPreviewData] = useState<CalificacionPreviewResponse | null>(null)
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [resultado, setResultado] = useState<ImportarResultado | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [advertenciasOpen, setAdvertenciasOpen] = useState(false)

  const materiaNombre = materias?.find((m) => m.id === materiaId)?.nombre ?? ''

  async function handlePreview() {
    if (!materiaId || !file) return
    setStep('loading')
    setErrorMessage(null)
    try {
      const data = await preview.mutateAsync({ materia_id: materiaId, file })
      setPreviewData(data)
      if (data.actividades.length === 0) {
        setStep('empty')
      } else {
        setSelectedIds(data.actividades.map((a) => a.nombre))
        setStep('preview')
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Error al procesar el archivo'
      setErrorMessage(message)
      setStep('error')
    }
  }

  async function handleImportar() {
    if (!materiaId || selectedIds.length === 0 || !file) return
    setStep('importing')
    try {
      const data = await importar.mutateAsync({
        materia_id: materiaId,
        actividades: selectedIds,
        file,
      })
      setResultado(data)
      setStep('result')
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Error al importar calificaciones'
      setErrorMessage(message)
      setStep('error')
    }
  }

  function handleReset() {
    setStep('select')
    setFile(null)
    setPreviewData(null)
    setSelectedIds([])
    setResultado(null)
    setErrorMessage(null)
    setAdvertenciasOpen(false)
  }

  if (step === 'loading' || step === 'importing') {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <span className="material-symbols-outlined text-primary text-4xl animate-spin">refresh</span>
        <p className="mt-4 font-body-md text-on-surface-variant">
          {step === 'loading' ? 'Procesando archivo...' : 'Importando calificaciones...'}
        </p>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="mx-auto max-w-2xl">
        <BentoCard title="Importar Calificaciones">
          <div className="rounded bg-error-container p-4 mb-6">
            <p className="font-body-md text-on-error-container">{errorMessage}</p>
          </div>
          <Button onClick={handleReset} variant="ghost">Volver a intentar</Button>
        </BentoCard>
      </div>
    )
  }

  if (step === 'empty') {
    return (
      <div className="mx-auto max-w-2xl">
        <BentoCard title="Importar Calificaciones">
          <div className="rounded bg-tertiary-container p-4 mb-6">
            <p className="font-body-md text-on-tertiary-container">
              No se detectaron actividades evaluables en el archivo.
            </p>
          </div>
          <Button onClick={handleReset} variant="ghost">Subir otro archivo</Button>
        </BentoCard>
      </div>
    )
  }

  if (step === 'result' && resultado) {
    return (
      <div className="mx-auto max-w-3xl">
        <BentoCard title="Importar Calificaciones">
          <div className="rounded neo-latex-border bg-surface-container-low p-4 mb-6">
            <p className="font-body-md text-on-surface">
              <span className="font-bold">{resultado.insertadas}</span> calificaciones insertadas
              {resultado.actualizadas > 0 && `, ${resultado.actualizadas} actualizadas`}
            </p>
          </div>

          {resultado.advertencias.length > 0 && (
            <div className="mb-6 rounded neo-latex-border bg-tertiary-container overflow-hidden">
              <button
                onClick={() => setAdvertenciasOpen(!advertenciasOpen)}
                className="flex w-full items-center justify-between px-4 py-3 font-label-caps text-label-caps uppercase text-on-tertiary-container hover:bg-opacity-90"
              >
                <span>{resultado.advertencias.length} advertencia(s)</span>
                <span className="material-symbols-outlined">{advertenciasOpen ? 'expand_less' : 'expand_more'}</span>
              </button>

              {advertenciasOpen && (
                <div className="border-t border-outline-variant px-4 py-2 bg-surface">
                  <ul className="space-y-1">
                    {resultado.advertencias.map((adv, i) => (
                      <li key={i} className="font-mono-data text-mono-data text-on-surface-variant">
                        Fila {adv.fila}: {adv.motivo}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <Button onClick={handleReset} variant="primary">Importar otro archivo</Button>
        </BentoCard>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-headline-md text-headline-md text-on-surface mb-8">
        Importar Calificaciones
      </h1>

      <div className="space-y-6">
        <BentoCard title="Selección de Archivo">
          <div className="space-y-6">
            <div>
              <label
                htmlFor="materia"
                className="block font-label-caps text-label-caps text-on-surface-variant uppercase mb-2"
              >
                Materia
              </label>
              <select
                id="materia"
                value={materiaId}
                onChange={(e) => setMateriaId(e.target.value)}
                className="block w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none"
              >
                <option value="">Seleccione una materia</option>
                {materiasLoading && (
                  <option value="" disabled>Cargando materias...</option>
                )}
                {materias?.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nombre}
                    {m.comision ? ` - ${m.comision}` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="file"
                className="block font-label-caps text-label-caps text-on-surface-variant uppercase mb-2"
              >
                Archivo (.xlsx o .csv)
              </label>
              <input
                id="file"
                type="file"
                accept=".xlsx,.csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="block w-full font-body-md text-on-surface-variant file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:font-label-caps file:text-label-caps file:uppercase file:bg-surface-container-high file:text-on-surface hover:file:bg-surface-container"
              />
            </div>

            <Button
              onClick={handlePreview}
              disabled={!materiaId || !file}
              variant="primary"
            >
              Vista Previa
            </Button>
          </div>
        </BentoCard>

        {step === 'preview' && previewData && (
          <BentoCard title="Vista Previa de Actividades">
            <div className="space-y-6">
              <PreviewTable
                actividades={previewData.actividades}
                selectedIds={selectedIds}
                onSelectionChange={setSelectedIds}
                materiaNombre={materiaNombre}
                totalFilas={previewData.total_filas}
              />

              <Button
                onClick={handleImportar}
                disabled={selectedIds.length === 0}
                variant="primary"
                className="w-full sm:w-auto"
              >
                Importar Seleccionadas ({selectedIds.length})
              </Button>
            </div>
          </BentoCard>
        )}
      </div>
    </div>
  )
}
