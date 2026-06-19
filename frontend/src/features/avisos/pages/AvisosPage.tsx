import { useState } from 'react'
import GestionAvisos from '../components/GestionAvisos'
import AvisosUsuario from '../components/AvisosUsuario'
import { Button } from '../../../shared/components/ui/Button'
import { useAuth } from '../../auth/hooks/useAuth'
import { hasPermission } from '../../../shared/utils/permissions'

type Tab = 'mis-avisos' | 'gestion'

export default function AvisosPage() {
  const { user } = useAuth()
  const puedeGestionar = hasPermission(user?.permissions ?? [], 'avisos:publicar')
  const [tab, setTab] = useState<Tab>('mis-avisos')

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Avisos</h1>
      </div>

      {puedeGestionar && (
        <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
          <Button
            onClick={() => setTab('mis-avisos')}
            variant={tab === 'mis-avisos' ? 'primary' : 'ghost'}
          >
            Mis avisos
          </Button>
          <Button
            onClick={() => setTab('gestion')}
            variant={tab === 'gestion' ? 'primary' : 'ghost'}
          >
            Gestión
          </Button>
        </div>
      )}

      <div>
        {(tab === 'mis-avisos' || !puedeGestionar) && <AvisosUsuario />}
        {tab === 'gestion' && puedeGestionar && <GestionAvisos />}
      </div>
    </div>
  )
}
