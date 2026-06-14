import { useState } from 'react'
import MetricasColoquios from '../components/MetricasColoquios'
import ListadoConvocatorias from '../components/ListadoConvocatorias'
import ConvocatoriaForm from '../components/ConvocatoriaForm'
import ImportarAlumnosForm from '../components/ImportarAlumnosForm'
import type { Convocatoria } from '../types'

type Vista = 'listado' | 'crear' | 'editar' | 'importar'

export default function ColoquiosPage() {
  const [vista, setVista] = useState<Vista>('listado')
  const [convocatoriaActual, setConvocatoriaActual] = useState<Convocatoria | null>(null)
  const [convocatoriaImportarId, setConvocatoriaImportarId] = useState<string | null>(null)

  const handleEditar = (conv: Convocatoria) => {
    setConvocatoriaActual(conv)
    setVista('editar')
  }

  const handleImportar = (convId: string) => {
    setConvocatoriaImportarId(convId)
    setVista('importar')
  }

  const handleBack = () => {
    setVista('listado')
    setConvocatoriaActual(null)
    setConvocatoriaImportarId(null)
  }

  return (
    <div className="mx-auto max-w-7xl py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Coloquios</h1>
        {vista === 'listado' && (
          <button
            type="button"
            onClick={() => setVista('crear')}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Nueva convocatoria
          </button>
        )}
        {vista !== 'listado' && (
          <button
            type="button"
            onClick={handleBack}
            className="text-sm text-gray-600 hover:underline"
          >
            ← Volver al listado
          </button>
        )}
      </div>

      {vista === 'listado' && (
        <>
          <div className="mb-6">
            <h2 className="mb-3 text-lg font-semibold text-gray-800">Métricas generales</h2>
            <MetricasColoquios />
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-800">Convocatorias</h2>
            <ListadoConvocatorias onEditar={handleEditar} onImportar={handleImportar} />
          </div>
        </>
      )}

      {vista === 'crear' && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-800">Nueva Convocatoria</h2>
          <ConvocatoriaForm onSuccess={handleBack} onCancel={handleBack} />
        </div>
      )}

      {vista === 'editar' && convocatoriaActual && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-800">
            Editar Convocatoria — {convocatoriaActual.materia_nombre}
          </h2>
          <ConvocatoriaForm
            convocatoria={convocatoriaActual}
            onSuccess={handleBack}
            onCancel={handleBack}
          />
        </div>
      )}

      {vista === 'importar' && convocatoriaImportarId && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-800">Importar Alumnos</h2>
          <ImportarAlumnosForm
            convocatoriaId={convocatoriaImportarId}
            onSuccess={handleBack}
            onCancel={handleBack}
          />
        </div>
      )}
    </div>
  )
}
