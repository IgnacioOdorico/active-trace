import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import UsuariosListado from '../components/UsuariosListado'
import UsuarioForm from '../components/UsuarioForm'
import type { Usuario } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'

export default function UsuariosPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeGestionar = perms.includes('*:*') || perms.includes('usuarios:gestionar')

  const [editando, setEditando] = useState<Usuario | null | 'nuevo'>(null)

  if (!puedeGestionar) {
    return (
      <BentoCard>
        <div className="rounded bg-error-container p-6 text-center font-body-md text-on-error-container">
          Acceso denegado. No tenés el permiso <code>usuarios:gestionar</code>.
        </div>
      </BentoCard>
    )
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Usuarios del Tenant</h1>
        <Button
          onClick={() => setEditando('nuevo')}
          variant="primary"
        >
          <span className="material-symbols-outlined mr-1 text-[18px]">add</span>
          Nuevo usuario
        </Button>
      </div>

      {editando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <BentoCard className="w-full max-w-md shadow-xl" title={editando === 'nuevo' ? 'Nuevo usuario' : `Editar: ${(editando as Usuario).email}`} action={
            <button
              onClick={() => setEditando(null)}
              className="material-symbols-outlined text-outline hover:text-on-surface"
            >
              close
            </button>
          }>
            <UsuarioForm
              usuario={editando === 'nuevo' ? null : (editando as Usuario)}
              onSuccess={() => setEditando(null)}
            />
            <div className="mt-4 flex justify-end">
              <Button
                onClick={() => setEditando(null)}
                variant="ghost"
              >
                Cancelar
              </Button>
            </div>
          </BentoCard>
        </div>
      )}

      <BentoCard>
        <UsuariosListado
          puedeGestionar={puedeGestionar}
          onEditar={(u) => setEditando(u)}
        />
      </BentoCard>
    </div>
  )
}
