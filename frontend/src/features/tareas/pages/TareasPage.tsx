import { useState } from 'react'
import MisTareas from '../components/MisTareas'
import TareasAdmin from '../components/TareasAdmin'
import CrearTareaForm from '../components/CrearTareaForm'
import EditarTareaForm from '../components/EditarTareaForm'
import HiloComentarios from '../components/HiloComentarios'
import type { Tarea } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { useAuth } from '../../auth/hooks/useAuth'
import { hasPermission } from '../../../shared/utils/permissions'

type Tab = 'mis-tareas' | 'admin'

export default function TareasPage() {
  const { user } = useAuth()
  const puedeGestionarTodas = hasPermission(user?.permissions ?? [], 'tareas:gestionar')
  const [tab, setTab] = useState<Tab>('mis-tareas')
  const [creando, setCreando] = useState(false)
  const [tareaDetalle, setTareaDetalle] = useState<Tarea | null>(null)
  const [tareaEditando, setTareaEditando] = useState<Tarea | null>(null)

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Tareas</h1>
        <Button
          onClick={() => setCreando(true)}
          variant="primary"
        >
          + Nueva tarea
        </Button>
      </div>

      {puedeGestionarTodas && (
        <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
          <Button
            onClick={() => setTab('mis-tareas')}
            variant={tab === 'mis-tareas' ? 'primary' : 'ghost'}
          >
            Mis Tareas
          </Button>
          <Button
            onClick={() => setTab('admin')}
            variant={tab === 'admin' ? 'primary' : 'ghost'}
          >
            Administración Global
          </Button>
        </div>
      )}

      <div className="rounded neo-latex-border bg-surface-container-lowest p-6">
        {(tab === 'mis-tareas' || !puedeGestionarTodas) && (
          <MisTareas onVerDetalle={setTareaDetalle} onEditar={setTareaEditando} />
        )}
        {tab === 'admin' && puedeGestionarTodas && (
          <TareasAdmin onVerDetalle={setTareaDetalle} onEditar={setTareaEditando} />
        )}
      </div>

      {creando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-scrim/40 backdrop-blur-sm">
          <div className="w-full max-w-lg">
            <BentoCard>
              <div className="mb-4 flex items-center justify-between border-b border-outline-variant pb-4">
                <h2 className="font-headline-sm text-headline-sm text-on-surface">Nueva Tarea</h2>
                <button
                  type="button"
                  onClick={() => setCreando(false)}
                  className="text-on-surface-variant hover:text-on-surface transition-colors"
                >
                  ✕
                </button>
              </div>
              <CrearTareaForm
                onSuccess={() => setCreando(false)}
                onCancel={() => setCreando(false)}
                asignadoFijo={puedeGestionarTodas ? undefined : user?.id}
              />
            </BentoCard>
          </div>
        </div>
      )}

      {tareaDetalle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-scrim/40 backdrop-blur-sm">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <BentoCard>
              <HiloComentarios
                tarea={tareaDetalle}
                onCerrar={() => setTareaDetalle(null)}
              />
            </BentoCard>
          </div>
        </div>
      )}

      {tareaEditando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-scrim/40 backdrop-blur-sm">
          <div className="w-full max-w-lg">
            <BentoCard>
              <div className="mb-4 flex items-center justify-between border-b border-outline-variant pb-4">
                <h2 className="font-headline-sm text-headline-sm text-on-surface">Editar Tarea</h2>
                <button
                  type="button"
                  onClick={() => setTareaEditando(null)}
                  className="text-on-surface-variant hover:text-on-surface transition-colors"
                >
                  ✕
                </button>
              </div>
              <EditarTareaForm
                tarea={tareaEditando}
                onSuccess={() => setTareaEditando(null)}
                onCancel={() => setTareaEditando(null)}
              />
            </BentoCard>
          </div>
        </div>
      )}
    </div>
  )
}
