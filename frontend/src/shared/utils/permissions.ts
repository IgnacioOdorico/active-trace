function parsePermCodigo(codigo: string): { modulo: string; accion: string; propio: boolean } {
  const [modulo, accionRaw = ''] = codigo.split(':', 2)
  const propio = accionRaw.includes('(propio)')
  const accion = accionRaw.replace('(propio)', '')
  return { modulo, accion, propio }
}

function matchPermission(required: string, userPerm: string): boolean {
  const req = parsePermCodigo(required)
  const usr = parsePermCodigo(userPerm)

  if (usr.modulo !== '*' && usr.modulo !== req.modulo) return false
  if (usr.accion !== '*' && usr.accion !== req.accion) return false
  if (usr.propio && !req.propio) return false

  return true
}

export function hasPermission(userPermissions: string[], required: string): boolean {
  return userPermissions.some((perm) => matchPermission(required, perm))
}

export function hasAllPermissions(userPermissions: string[], required: string[]): boolean {
  return required.every((perm) => hasPermission(userPermissions, perm))
}
