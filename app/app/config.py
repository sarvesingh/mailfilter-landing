"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All env vars for the MailFilter app."""

    # Database
    DATABASE_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # AI
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"

    # Encryption
    FERNET_KEY: str

    # Email
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "mail@mailfilter.com"

    # Task queue
    REDIS_URL: str = "redis://localhost:6379"

    # App
    APP_URL: str = "http://localhost:8000"
    ENV: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
