import { describe, it, expect } from 'vitest'
import { hasPermission, hasAllPermissions } from '../permissions'

describe('hasPermission', () => {
  it('matches an exact permission code', () => {
    expect(hasPermission(['calificaciones:importar'], 'calificaciones:importar')).toBe(true)
  })

  it('matches via module wildcard (ej. calificaciones:*)', () => {
    expect(hasPermission(['calificaciones:*'], 'calificaciones:importar')).toBe(true)
  })

  it('matches via full wildcard *:*', () => {
    expect(hasPermission(['*:*'], 'usuarios:gestionar')).toBe(true)
  })

  it('no matchea entre módulos distintos', () => {
    expect(hasPermission(['atrasados:ver'], 'calificaciones:importar')).toBe(false)
  })

  it('no matchea entre acciones distintas del mismo módulo', () => {
    expect(hasPermission(['tareas:gestionar'], 'tareas:eliminar')).toBe(false)
  })

  it('un permiso (propio) NO satisface un requerimiento sin (propio)', () => {
    expect(hasPermission(['tareas:gestionar(propio)'], 'tareas:gestionar')).toBe(false)
  })

  it('un permiso sin (propio) SÍ satisface un requerimiento (propio)', () => {
    expect(hasPermission(['encuentros:gestionar'], 'encuentros:gestionar(propio)')).toBe(true)
  })

  it('devuelve false con lista de permisos vacía', () => {
    expect(hasPermission([], 'calificaciones:importar')).toBe(false)
  })

  it('no rompe con códigos sin formato modulo:accion', () => {
    expect(hasPermission(['basic.access'], 'admin.access')).toBe(false)
    expect(hasPermission(['basic.access'], 'basic.access')).toBe(true)
  })
})

describe('hasAllPermissions', () => {
  it('requiere que se cumplan todos los permisos pedidos', () => {
    const perms = ['calificaciones:*', 'atrasados:ver']
    expect(hasAllPermissions(perms, ['calificaciones:importar', 'atrasados:ver'])).toBe(true)
    expect(hasAllPermissions(perms, ['calificaciones:importar', 'usuarios:gestionar'])).toBe(false)
  })
})
