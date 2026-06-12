import type { User } from '../../shared/types/auth'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  requires_2fa?: boolean
  ephemeral_token?: string
}

export interface TwoFactorVerifyRequest {
  ephemeral_token: string
  totp_code: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  password: string
}

export interface AuthUser extends User {}

export interface RefreshResponse {
  access_token: string
  refresh_token: string
}
