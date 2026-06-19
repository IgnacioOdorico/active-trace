import { screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import AvisosPage from '../pages/AvisosPage'

const mockUseAuth = vi.fn()
vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock('../components/AvisosUsuario', () => ({
  default: () => <div>Mis avisos (contenido)</div>,
}))
vi.mock('../components/GestionAvisos', () => ({
  default: () => <div>Gestion (contenido)</div>,
}))

describe('AvisosPage — visibilidad según permiso', () => {
  it('ALUMNO sin avisos:publicar solo ve sus propios avisos, sin pestañas', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'alumno-1', permissions: ['coloquios:reservar', 'mensajes:*(propio)', 'perfil:ver(propio)'] },
      logout: vi.fn(),
    })

    renderWithProviders(<AvisosPage />)

    expect(screen.getByText('Mis avisos (contenido)')).toBeInTheDocument()
    expect(screen.queryByText('Gestión')).not.toBeInTheDocument()
    expect(screen.queryByText('Gestion (contenido)')).not.toBeInTheDocument()
  })

  it('COORDINADOR con avisos:publicar ve ambas pestañas', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'coordinador-1', permissions: ['avisos:publicar'] },
      logout: vi.fn(),
    })

    renderWithProviders(<AvisosPage />)

    expect(screen.getByText('Mis avisos (contenido)')).toBeInTheDocument()
    expect(screen.getByText('Gestión')).toBeInTheDocument()
  })
})
