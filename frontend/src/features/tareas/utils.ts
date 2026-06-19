import type { UsuarioAsignable } from './types'

export function formatNombreUsuario(u: UsuarioAsignable): string {
  return [u.nombre, u.apellidos].filter(Boolean).join(' ') || u.email
}
