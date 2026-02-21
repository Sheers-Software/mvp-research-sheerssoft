"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from google.cloud import secretmanager
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://sheerssoft:sheerssoft_dev_password@localhost:5432/sheerssoft"
    redis_url: str = "redis://localhost:6379/0"

    # Gemini (Default LLM)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768

    # OpenAI (Fallback)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Anthropic (LLM fallback)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-haiku-20240307"

    # AI behavior
    ai_confidence_threshold: float = 0.7  # Handoff if below this

    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "reports@yourdomain.com"
    staff_notification_email: str = "reservations@vivatel.com.my"  # Default for pilot
    sendgrid_webhook_public_key: str = ""  # Ed25519 public key for signature verification

    # WhatsApp
    whatsapp_verify_token: str = "sheerssoft_verify_token"
    whatsapp_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_app_secret: str = ""  # For webhook signature verification

    # Auth
    jwt_secret: str = "dev_jwt_secret_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # Admin Credentials
    admin_user: str = "admin"
    admin_password: str = "password123"

    # Security
    fernet_encryption_key: str = ""  # PII field-level encryption key
    widget_api_key_strict: bool = False  # Enforce API key validation for widget

    # Environment
    environment: str = "development"
    allowed_origins: str = "http://localhost:3000"

    # Report scheduling
    daily_report_hour: int = 7
    daily_report_minute: int = 30
    timezone: str = "Asia/Kuala_Lumpur"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_demo(self) -> bool:
        return self.environment == "demo"

    @property
    def channels_are_live(self) -> bool:
        """True only in production with real channel credentials configured."""
        return self.is_production and (
            bool(self.whatsapp_api_token) or bool(self.sendgrid_api_key)
        )

    def model_post_init(self, __context):
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")

        # Fallback to GCP Secret Manager if the Gemini key is not configured locally
        if not self.gemini_api_key and self.is_production:
            try:
                client = secretmanager.SecretManagerServiceClient()
                # Project nocturn-ai-487207
                name = "projects/nocturn-ai-487207/secrets/GEMINI_API_KEY/versions/latest"
                response = client.access_secret_version(request={"name": name})
                self.gemini_api_key = response.payload.data.decode("UTF-8")
                logger.info("Successfully loaded GEMINI_API_KEY from GCP Secret Manager.")
            except Exception as e:
                logger.warning(
                    f"Could not load GEMINI_API_KEY from Secret Manager. "
                    f"If running locally, this is expected unless you have run `gcloud auth application-default login`. "
                    f"Error: {e}"
                )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
