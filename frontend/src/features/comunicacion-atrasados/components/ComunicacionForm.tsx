import { useState } from 'react'
import { useMaterias } from '../../academico/hooks/useMaterias'
import type { PreviewResponse, PreviewRequest, EnviarRequest, EnviarResponse } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
      <BentoCard>
        <div className="space-y-6">
          <div className="flex flex-col gap-1">
            <label htmlFor="materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">Materia</label>
            <select
              id="materia"
              value={materiaId}
              onChange={(e) => setMateriaId(e.target.value)}
              className="w-full max-w-md neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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

          <div className="flex flex-col gap-1">
            <label htmlFor="asunto" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              Asunto (template)
            </label>
            <p className="font-body-md text-[12px] text-on-surface-variant mb-1">Use {'{nombre}'}, {'{apellidos}'}, {'{materia}'} como variables.</p>
            <Input
              id="asunto"
              type="text"
              value={asuntoTemplate}
              onChange={(e) => setAsuntoTemplate(e.target.value)}
              placeholder="Ej: Notificación de materias atrasadas - {materia}"
              className="w-full"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="cuerpo" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              Cuerpo (template)
            </label>
            <p className="font-body-md text-[12px] text-on-surface-variant mb-1">Use {'{nombre}'}, {'{apellidos}'}, {'{materia}'}, {'{actividades}'} como variables.</p>
            <textarea
              id="cuerpo"
              rows={6}
              value={cuerpoTemplate}
              onChange={(e) => setCuerpoTemplate(e.target.value)}
              placeholder="Estimado/a {nombre} {apellidos},&#10;&#10;Le informamos que tiene actividades pendientes en {materia}..."
              className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>
      </BentoCard>

      <BentoCard>
        <div className="space-y-4">
          <div className="flex flex-col gap-1">
            <label htmlFor="destinatarioPreview" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
              Destinatario para preview
            </label>
            <div className="flex items-center gap-3">
              <Input
                id="destinatarioPreview"
                type="email"
                value={destinatarioPreview}
                onChange={(e) => setDestinatarioPreview(e.target.value)}
                placeholder="email@ejemplo.com"
                className="w-full max-w-md"
              />
              <Button
                onClick={handlePreview}
                disabled={!materiaId || !destinatarioPreview || !asuntoTemplate || !cuerpoTemplate || previewLoading}
                variant="secondary"
              >
                {previewLoading ? 'Generando preview...' : 'Vista Previa'}
              </Button>
            </div>
          </div>

          {previewError && (
            <div className="rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">{previewError}</div>
          )}

          {previewData && (
            <div className="rounded neo-latex-border bg-surface-container-high p-4 border-l-4 border-l-primary">
              <div className="mb-2 flex items-center justify-between">
                <p className="font-label-caps text-label-caps uppercase text-primary">Preview</p>
                <span className="rounded bg-primary/10 px-2 py-0.5 font-body-md text-[12px] font-medium text-primary border border-primary/20">
                  Solo lectura — preview del destinatario seleccionado
                </span>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-3">
                <p className="font-body-md text-body-md font-medium text-on-surface">
                  <span className="text-on-surface-variant">Asunto:</span> {previewData.asunto}
                </p>
                <hr className="my-2 border-outline-variant" />
                <p className="whitespace-pre-wrap font-body-md text-body-md text-on-surface">{previewData.cuerpo}</p>
              </div>
            </div>
          )}
        </div>
      </BentoCard>

      <BentoCard>
        <div className="space-y-4">
          <div className="flex flex-col gap-1">
            <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Destinatarios</label>
            <p className="font-body-md text-[12px] text-on-surface-variant mb-1">Agregue los emails a quienes enviar la comunicación.</p>

            {destinatarios.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2 mb-2">
                {destinatarios.map((email) => (
                  <span
                    key={email}
                    className="inline-flex items-center rounded-full bg-primary/10 border border-primary/20 px-3 py-1 font-body-md text-[14px] text-primary"
                  >
                    {email}
                    <button
                      type="button"
                      onClick={() => eliminarDestinatario(email)}
                      className="ml-2 text-primary hover:text-primary/70"
                      aria-label={`Eliminar ${email}`}
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <Input
                type="email"
                value={nuevoDestinatario}
                onChange={(e) => setNuevoDestinatario(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); agregarDestinatario() } }}
                placeholder="email@ejemplo.com"
                className="flex-1"
              />
              <Button
                onClick={agregarDestinatario}
                variant="secondary"
              >
                Agregar
              </Button>
            </div>
          </div>

          {sendError && (
            <div className="rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">{sendError}</div>
          )}

          <div className="flex gap-3 pt-4 border-t border-outline-variant">
            <Button
              onClick={() => setShowConfirm(true)}
              disabled={!materiaId || destinatarios.length === 0 || !asuntoTemplate || !cuerpoTemplate || sending}
              variant="primary"
            >
              {sending ? 'Enviando...' : 'Enviar'}
            </Button>
          </div>
        </div>
      </BentoCard>

      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-scrim/40 backdrop-blur-sm">
          <BentoCard className="mx-4 w-full max-w-md shadow-xl bg-surface-container-lowest">
            <h3 className="font-headline-sm text-headline-sm text-on-surface">Confirmar envío</h3>
            <p className="mt-2 font-body-md text-body-md text-on-surface-variant">
              Se enviará la comunicación a <strong className="font-mono-data text-on-surface">{destinatarios.length}</strong> destinatario(s).
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <Button
                onClick={() => setShowConfirm(false)}
                variant="secondary"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleSend}
                disabled={sending}
                variant="primary"
              >
                {sending ? 'Enviando...' : 'Confirmar Envío'}
              </Button>
            </div>
          </BentoCard>
        </div>
      )}
    </div>
  )
}
