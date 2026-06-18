import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import MisTareas from '../components/MisTareas'
import TareasAdmin from '../components/TareasAdmin'
import HiloComentarios from '../components/HiloComentarios'
import type { Tarea } from '../types'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

const TAREA_FIXTURE: Tarea = {
  id: 'tarea-1',
  descripcion: 'Verificar actas del primer parcial',
  estado: 'Pendiente',
  materia_id: 'm-1',
  asignado_a: 'user-2',
  asignado_por: 'user-1',
  created_at: '2024-03-01T10:00:00',
  updated_at: '2024-03-01T10:00:00',
}

const ASIGNABLES_FIXTURE = [
  { id: 'user-1', nombre: 'Diego', apellidos: 'Herrera', email: 'coordinador1@demo.local' },
  { id: 'user-2', nombre: 'Marina', apellidos: 'Suárez', email: 'profesor1@demo.local' },
]

const MATERIAS_FIXTURE = [{ id: 'm-1', nombre: 'Programación I' }]

function mockGetByUrl(routes: Record<string, unknown>) {
  const sorted = Object.entries(routes).sort((a, b) => b[0].length - a[0].length)
  mockApiClient.get.mockImplementation((url: string) => {
    for (const [path, data] of sorted) {
      if (url.includes(path)) return Promise.resolve({ data })
    }
    return Promise.resolve({ data: {} })
  })
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Workflow de estados', () => {
  it('renderiza el select de estado con los valores correctos', async () => {
    mockGetByUrl({
      '/api/tareas/mias': { items: [TAREA_FIXTURE], total: 1, pagina: 1, page_size: 50 },
      '/api/tareas/asignables': ASIGNABLES_FIXTURE,
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
    })

    renderWithProviders(<MisTareas onVerDetalle={vi.fn()} onEditar={vi.fn()} />)

    const select = await screen.findByDisplayValue('Pendiente')
    expect(select).toBeInTheDocument()
    expect(select.tagName).toBe('SELECT')
  })

  it('llama PATCH /api/tareas/{id} al cambiar estado', async () => {
    mockGetByUrl({
      '/api/tareas/mias': { items: [TAREA_FIXTURE], total: 1, pagina: 1, page_size: 50 },
      '/api/tareas/asignables': ASIGNABLES_FIXTURE,
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
    })
    mockApiClient.patch.mockResolvedValueOnce({ data: { ...TAREA_FIXTURE, estado: 'En progreso' } })

    const user = userEvent.setup()
    renderWithProviders(<MisTareas onVerDetalle={vi.fn()} onEditar={vi.fn()} />)

    const select = await screen.findByDisplayValue('Pendiente')
    await user.selectOptions(select, 'En progreso')

    expect(mockApiClient.patch).toHaveBeenCalledWith(
      '/api/tareas/tarea-1',
      { estado: 'En progreso' },
    )
  })

  it('resuelve asignado_por y materia_id a sus nombres reales', async () => {
    mockGetByUrl({
      '/api/tareas/mias': { items: [TAREA_FIXTURE], total: 1, pagina: 1, page_size: 50 },
      '/api/tareas/asignables': ASIGNABLES_FIXTURE,
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
    })

    renderWithProviders(<MisTareas onVerDetalle={vi.fn()} onEditar={vi.fn()} />)

    expect(await screen.findByText('Asignado por: Diego Herrera')).toBeInTheDocument()
    expect(screen.getByText('Materia: Programación I')).toBeInTheDocument()
    expect(screen.queryByText(/user-1/)).not.toBeInTheDocument()
  })
})

describe('TareasAdmin', () => {
  it('resuelve asignado_por y asignado_a a sus nombres reales', async () => {
    mockGetByUrl({
      '/api/tareas': { items: [TAREA_FIXTURE], total: 1, pagina: 1, page_size: 50 },
      '/api/tareas/asignables': ASIGNABLES_FIXTURE,
      '/api/v1/estructura/materias': MATERIAS_FIXTURE,
    })

    renderWithProviders(<TareasAdmin onVerDetalle={vi.fn()} onEditar={vi.fn()} />)

    expect(await screen.findByText('Diego Herrera → Marina Suárez')).toBeInTheDocument()
    expect(screen.queryByText(/user-1/)).not.toBeInTheDocument()
  })
})

describe('Hilo de comentarios', () => {
  it('renderiza comentarios existentes', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        items: [
          {
            id: 'c-1',
            tarea_id: 'tarea-1',
            autor_id: 'user-1',
            texto: 'Por favor revisar el anexo',
            creado_at: '2024-03-01T11:00:00',
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
    })

    renderWithProviders(<HiloComentarios tarea={TAREA_FIXTURE} onCerrar={vi.fn()} />)

    expect(await screen.findByText('Por favor revisar el anexo')).toBeInTheDocument()
    expect(screen.getByText('user-1')).toBeInTheDocument()
  })

  it('llama POST /api/tareas/{id}/comentarios al agregar', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: { items: [], total: 0, pagina: 1, page_size: 50 } })
    mockApiClient.post.mockResolvedValueOnce({ data: { id: 'c-2', texto: 'Nuevo comentario' } })

    const user = userEvent.setup()
    renderWithProviders(<HiloComentarios tarea={TAREA_FIXTURE} onCerrar={vi.fn()} />)

    const textarea = await screen.findByPlaceholderText(/Agregar comentario/i)
    await user.type(textarea, 'Nuevo comentario')
    await user.click(screen.getByRole('button', { name: /Enviar/i }))

    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/api/tareas/tarea-1/comentarios',
      { texto: 'Nuevo comentario' },
    )
  })
})
