import { useState } from 'react'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCalificacionesApi } from '../hooks/useCalificacionesApi'
import PreviewTable from '../components/PreviewTable'
import type { CalificacionPreviewResponse, ImportarResultado } from '../types'

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

  const materiaNombre =
    previewData?.materia_nombre ??
    materias?.find((m) => m.id === materiaId)?.nombre ??
    ''

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
        setSelectedIds(data.actividades.map((a) => a.id))
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
    if (!materiaId || selectedIds.length === 0) return
    setStep('importing')
    try {
      const data = await importar.mutateAsync({
        materia_id: materiaId,
        actividad_ids: selectedIds,
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

  if (step === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-sm text-gray-600">Procesando archivo...</p>
      </div>
    )
  }

  if (step === 'importing') {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-sm text-gray-600">Importando calificaciones...</p>
      </div>
    )
  }

  if (step === 'error') {
    return (
      <div className="mx-auto max-w-2xl py-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Importar Calificaciones
        </h1>

        <div className="mt-6 rounded-md bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">{errorMessage}</p>
        </div>

        <button
          onClick={handleReset}
          className="mt-4 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
        >
          Volver a intentar
        </button>
      </div>
    )
  }

  if (step === 'empty') {
    return (
      <div className="mx-auto max-w-2xl py-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Importar Calificaciones
        </h1>

        <div className="mt-6 rounded-md bg-yellow-50 p-4">
          <p className="text-sm font-medium text-yellow-800">
            No se detectaron actividades evaluables en el archivo.
          </p>
        </div>

        <button
          onClick={handleReset}
          className="mt-4 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
        >
          Subir otro archivo
        </button>
      </div>
    )
  }

  if (step === 'result' && resultado) {
    return (
      <div className="mx-auto max-w-3xl py-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Importar Calificaciones
        </h1>

        <div className="mt-6 rounded-md border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">
            {resultado.insertadas} calificaciones insertadas
            {resultado.actualizadas > 0 && `, ${resultado.actualizadas} actualizadas`}
          </p>
        </div>

        {resultado.advertencias.length > 0 && (
          <div className="mt-4 rounded-md border border-yellow-200 bg-yellow-50">
            <button
              onClick={() => setAdvertenciasOpen(!advertenciasOpen)}
              className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium text-yellow-800"
            >
              <span>
                {resultado.advertencias.length} advertencia(s)
              </span>
              <span>{advertenciasOpen ? '▲' : '▼'}</span>
            </button>

            {advertenciasOpen && (
              <div className="border-t border-yellow-200 px-4 py-2">
                <ul className="space-y-1">
                  {resultado.advertencias.map((adv, i) => (
                    <li key={i} className="text-sm text-yellow-700">
                      Fila {adv.fila}: {adv.motivo}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleReset}
          className="mt-6 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Importar otro archivo
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">
        Importar Calificaciones
      </h1>

      <div className="mt-6 space-y-6">
        <div>
          <label
            htmlFor="materia"
            className="block text-sm font-medium text-gray-700"
          >
            Materia
          </label>
          <select
            id="materia"
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Seleccione una materia</option>
            {materiasLoading && (
              <option value="" disabled>
                Cargando materias...
              </option>
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
            className="block text-sm font-medium text-gray-700"
          >
            Archivo (.xlsx o .csv)
          </label>
          <input
            id="file"
            type="file"
            accept=".xlsx,.csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:rounded-md file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <button
          onClick={handlePreview}
          disabled={!materiaId || !file}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Vista Previa
        </button>
      </div>

      {step === 'preview' && previewData && (
        <div className="mt-8 space-y-4">
          <PreviewTable
            actividades={previewData.actividades}
            selectedIds={selectedIds}
            onSelectionChange={setSelectedIds}
            materiaNombre={materiaNombre}
            totalFilas={previewData.total_filas}
          />

          <button
            onClick={handleImportar}
            disabled={selectedIds.length === 0}
            className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Importar Seleccionadas ({selectedIds.length})
          </button>
        </div>
      )}
    </div>
  )
}
