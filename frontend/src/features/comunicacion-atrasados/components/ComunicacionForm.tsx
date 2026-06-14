import { useState } from 'react'
import { useMaterias } from '../../academico/hooks/useMaterias'
import type { PreviewResponse, PreviewRequest, EnviarRequest, EnviarResponse } from '../types'

interface Props {
  initialMateriaId?: string
  initialDestinatarioEmail?: string
  onPreview: (params: PreviewRequest) => Promise<PreviewResponse>
  onEnviar: (params: EnviarRequest) => Promise<EnviarResponse>
}

export default function ComunicacionForm({ initialMateriaId, initialDestinatarioEmail, onPreview, onEnviar }: Props) {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const [materiaId, setMateriaId] = useState(initialMateriaId ?? '')
  const [asuntoTemplate, setAsuntoTemplate] = useState('')
  const [cuerpoTemplate, setCuerpoTemplate] = useState('')
  const [destinatarioPreview, setDestinatarioPreview] = useState(initialDestinatarioEmail ?? '')
  const [destinatarios, setDestinatarios] = useState<string[]>(
    initialDestinatarioEmail ? [initialDestinatarioEmail] : [],
  )
  const [nuevoDestinatario, setNuevoDestinatario] = useState('')
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)
  const [showConfirm, setShowConfirm] = useState(false)

  async function handlePreview() {
    if (!materiaId || !destinatarioPreview || !asuntoTemplate || !cuerpoTemplate) return
    setPreviewLoading(true)
    setPreviewError(null)
    try {
      const data = await onPreview({
        materia_id: materiaId,
        destinatario_email: destinatarioPreview,
        asunto_template: asuntoTemplate,
        cuerpo_template: cuerpoTemplate,
      })
      setPreviewData(data)
    } catch (err) {
      setPreviewError(err instanceof Error ? err.message : 'Error al generar preview')
    } finally {
      setPreviewLoading(false)
    }
  }

  async function handleSend() {
    if (!materiaId || destinatarios.length === 0 || !asuntoTemplate || !cuerpoTemplate) return
    setSending(true)
    setSendError(null)
    try {
      await onEnviar({
        materia_id: materiaId,
        destinatarios,
        asunto_template: asuntoTemplate,
        cuerpo_template: cuerpoTemplate,
      })
    } catch (err) {
      setSendError(err instanceof Error ? err.message : 'Error al enviar')
    } finally {
      setSending(false)
      setShowConfirm(false)
    }
  }

  function agregarDestinatario() {
    const email = nuevoDestinatario.trim()
    if (email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && !destinatarios.includes(email)) {
      setDestinatarios([...destinatarios, email])
      setNuevoDestinatario('')
    }
  }

  function eliminarDestinatario(email: string) {
    setDestinatarios(destinatarios.filter((d) => d !== email))
  }

  return (
    <div className="space-y-6">
      <div>
        <label htmlFor="materia" className="block text-sm font-medium text-gray-700">Materia</label>
        <select
          id="materia"
          value={materiaId}
          onChange={(e) => setMateriaId(e.target.value)}
          className="mt-1 block w-full max-w-md rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Seleccione una materia</option>
          {materiasLoading && <option value="" disabled>Cargando materias...</option>}
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre}{m.comision ? ` - ${m.comision}` : ''}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="asunto" className="block text-sm font-medium text-gray-700">
          Asunto (template)
        </label>
        <p className="text-xs text-gray-500">Use {'{nombre}'}, {'{apellidos}'}, {'{materia}'} como variables.</p>
        <input
          id="asunto"
          type="text"
          value={asuntoTemplate}
          onChange={(e) => setAsuntoTemplate(e.target.value)}
          placeholder="Ej: Notificación de materias atrasadas - {materia}"
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="cuerpo" className="block text-sm font-medium text-gray-700">
          Cuerpo (template)
        </label>
        <p className="text-xs text-gray-500">Use {'{nombre}'}, {'{apellidos}'}, {'{materia}'}, {'{actividades}'} como variables.</p>
        <textarea
          id="cuerpo"
          rows={6}
          value={cuerpoTemplate}
          onChange={(e) => setCuerpoTemplate(e.target.value)}
          placeholder="Estimado/a {nombre} {apellidos},&#10;&#10;Le informamos que tiene actividades pendientes en {materia}..."
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div>
        <label htmlFor="destinatarioPreview" className="block text-sm font-medium text-gray-700">
          Destinatario para preview
        </label>
        <input
          id="destinatarioPreview"
          type="email"
          value={destinatarioPreview}
          onChange={(e) => setDestinatarioPreview(e.target.value)}
          placeholder="email@ejemplo.com"
          className="mt-1 block w-full max-w-md rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <button
          type="button"
          onClick={handlePreview}
          disabled={!materiaId || !destinatarioPreview || !asuntoTemplate || !cuerpoTemplate || previewLoading}
          className="mt-2 rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {previewLoading ? 'Generando preview...' : 'Vista Previa'}
        </button>
      </div>

      {previewError && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">{previewError}</div>
      )}

      {previewData && (
        <div className="rounded-md border border-blue-200 bg-blue-50 p-4">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">Preview</p>
            <span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
              Solo lectura — preview del destinatario seleccionado
            </span>
          </div>
          <div className="rounded border border-blue-100 bg-white p-3">
            <p className="text-sm font-medium text-gray-900">
              <span className="text-gray-500">Asunto:</span> {previewData.asunto}
            </p>
            <hr className="my-2 border-blue-100" />
            <p className="whitespace-pre-wrap text-sm text-gray-700">{previewData.cuerpo}</p>
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Destinatarios</label>
        <p className="text-xs text-gray-500">Agregue los emails a quienes enviar la comunicación.</p>

        {destinatarios.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {destinatarios.map((email) => (
              <span
                key={email}
                className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
              >
                {email}
                <button
                  type="button"
                  onClick={() => eliminarDestinatario(email)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                  aria-label={`Eliminar ${email}`}
                >
                  &times;
                </button>
              </span>
            ))}
          </div>
        )}

        <div className="mt-2 flex gap-2">
          <input
            type="email"
            value={nuevoDestinatario}
            onChange={(e) => setNuevoDestinatario(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); agregarDestinatario() } }}
            placeholder="email@ejemplo.com"
            className="block flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={agregarDestinatario}
            className="rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Agregar
          </button>
        </div>
      </div>

      {sendError && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">{sendError}</div>
      )}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={() => setShowConfirm(true)}
          disabled={!materiaId || destinatarios.length === 0 || !asuntoTemplate || !cuerpoTemplate || sending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {sending ? 'Enviando...' : 'Enviar'}
        </button>
      </div>

      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="mx-4 w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-gray-900">Confirmar envío</h3>
            <p className="mt-2 text-sm text-gray-600">
              Se enviará la comunicación a <strong>{destinatarios.length}</strong> destinatario(s).
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowConfirm(false)}
                className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleSend}
                disabled={sending}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {sending ? 'Enviando...' : 'Confirmar Envío'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
