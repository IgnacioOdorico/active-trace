import { useState } from 'react'
import MetricasColoquios from '../components/MetricasColoquios'
import ListadoConvocatorias from '../components/ListadoConvocatorias'
import ConvocatoriaForm from '../components/ConvocatoriaForm'
import EditarConvocatoriaForm from '../components/EditarConvocatoriaForm'
import ImportarAlumnosForm from '../components/ImportarAlumnosForm'
import type { Convocatoria } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'

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
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Coloquios</h1>
        {vista === 'listado' && (
          <Button
            onClick={() => setVista('crear')}
            variant="primary"
          >
            + Nueva convocatoria
          </Button>
        )}
        {vista !== 'listado' && (
          <Button
            onClick={handleBack}
            variant="ghost"
          >
            ← Volver al listado
          </Button>
        )}
      </div>

      {vista === 'listado' && (
        <>
          <div className="mb-6">
            <h2 className="mb-4 font-headline-sm text-headline-sm text-on-surface">Métricas generales</h2>
            <MetricasColoquios />
          </div>
          <BentoCard>
            <h2 className="mb-6 font-headline-sm text-headline-sm text-on-surface">Convocatorias</h2>
            <ListadoConvocatorias onEditar={handleEditar} onImportar={handleImportar} />
          </BentoCard>
        </>
      )}

      {vista === 'crear' && (
        <BentoCard>
          <h2 className="mb-6 font-headline-sm text-headline-sm text-on-surface">Nueva Convocatoria</h2>
          <ConvocatoriaForm onSuccess={handleBack} onCancel={handleBack} />
        </BentoCard>
      )}

      {vista === 'editar' && convocatoriaActual && (
        <BentoCard>
          <h2 className="mb-6 font-headline-sm text-headline-sm text-on-surface">
            Editar Convocatoria — {convocatoriaActual.instancia}
          </h2>
          <EditarConvocatoriaForm
            convocatoria={convocatoriaActual}
            onSuccess={handleBack}
            onCancel={handleBack}
          />
        </BentoCard>
      )}

      {vista === 'importar' && convocatoriaImportarId && (
        <BentoCard>
          <h2 className="mb-6 font-headline-sm text-headline-sm text-on-surface">Importar Alumnos</h2>
          <ImportarAlumnosForm
            convocatoriaId={convocatoriaImportarId}
            onSuccess={handleBack}
            onCancel={handleBack}
          />
        </BentoCard>
      )}
    </div>
  )
}
