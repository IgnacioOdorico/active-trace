import { screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import EncuentrosTransversal from '../components/EncuentrosTransversal'
import GestionGuardias from '../components/GestionGuardias'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

const MATERIAS = [{ id: 'mat-1', nombre: 'Programación I' }]
const CARRERAS = [{ id: 'carr-1', nombre: 'Ingeniería en Sistemas' }]

function mockGetByUrl(routes: Record<string, unknown>) {
  mockApiClient.get.mockImplementation((url: string) => {
    for (const [path, data] of Object.entries(routes)) {
      if (url.includes(path)) return Promise.resolve({ data })
    }
    return Promise.resolve({ data: {} })
  })
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('EncuentrosTransversal', () => {
  it('renderiza encuentros desde la respuesta paginada real del backend (items, no data)', async () => {
    mockGetByUrl({
      '/api/encuentros/instancias': {
        items: [
          {
            id: 'enc-1',
            slot_id: 'slot-1',
            materia_id: 'mat-1',
            fecha: '2026-06-23',
            hora: '18:00:00',
            titulo: 'Consulta semanal Programación I',
            estado: 'Realizado',
            meet_url: 'https://meet.example.com/prog1',
            video_url: 'https://example.com/grabacion.mp4',
            comentario: 'Repaso de recursividad',
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS,
    })

    renderWithProviders(<EncuentrosTransversal />)

    expect(await screen.findByText('Consulta semanal Programación I')).toBeInTheDocument()
    expect(screen.getAllByText('Realizado').length).toBeGreaterThan(0)
  })

  it('resuelve materia_id al nombre real de la materia', async () => {
    mockGetByUrl({
      '/api/encuentros/instancias': {
        items: [
          {
            id: 'enc-1',
            slot_id: 'slot-1',
            materia_id: 'mat-1',
            fecha: '2026-06-23',
            hora: '18:00:00',
            titulo: 'Consulta semanal Programación I',
            estado: 'Realizado',
            meet_url: 'https://meet.example.com/prog1',
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS,
    })

    renderWithProviders(<EncuentrosTransversal />)

    expect(await screen.findByText('Programación I')).toBeInTheDocument()
    expect(screen.queryByText('mat-1')).not.toBeInTheDocument()
  })
})

describe('GestionGuardias', () => {
  it('renderiza guardias desde la respuesta paginada real del backend (items, no data)', async () => {
    mockGetByUrl({
      '/api/guardias': {
        items: [
          {
            id: 'guardia-1',
            asignacion_id: 'asig-1',
            materia_id: 'mat-1',
            carrera_id: 'carr-1',
            cohorte_id: 'coh-1',
            dia: 'Miércoles',
            horario: '14:00-16:00',
            estado: 'Pendiente',
            comentarios: 'Guardia de consulta de álgebra',
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS,
      '/api/v1/admin/carreras': CARRERAS,
    })

    renderWithProviders(<GestionGuardias />)

    expect(await screen.findByText('Miércoles')).toBeInTheDocument()
    expect(screen.getByText('14:00-16:00')).toBeInTheDocument()
    expect(screen.getByText('Pendiente')).toBeInTheDocument()
  })

  it('resuelve materia_id y carrera_id a sus nombres reales', async () => {
    mockGetByUrl({
      '/api/guardias': {
        items: [
          {
            id: 'guardia-1',
            asignacion_id: 'asig-1',
            materia_id: 'mat-1',
            carrera_id: 'carr-1',
            dia: 'Miércoles',
            horario: '14:00-16:00',
            estado: 'Pendiente',
          },
        ],
        total: 1,
        pagina: 1,
        page_size: 50,
      },
      '/api/v1/estructura/materias': MATERIAS,
      '/api/v1/admin/carreras': CARRERAS,
    })

    renderWithProviders(<GestionGuardias />)

    expect(await screen.findByText('Programación I')).toBeInTheDocument()
    expect(screen.getByText('Ingeniería en Sistemas')).toBeInTheDocument()
    expect(screen.queryByText('mat-1')).not.toBeInTheDocument()
    expect(screen.queryByText('carr-1')).not.toBeInTheDocument()
  })
})
