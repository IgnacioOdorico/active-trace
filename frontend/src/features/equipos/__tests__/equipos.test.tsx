import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import MisEquipos from '../components/MisEquipos'
import ClonarEquipoForm from '../components/ClonarEquipoForm'
import { VigenciaIndividualForm, VigenciaMasivaForm } from '../components/VigenciaForm'
import type { MiEquipo } from '../types'

// Mock apiClient — nunca fetch directo en componentes
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

beforeEach(() => {
  vi.clearAllMocks()
})

describe('MisEquipos — listado', () => {
  it('muestra estado vacío cuando data es []', async () => {
    mockApiClient.get.mockResolvedValueOnce({ data: { data: [], total: 0 } })
    renderWithProviders(<MisEquipos onVigencia={vi.fn()} />)
    expect(await screen.findByText(/Sin equipos asignados/i)).toBeInTheDocument()
  })

  it('renderiza filas con los equipos recibidos', async () => {
    mockApiClient.get.mockResolvedValueOnce({
      data: {
        data: [
          {
            id: 'eq-1',
            materia_id: 'm-1',
            materia_nombre: 'Matemática I',
            carrera: 'Sistemas',
            cohorte: '2024-1',
            comisiones: [],
            rol: 'titular',
            vigencia_desde: '2024-03-01',
            vigencia_hasta: '2024-07-31',
            activo: true,
          },
        ],
        total: 1,
      },
    })
    renderWithProviders(<MisEquipos onVigencia={vi.fn()} />)
    expect(await screen.findByText('Matemática I')).toBeInTheDocument()
    expect(screen.getByText('titular')).toBeInTheDocument()
  })
})

function mockAsignacionMasivaLookups() {
  mockApiClient.get.mockImplementation((url: string) => {
    if (url.includes('/equipos/docentes-disponibles')) {
      return Promise.resolve({
        data: [
          { id: 'd-1', nombre_completo: 'Marina Suárez', email: 'profesor1@demo.local', roles: ['PROFESOR'] },
          { id: 'd-2', nombre_completo: 'Roberto Acosta', email: 'nexo1@demo.local', roles: ['NEXO'] },
        ],
      })
    }
    if (url.includes('/estructura/materias')) {
      return Promise.resolve({ data: [{ id: 'm-1', codigo: 'PROG1', nombre: 'Programación I', descripcion: null, carrera_id: null }] })
    }
    if (url.includes('/admin/carreras')) {
      return Promise.resolve({ data: [{ id: 'c-1', codigo: 'SIS', nombre: 'Ingeniería en Sistemas', descripcion: null, activa: true }] })
    }
    if (url.includes('/admin/cohortes')) {
      return Promise.resolve({ data: [{ id: 'co-1', nombre: '2026', carrera_id: 'c-1', fecha_inicio: null, fecha_fin: null, activa: true }] })
    }
    return Promise.resolve({ data: { data: [], total: 0 } })
  })
}

describe('AsignacionMasivaForm — selectores reales (no inputs de texto)', () => {
  it('puebla docentes, materia, carrera y cohorte con datos del backend', async () => {
    mockAsignacionMasivaLookups()

    const { default: AsignacionMasivaForm } = await import('../components/AsignacionMasivaForm')
    renderWithProviders(<AsignacionMasivaForm onSuccess={vi.fn()} />)

    expect(await screen.findByRole('option', { name: /Marina Suárez/i })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Programación I' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Ingeniería en Sistemas' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: '2026' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'PROFESOR' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'TUTOR' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'NEXO' })).toBeInTheDocument()
  })

  it('envía el payload con carrera_id/cohorte_id/desde (no carrera/cohorte/vigencia_desde)', async () => {
    mockAsignacionMasivaLookups()
    mockApiClient.post.mockResolvedValueOnce({ data: { ids_creados: ['a-1', 'a-2'] } })

    const { default: AsignacionMasivaForm } = await import('../components/AsignacionMasivaForm')
    const onSuccess = vi.fn()
    const user = userEvent.setup()
    renderWithProviders(<AsignacionMasivaForm onSuccess={onSuccess} />)

    await screen.findByRole('option', { name: /Marina Suárez/i })

    await user.selectOptions(screen.getByLabelText(/Docentes/i), ['d-1', 'd-2'])
    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    await user.selectOptions(screen.getByLabelText(/Carrera/i), 'c-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte/i), 'co-1')
    await user.selectOptions(screen.getByLabelText(/Rol/i), 'PROFESOR')
    await user.type(screen.getByLabelText(/Vigencia desde/i), '2026-03-01')

    await user.click(screen.getByRole('button', { name: /Asignar masivamente/i }))

    await waitFor(() => expect(mockApiClient.post).toHaveBeenCalledTimes(1))
    const [url, payload] = mockApiClient.post.mock.calls[0]!
    expect(url).toBe('/api/equipos/asignacion-masiva')
    expect(payload).toMatchObject({
      usuario_ids: ['d-1', 'd-2'],
      materia_id: 'm-1',
      carrera_id: 'c-1',
      cohorte_id: 'co-1',
      rol: 'PROFESOR',
      desde: '2026-03-01',
    })
    expect(payload).not.toHaveProperty('carrera')
    expect(payload).not.toHaveProperty('cohorte')
    expect(payload).not.toHaveProperty('vigencia_desde')

    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(['a-1', 'a-2']))
  })
})

