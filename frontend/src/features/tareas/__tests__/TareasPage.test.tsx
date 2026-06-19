import { screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import TareasPage from '../pages/TareasPage'

const mockUseAuth = vi.fn()
vi.mock('../../auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}))

vi.mock('../components/MisTareas', () => ({
  default: () => <div>Mis Tareas (contenido)</div>,
}))
vi.mock('../components/TareasAdmin', () => ({
  default: () => <div>Administración Global (contenido)</div>,
}))

describe('TareasPage — visibilidad según permiso', () => {
  it('PROFESOR con permiso (propio) NO ve la pestaña ni el contenido de Administración Global', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'profesor-1', permissions: ['tareas:gestionar(propio)'] },
      logout: vi.fn(),
    })

    renderWithProviders(<TareasPage />)

    expect(screen.getByText('Mis Tareas (contenido)')).toBeInTheDocument()
    expect(screen.queryByText('Administración Global')).not.toBeInTheDocument()
    expect(screen.queryByText('Administración Global (contenido)')).not.toBeInTheDocument()
  })

  it('COORDINADOR con permiso full SÍ ve ambas pestañas', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'coordinador-1', permissions: ['tareas:gestionar'] },
      logout: vi.fn(),
    })

    renderWithProviders(<TareasPage />)

    expect(screen.getByText('Mis Tareas (contenido)')).toBeInTheDocument()
    expect(screen.getByText('Administración Global')).toBeInTheDocument()
  })
})
