import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import MisTareas from '../components/MisTareas'
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
  titulo: 'Revisar actas',
  descripcion: 'Verificar actas del primer parcial',
  estado: 'Pendiente',
  materia_id: 'm-1',
  materia_nombre: 'Matemática I',
  asignado_id: 'user-2',
  asignado_nombre: 'Juan Pérez',
  asignador_id: 'user-1',
  asignador_nombre: 'María García',
  creado_en: '2024-03-01T10:00:00',
  actualizado_en: '2024-03-01T10:00:00',
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('Workflow de estados', () => {
  it('renderiza el select de estado con los valores correctos', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { data: [TAREA_FIXTURE], total: 1 },
    })

    renderWithProviders(<MisTareas onVerDetalle={vi.fn()} />)

    const select = await screen.findByDisplayValue('Pendiente')
    expect(select).toBeInTheDocument()
    expect(select.tagName).toBe('SELECT')
  })

  it('llama PATCH /api/tareas/{id} al cambiar estado', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: { data: [TAREA_FIXTURE], total: 1 },
    })
    mockApiClient.patch.mockResolvedValueOnce({ data: { ...TAREA_FIXTURE, estado: 'En progreso' } })

    const user = userEvent.setup()
    renderWithProviders(<MisTareas onVerDetalle={vi.fn()} />)

    const select = await screen.findByDisplayValue('Pendiente')
    await user.selectOptions(select, 'En progreso')

    expect(mockApiClient.patch).toHaveBeenCalledWith(
      '/api/tareas/tarea-1',
      { estado: 'En progreso' },
    )
  })
})

describe('Hilo de comentarios', () => {
  it('renderiza comentarios existentes', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        data: [
          {
            id: 'c-1',
            tarea_id: 'tarea-1',
            autor_id: 'user-1',
            autor_nombre: 'María García',
            contenido: 'Por favor revisar el anexo',
            creado_en: '2024-03-01T11:00:00',
          },
        ],
        total: 1,
      },
    })

    renderWithProviders(<HiloComentarios tarea={TAREA_FIXTURE} onCerrar={vi.fn()} />)

    expect(await screen.findByText('Por favor revisar el anexo')).toBeInTheDocument()
    expect(screen.getByText('María García')).toBeInTheDocument()
  })

  it('llama POST /api/tareas/{id}/comentarios al agregar', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: { data: [], total: 0 } })
    mockApiClient.post.mockResolvedValueOnce({ data: { id: 'c-2', contenido: 'Nuevo comentario' } })

    const user = userEvent.setup()
    renderWithProviders(<HiloComentarios tarea={TAREA_FIXTURE} onCerrar={vi.fn()} />)

    const textarea = await screen.findByPlaceholderText(/Agregar comentario/i)
    await user.type(textarea, 'Nuevo comentario')
    await user.click(screen.getByRole('button', { name: /Enviar/i }))

    expect(mockApiClient.post).toHaveBeenCalledWith(
      '/api/tareas/tarea-1/comentarios',
      { contenido: 'Nuevo comentario' },
    )
  })
})
