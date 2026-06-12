import { useAuth } from '../features/auth/hooks/useAuth'

export default function Home() {
  const { user } = useAuth()

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">
        Bienvenido, {user?.nombre}
      </h1>
      <p className="mt-2 text-gray-600">
        Ha iniciado sesión como {user?.email}
      </p>
    </div>
  )
}