describe('AsignacionMasiva — error 422', () => {
  it('muestra el detalle del error 422 sin perder el formulario', async () => {
    mockAsignacionMasivaLookups()
    mockApiClient.post.mockRejectedValueOnce({
      response: { status: 422, data: { detail: 'usuario_id inválido' } },
    })

    const { default: AsignacionMasivaForm } = await import('../components/AsignacionMasivaForm')
    const onSuccess = vi.fn()
    const user = userEvent.setup()
    renderWithProviders(<AsignacionMasivaForm onSuccess={onSuccess} />)

    await screen.findByRole('option', { name: /Marina Suárez/i })
    await user.selectOptions(screen.getByLabelText(/Docentes/i), ['d-1'])
    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    await user.selectOptions(screen.getByLabelText(/Carrera/i), 'c-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte/i), 'co-1')
    await user.selectOptions(screen.getByLabelText(/Rol/i), 'PROFESOR')
    await user.type(screen.getByLabelText(/Vigencia desde/i), '2026-03-01')
    await user.click(screen.getByRole('button', { name: /Asignar masivamente/i }))

    expect(await screen.findByText('usuario_id inválido')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Asignar masivamente/i })).toBeInTheDocument()
    expect(onSuccess).not.toHaveBeenCalled()
  })
})

function mockClonarLookups() {
  mockApiClient.get.mockImplementation((url: string) => {
    if (url.includes('/estructura/materias')) {
      return Promise.resolve({ data: [{ id: 'm-1', codigo: 'PROG1', nombre: 'Programación I', descripcion: null, carrera_id: null }] })
    }
    if (url.includes('/admin/cohortes')) {
      return Promise.resolve({
        data: [
          { id: 'co-1', nombre: '2025-2', carrera_id: 'c-1', fecha_inicio: null, fecha_fin: null, activa: true },
          { id: 'co-2', nombre: '2026-1', carrera_id: 'c-1', fecha_inicio: null, fecha_fin: null, activa: true },
        ],
      })
    }
    return Promise.resolve({ data: { data: [], total: 0 } })
  })
}

