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
    gemini_model: str = "gemini-1.5-flash"
    gemini_embedding_model: str = "embedding-001"
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

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

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

        # All environments use GCP Secret Manager as the single source of truth for secrets.
        # Credentials are resolved via Application Default Credentials (ADC):
        #   - Local dev: run `gcloud auth application-default login`
        #   - Docker local: set GOOGLE_APPLICATION_CREDENTIALS to a mounted service account key
        #   - GCP (Cloud Run / GCE): workload identity / attached service account (automatic)
        secrets_to_fetch = [
            "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "SENDGRID_API_KEY", "WHATSAPP_API_TOKEN", "WHATSAPP_APP_SECRET",
            "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER",
            "DATABASE_URL", "JWT_SECRET", "WHATSAPP_VERIFY_TOKEN",
            "WHATSAPP_PHONE_NUMBER_ID", "FERNET_ENCRYPTION_KEY", "ADMIN_PASSWORD",
        ]

        client = None
        for key in secrets_to_fetch:
            current_val = getattr(self, key.lower(), "")
            if not current_val:
                try:
                    if not client:
                        try:
                            client = secretmanager.SecretManagerServiceClient()
                        except Exception as client_err:
                            logger.warning(f"Failed to initialize Secret Manager client: {client_err}")
                            break  # Stop trying to fetch secrets if client fails to init

                    name = f"projects/nocturn-ai-487207/secrets/{key}/versions/latest"
                    response = client.access_secret_version(request={"name": name})
                    fetched_val = response.payload.data.decode("UTF-8")

                    setattr(self, key.lower(), fetched_val)
                    logger.info(f"Successfully loaded {key} from GCP Secret Manager.")
                except Exception as e:
                    logger.warning(
                        f"Could not load {key} from Secret Manager. "
                        f"Error: {e}"
                    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
