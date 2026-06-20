import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderWithProviders } from '../../../test/test-utils'
import PreviewTable from '../components/PreviewTable'

vi.mock('../../../shared/services/httpClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

vi.mock('../../academico/hooks/useMaterias', () => ({
  useMaterias: vi.fn().mockReturnValue({
    data: [{ id: 'm-1', nombre: 'Programación I', comision: 'A' }],
    isLoading: false,
  }),
}))

import apiClient from '../../../shared/services/httpClient'
const mockApiClient = vi.mocked(apiClient)

beforeEach(() => {
  vi.clearAllMocks()
})

// Contrato real del backend: ActividadDetectada solo tiene nombre/tipo
// (sin id ni columnas) — esto rompía PreviewTable con
// "Cannot read properties of undefined (reading 'join')".
describe('PreviewTable — contrato real (nombre/tipo, sin id ni columnas)', () => {
  it('renderiza actividades usando nombre como identificador, sin crashear', () => {
    renderWithProviders(
      <PreviewTable
        actividades={[
          { nombre: 'Primer Parcial (Real)', tipo: 'numerica' },
          { nombre: 'TP Final', tipo: 'textual' },
        ]}
        selectedIds={['Primer Parcial (Real)']}
        onSelectionChange={vi.fn()}
        materiaNombre="Programación I"
        totalFilas={12}
      />,
    )
    expect(screen.getByText('Primer Parcial (Real)')).toBeInTheDocument()
    expect(screen.getByText('TP Final')).toBeInTheDocument()
    expect(screen.getByText('Numérica')).toBeInTheDocument()
    expect(screen.getByText('Textual')).toBeInTheDocument()
  })

  it('seleccionar todo usa nombre, no id', async () => {
    const onSelectionChange = vi.fn()
    renderWithProviders(
      <PreviewTable
        actividades={[
          { nombre: 'Primer Parcial (Real)', tipo: 'numerica' },
          { nombre: 'TP Final', tipo: 'textual' },
        ]}
        selectedIds={[]}
        onSelectionChange={onSelectionChange}
        materiaNombre="Programación I"
        totalFilas={12}
      />,
    )
    await userEvent.setup().click(screen.getByRole('checkbox', { name: /Seleccionar todo/i }))
    expect(onSelectionChange).toHaveBeenCalledWith(['Primer Parcial (Real)', 'TP Final'])
  })
})

describe('CalificacionesImportarPage — vista previa con el contrato real', () => {
  it('muestra las actividades detectadas sin crashear ante la respuesta real del backend', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: {
        actividades: [
          { nombre: 'Primer Parcial (Real)', tipo: 'numerica' },
          { nombre: 'TP Final', tipo: 'textual' },
        ],
        preview: [{ Nombre: 'Lautaro', 'Apellido(s)': 'Martínez', 'Primer Parcial (Real)': '78' }],
        total_filas: 12,
      },
    })

    const { default: CalificacionesImportarPage } = await import('../pages/CalificacionesImportarPage')
    const user = userEvent.setup()
    renderWithProviders(<CalificacionesImportarPage />)

    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    const file = new File(['Nombre,Apellido(s)\nLautaro,Martínez'], 'notas.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText(/Archivo/i), file)
    await user.click(screen.getByRole('button', { name: /Vista Previa/i }))

    expect(await screen.findByText('Primer Parcial (Real)')).toBeInTheDocument()
    expect(screen.getByText('TP Final')).toBeInTheDocument()
    expect(screen.getByText(/12 filas detectadas/i)).toBeInTheDocument()
  })

  it('al importar reenvía el mismo archivo como multipart (antes el endpoint lo ignoraba)', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: {
        actividades: [{ nombre: 'Primer Parcial (Real)', tipo: 'numerica' }],
        preview: [],
        total_filas: 12,
      },
    })
    mockApiClient.post.mockResolvedValueOnce({
      data: { insertadas: 12, actualizadas: 0, filas_afectadas: 12, errores: [], advertencias: [] },
    })

    const { default: CalificacionesImportarPage } = await import('../pages/CalificacionesImportarPage')
    const user = userEvent.setup()
    renderWithProviders(<CalificacionesImportarPage />)

    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    const file = new File(['Nombre,Apellido(s)\nLautaro,Martínez'], 'notas.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText(/Archivo/i), file)
    await user.click(screen.getByRole('button', { name: /Vista Previa/i }))
    await screen.findByText('Primer Parcial (Real)')

    await user.click(screen.getByRole('button', { name: /Importar Seleccionadas/i }))

    await waitFor(() => expect(mockApiClient.post).toHaveBeenCalledTimes(2))
    const [url, formData, config] = mockApiClient.post.mock.calls[1]!
    expect(url).toBe('/api/calificaciones/importar')
    const sentData = formData as FormData
    expect(sentData.get('file')).toBeInstanceOf(File)
    expect(sentData.get('materia_id')).toBe('m-1')
    expect(sentData.get('actividades')).toBe(JSON.stringify(['Primer Parcial (Real)']))
    expect(config).toMatchObject({ headers: { 'Content-Type': 'multipart/form-data' } })

    const resultado = await screen.findByText(/calificaciones insertadas/i)
    expect(resultado).toHaveTextContent('12 calificaciones insertadas')
  })

  it('sin actividades detectadas muestra el estado vacío', async () => {
    mockApiClient.post.mockResolvedValueOnce({
      data: { actividades: [], preview: [], total_filas: 0 },
    })

    const { default: CalificacionesImportarPage } = await import('../pages/CalificacionesImportarPage')
    const user = userEvent.setup()
    renderWithProviders(<CalificacionesImportarPage />)

    await user.selectOptions(screen.getByLabelText(/Materia/i), 'm-1')
    const file = new File(['x'], 'vacio.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText(/Archivo/i), file)
    await user.click(screen.getByRole('button', { name: /Vista Previa/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/No se detectaron actividades evaluables/i),
      ).toBeInTheDocument()
    })
  })
})
