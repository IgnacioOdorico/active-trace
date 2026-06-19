import { useState } from 'react'
import MisEquipos from '../components/MisEquipos'
import AsignacionMasivaForm from '../components/AsignacionMasivaForm'
import ClonarEquipoForm from '../components/ClonarEquipoForm'
import { VigenciaIndividualForm, VigenciaMasivaForm } from '../components/VigenciaForm'
import type { MiEquipo } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'

type Panel = 'listado' | 'asignacion' | 'clonar' | 'vigencia-masiva'

export default function EquiposPage() {
  const [panel, setPanel] = useState<Panel>('listado')
  const [equipoVigencia, setEquipoVigencia] = useState<MiEquipo | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const handleVigenciaOpen = (equipo: MiEquipo) => {
    setEquipoVigencia(equipo)
  }

  const handleVigenciaClose = () => {
    setEquipoVigencia(null)
    setSuccessMsg('Vigencia actualizada correctamente.')
    setTimeout(() => setSuccessMsg(null), 3000)
  }

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-headline-md text-headline-md text-on-surface">Equipos Docentes</h1>
        <div className="flex gap-2">
          <Button
            onClick={() => setPanel('listado')}
            variant={panel === 'listado' ? 'primary' : 'ghost'}
          >
            Mis Equipos
          </Button>
          <Button
            onClick={() => setPanel('asignacion')}
            variant={panel === 'asignacion' ? 'primary' : 'ghost'}
          >
            Asignación Masiva
          </Button>
          <Button
            onClick={() => setPanel('clonar')}
            variant={panel === 'clonar' ? 'primary' : 'ghost'}
          >
            Clonar Equipo
          </Button>
          <Button
            onClick={() => setPanel('vigencia-masiva')}
            variant={panel === 'vigencia-masiva' ? 'primary' : 'ghost'}
          >
            Vigencia Masiva
          </Button>
        </div>
      </div>

      {successMsg && (
        <div className="mb-6 rounded neo-latex-border bg-[#d4edda] p-4 font-body-md text-[#155724]">
          {successMsg}
        </div>
      )}

      <BentoCard>
        {panel === 'listado' && (
          <MisEquipos onVigencia={handleVigenciaOpen} />
        )}
        {panel === 'asignacion' && (
          <div>
            <h2 className="mb-4 font-label-caps text-label-caps text-on-surface-variant uppercase">Asignación Masiva</h2>
            <AsignacionMasivaForm
              onSuccess={(ids) => {
                setSuccessMsg(`${ids.length} asignaciones creadas.`)
                setPanel('listado')
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
        {panel === 'clonar' && (
          <div>
            <h2 className="mb-4 font-label-caps text-label-caps text-on-surface-variant uppercase">Clonar Equipo</h2>
            <ClonarEquipoForm
              onSuccess={() => {
                setSuccessMsg('Equipo clonado correctamente.')
                setPanel('listado')
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
        {panel === 'vigencia-masiva' && (
          <div>
            <h2 className="mb-4 font-label-caps text-label-caps text-on-surface-variant uppercase">Modificar Vigencia Masiva</h2>
            <VigenciaMasivaForm
              onSuccess={(filas) => {
                setSuccessMsg(`${filas} fila(s) afectada(s).`)
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
      </BentoCard>

      {equipoVigencia && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <BentoCard className="w-full max-w-md shadow-xl" title="Modificar Vigencia" action={
            <button
              onClick={() => setEquipoVigencia(null)}
              className="material-symbols-outlined text-outline hover:text-on-surface"
            >
              close
            </button>
          }>
            <VigenciaIndividualForm equipo={equipoVigencia} onSuccess={handleVigenciaClose} />
          </BentoCard>
        </div>
      )}
    </div>
  )
}
