import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  useMemo,
  createElement,
  type ReactNode,
} from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient, { setupAuthInterceptors } from '../../../shared/services/httpClient'
import type { AuthUser } from '../types'
import type { LoginResponse, TwoFactorVerifyRequest } from '../types'

interface AuthContextType {
  user: AuthUser | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  requires2fa: boolean
  login: (email: string, password: string) => Promise<LoginResponse | { requires_2fa: true; ephemeral_token: string }>
  verify2fa: (ephemeralToken: string, totpCode: string) => Promise<void>
  logout: () => Promise<void>
  getAccessToken: () => string | null
}

const AuthContext = createContext<AuthContextType | null>(null)

function clearStoredTokens() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('refreshToken')
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [requires2fa, setRequires2fa] = useState(false)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const bootAttemptedRef = useRef(false)

  const accessTokenRef = useRef<string | null>(null)
  const refreshTokenRef = useRef<string | null>(null)
  const isLoggingOutRef = useRef(false)

  const syncTokenRefs = useCallback(() => {
    accessTokenRef.current = accessToken
    refreshTokenRef.current = refreshToken
  }, [accessToken, refreshToken])

  useEffect(() => {
    syncTokenRefs()
  }, [syncTokenRefs])

  useEffect(() => {
    isLoggingOutRef.current = isLoggingOut
  }, [isLoggingOut])

  const clearSession = useCallback(() => {
    clearStoredTokens()
    setAccessToken(null)
    setRefreshToken(null)
    accessTokenRef.current = null
    refreshTokenRef.current = null
    setUser(null)
    setRequires2fa(false)
  }, [])

  useEffect(() => {
    setupAuthInterceptors({
      getAccessToken: () => accessTokenRef.current,
      getRefreshToken: () => refreshTokenRef.current,
      onTokenRefreshed: (access: string, refresh: string) => {
        setAccessToken(access)
        setRefreshToken(refresh)
        localStorage.setItem('accessToken', access)
        localStorage.setItem('refreshToken', refresh)
        accessTokenRef.current = access
        refreshTokenRef.current = refresh
      },
      onAuthFailure: () => {
        clearSession()
      },
      isLoggingOut: () => isLoggingOutRef.current,
    })
  }, [clearSession])

  useEffect(() => {
    if (bootAttemptedRef.current) return
    bootAttemptedRef.current = true

    const storedAccessToken = localStorage.getItem('accessToken')
    const storedRefreshToken = localStorage.getItem('refreshToken')

    if (!storedRefreshToken) {
      setIsLoading(false)
      return
    }

    if (storedAccessToken) {
      setAccessToken(storedAccessToken)
      accessTokenRef.current = storedAccessToken
    }
    setRefreshToken(storedRefreshToken)
    refreshTokenRef.current = storedRefreshToken

    setIsLoading(true)

    apiClient
      .get<AuthUser>('/api/auth/me')
      .then((response) => {
        setUser(response.data)
      })
      .catch(() => {
        clearSession()
      })
      .finally(() => {
        setIsLoading(false)
      })
  }, [clearSession])

  const login = useCallback(
    async (
      email: string,
      password: string,
    ): Promise<LoginResponse | { requires_2fa: true; ephemeral_token: string }> => {
      const response = await apiClient.post<LoginResponse>('/api/auth/login', {
        email,
        password,
      })

      if (response.data.requires_2fa) {
        setRequires2fa(true)
        return {
          requires_2fa: true,
          ephemeral_token: response.data.ephemeral_token!,
        }
      }

      const { access_token, refresh_token } = response.data
      setAccessToken(access_token)
      setRefreshToken(refresh_token)
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      accessTokenRef.current = access_token
      refreshTokenRef.current = refresh_token

      const meResponse = await apiClient.get<AuthUser>('/api/auth/me')
      setUser(meResponse.data)

      return response.data
    },
    [],
  )

  const verify2fa = useCallback(
    async (ephemeralToken: string, totpCode: string) => {
      const response = await apiClient.post<TwoFactorVerifyRequest & LoginResponse>(
        '/api/auth/2fa/verify',
        { ephemeral_token: ephemeralToken, totp_code: totpCode } satisfies TwoFactorVerifyRequest,
      )

      const { access_token, refresh_token } = response.data as unknown as LoginResponse
      setAccessToken(access_token)
      setRefreshToken(refresh_token)
      localStorage.setItem('accessToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      accessTokenRef.current = access_token
      refreshTokenRef.current = refresh_token

      const meResponse = await apiClient.get<AuthUser>('/api/auth/me')
      setUser(meResponse.data)
      setRequires2fa(false)
    },
    [],
  )

  const logout = useCallback(async () => {
    setIsLoggingOut(true)
    try {
      await apiClient.post('/api/auth/logout')
    } catch {
      // fire-and-forget
    } finally {
      clearSession()
      setIsLoggingOut(false)
      navigate('/login', { replace: true })
    }
  }, [clearSession, navigate])

  const getAccessToken = useCallback(() => accessToken, [accessToken])

  const value = useMemo(
    () => ({
      user,
      accessToken,
      isAuthenticated: !!user,
      isLoading,
      requires2fa,
      login,
      verify2fa,
      logout,
      getAccessToken,
    }),
    [user, accessToken, isLoading, requires2fa, login, verify2fa, logout, getAccessToken],
  )

  return createElement(AuthContext.Provider, { value }, children)
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider')
  }
  return context
}
