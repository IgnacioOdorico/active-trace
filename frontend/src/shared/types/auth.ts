export interface User {
  id: string
  email: string
  nombre: string
  roles: string[]
  permissions: string[]
  tenant_id: string
}

export type AuthState = 'loading' | 'authenticated' | 'unauthenticated'
