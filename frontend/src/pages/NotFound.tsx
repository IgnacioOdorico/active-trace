import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex min-h-full items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300">404</h1>
        <p className="mt-4 text-lg text-gray-600">
          Página no encontrada
        </p>
        <Link
          to="/"
          className="mt-6 inline-block text-blue-600 hover:text-blue-800"
        >
          Volver al inicio
        </Link>
      </div>
    </div>
  )
}