describe('ClonarEquipoForm — selectores reales (materia + cohorte origen/destino)', () => {
  it('puebla materia y cohortes con datos del backend', async () => {
    mockClonarLookups()
    renderWithProviders(<ClonarEquipoForm onSuccess={vi.fn()} />)

    expect(await screen.findByRole('option', { name: 'Programación I' })).toBeInTheDocument()
    const cohorteOptions = await screen.findAllByRole('option', { name: '2025-2' })
    expect(cohorteOptions).toHaveLength(2) // aparece en cohorte origen y destino
  })

  it('envía el payload con materia_id/cohorte_origen_id/cohorte_destino_id/desde', async () => {
    mockClonarLookups()
    mockApiClient.post.mockResolvedValueOnce({ data: { ids_creados: ['a-1'] } })

    const onSuccess = vi.fn()
    const user = userEvent.setup()
    renderWithProviders(<ClonarEquipoForm onSuccess={onSuccess} />)

    await screen.findByRole('option', { name: 'Programación I' })

    await user.selectOptions(screen.getByLabelText(/^Materia$/i), 'm-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte origen/i), 'co-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte destino/i), 'co-2')
    await user.type(screen.getByLabelText(/Vigencia desde/i), '2026-03-01')

    await user.click(screen.getByRole('button', { name: /Clonar equipo/i }))

    await waitFor(() => expect(mockApiClient.post).toHaveBeenCalledTimes(1))
    const [url, payload] = mockApiClient.post.mock.calls[0]!
    expect(url).toBe('/api/equipos/clonar')
    expect(payload).toMatchObject({
      materia_id: 'm-1',
      cohorte_origen_id: 'co-1',
      cohorte_destino_id: 'co-2',
      desde: '2026-03-01',
    })
    expect(payload).not.toHaveProperty('equipo_origen_id')
    expect(payload).not.toHaveProperty('cohorte_destino')

    await waitFor(() => expect(onSuccess).toHaveBeenCalled())
  })

  it('informa cuando no hay asignaciones vigentes para clonar (ids_creados vacío)', async () => {
    mockClonarLookups()
    mockApiClient.post.mockResolvedValueOnce({ data: { ids_creados: [] } })

    const user = userEvent.setup()
    renderWithProviders(<ClonarEquipoForm onSuccess={vi.fn()} />)

    await screen.findByRole('option', { name: 'Programación I' })
    await user.selectOptions(screen.getByLabelText(/^Materia$/i), 'm-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte origen/i), 'co-1')
    await user.selectOptions(screen.getByLabelText(/Cohorte destino/i), 'co-2')
    await user.type(screen.getByLabelText(/Vigencia desde/i), '2026-03-01')
    await user.click(screen.getByRole('button', { name: /Clonar equipo/i }))

    expect(await screen.findByText(/No había asignaciones vigentes para clonar/i)).toBeInTheDocument()
  })
})

const equipoMock: MiEquipo = {
  id: 'eq-1',
  materia_id: 'm-1',
  materia_nombre: 'Programación II',
  carrera: 'Sistemas',
  cohorte: '2026-1',
  comisiones: [],
  rol: 'PROFESOR',
  vigencia_desde: '2026-03-01',
  vigencia_hasta: '2026-07-31',
  activo: true,
}

describe('VigenciaIndividualForm — payload con desde/hasta (no vigencia_desde/vigencia_hasta)', () => {
  it('envía el payload con los nombres reales esperados por el backend', async () => {
    mockApiClient.patch.mockResolvedValueOnce({ data: { id: 'eq-1' } })

    const onSuccess = vi.fn()
    renderWithProviders(<VigenciaIndividualForm equipo={equipoMock} onSuccess={onSuccess} />)

    await userEvent.setup().click(screen.getByRole('button', { name: /Guardar vigencia/i }))

    await waitFor(() => expect(mockApiClient.patch).toHaveBeenCalledTimes(1))
    const [url, payload] = mockApiClient.patch.mock.calls[0]!
    expect(url).toBe('/api/equipos/eq-1/vigencia')
    expect(payload).toMatchObject({ desde: '2026-03-01', hasta: '2026-07-31' })
    expect(payload).not.toHaveProperty('vigencia_desde')
    expect(payload).not.toHaveProperty('vigencia_hasta')
  })
})

describe('VigenciaMasivaForm — selectores reales de materia/cohorte (no equipo_origen_id)', () => {
  it('puebla materia y cohorte, y envía el payload con materia_id/cohorte_id/desde', async () => {
    mockClonarLookups()
    mockApiClient.patch.mockResolvedValueOnce({ data: { filas_afectadas: 3 } })

    const onSuccess = vi.fn()
    const user = userEvent.setup()
    renderWithProviders(<VigenciaMasivaForm onSuccess={onSuccess} />)

    await screen.findByRole('option', { name: 'Programación I' })

    await user.selectOptions(screen.getByLabelText(/^Materia$/i), 'm-1')
    await user.selectOptions(screen.getByLabelText(/^Cohorte$/i), 'co-1')
    await user.type(screen.getByLabelText(/^Desde$/i), '2026-03-01')

    await user.click(screen.getByRole('button', { name: /Actualizar vigencia masiva/i }))

    await waitFor(() => expect(mockApiClient.patch).toHaveBeenCalledTimes(1))
    const [url, payload] = mockApiClient.patch.mock.calls[0]!
    expect(url).toBe('/api/equipos/vigencia-masiva')
    expect(payload).toMatchObject({ materia_id: 'm-1', cohorte_id: 'co-1', desde: '2026-03-01' })
    expect(payload).not.toHaveProperty('equipo_origen_id')
    expect(payload).not.toHaveProperty('vigencia_desde')

    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(3))
  })
})
