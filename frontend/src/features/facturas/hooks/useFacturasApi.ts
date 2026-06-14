import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { Factura, FacturasFilters } from '../types'

function buildParams(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, value)
    }
  }
  return params.toString()
}

export function useFacturas(filters: FacturasFilters = {}) {
  return useQuery({
    queryKey: ['facturas', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<Factura[]>(`/api/facturas${qs ? `?${qs}` : ''}`)
      return data
    },
  })
}

export function useCargarFactura() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      periodo,
      detalle,
      archivo,
    }: {
      periodo: string
      detalle: string
      archivo: File
    }) => {
      const formData = new FormData()
      formData.append('periodo', periodo)
      formData.append('detalle', detalle)
      formData.append('archivo', archivo)
      const { data } = await apiClient.post<Factura>('/api/facturas', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] })
    },
  })
}

export function useAbonarFactura() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.patch(`/api/facturas/${id}/abonar`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] })
    },
  })
}
