from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class Login2FARequired(BaseModel):
    status: str = "2FA_REQUIRED"
    ephemeral_token: str


class TOTPEnrollResponse(BaseModel):
    provisioning_uri: str
    secret: str


class TOTPVerifyRequest(BaseModel):
    code: str
    ephemeral_token: str | None = None


class ForgotRequest(BaseModel):
    email: str


class ResetRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
