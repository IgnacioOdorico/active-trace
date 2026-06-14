import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

let refreshPromise: Promise<void> | null = null

let getAccessToken: () => string | null = () => null
let getRefreshToken: () => string | null = () => null
let onTokenRefreshed: (access: string, refresh: string) => void = () => {}
let onAuthFailure: () => void = () => {}
let isLoggingOut: () => boolean = () => false

export function setupAuthInterceptors(config: {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  onTokenRefreshed: (access: string, refresh: string) => void
  onAuthFailure: () => void
  isLoggingOut: () => boolean
}) {
  getAccessToken = config.getAccessToken
  getRefreshToken = config.getRefreshToken
  onTokenRefreshed = config.onTokenRefreshed
  onAuthFailure = config.onAuthFailure
  isLoggingOut = config.isLoggingOut
}

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response?.status !== 401 ||
      isLoggingOut() ||
      originalRequest?._retry
    ) {
      return Promise.reject(error)
    }

    originalRequest._retry = true

    if (!refreshPromise) {
      refreshPromise = (async () => {
        const token = getRefreshToken()
        if (!token) throw new Error('No refresh token')

        const { data } = await axios.post(
          `${apiClient.defaults.baseURL}/api/auth/refresh`,
          { refresh_token: token },
        )
        onTokenRefreshed(data.access_token, data.refresh_token)
      })().finally(() => {
        refreshPromise = null
      })
    }

    try {
      await refreshPromise
      const newToken = getAccessToken()
      originalRequest.headers.Authorization = `Bearer ${newToken}`
      return apiClient(originalRequest)
    } catch {
      onAuthFailure()
      return Promise.reject(error)
    }
  },
)

export default apiClient
