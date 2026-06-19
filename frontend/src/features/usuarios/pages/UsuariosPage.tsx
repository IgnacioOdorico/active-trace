import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import UsuariosListado from '../components/UsuariosListado'
import UsuarioForm from '../components/UsuarioForm'
import type { Usuario } from '../types'

export default function UsuariosPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeGestionar = perms.includes('*:*') || perms.includes('usuarios:gestionar')

  const [editando, setEditando] = useState<Usuario | null | 'nuevo'>(null)

  if (!puedeGestionar) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso <code>usuarios:gestionar</code>.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Usuarios del Tenant</h1>
        <button
          onClick={() => setEditando('nuevo')}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + Nuevo usuario
        </button>
      </div>

      {editando && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">
            {editando === 'nuevo' ? 'Nuevo usuario' : `Editar: ${(editando as Usuario).email}`}
          </h2>
          <UsuarioForm
            usuario={editando === 'nuevo' ? null : (editando as Usuario)}
            onSuccess={() => setEditando(null)}
          />
          <div className="mt-2 flex justify-start">
            <button
              onClick={() => setEditando(null)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <UsuariosListado
        puedeGestionar={puedeGestionar}
        onEditar={(u) => setEditando(u)}
      />
    </div>
  )
}
