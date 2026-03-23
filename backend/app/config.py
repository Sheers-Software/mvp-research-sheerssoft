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
    database_url: str = ""  # Loaded from GCP Secret Manager; fallback to local dev if empty after fetch
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
    sendgrid_from_email: str = ""  # Loaded from Secret Manager as SENDGRID_FROM_EMAIL
    staff_notification_email: str = ""  # Loaded from Secret Manager as STAFF_NOTIFICATION_EMAIL; fallback to from_email
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

    # Auth (Supabase Auth — magic link based)
    jwt_secret: str = "dev_jwt_secret_change_in_production"  # Supabase project JWT secret
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    supabase_url: str = ""  # e.g. https://xxx.supabase.co
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""  # Admin API access (user creation, magic links)
    
    # Legacy Admin Credentials (kept for backward compatibility during migration)
    admin_user: str = "admin"
    admin_password: str = "password123"

    # Comma-separated list of emails that are always granted superadmin on magic link login
    superadmin_emails: str = ""

    # Security
    fernet_encryption_key: str = ""  # PII field-level encryption key
    widget_api_key_strict: bool = False  # Enforce API key validation for widget

    # Stripe
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_currency: str = "usd"          # e.g. "usd" or "myr"
    stripe_setup_fee_amount: int = 15000  # Smallest currency unit (cents/sen); 15000 = $150 USD

    # Environment
    environment: str = "development"
    allowed_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"  # Used for magic link redirect; set to deployed frontend URL

    # Report scheduling
    daily_report_hour: int = 7
    daily_report_minute: int = 30
    timezone: str = "Asia/Kuala_Lumpur"

    # Internal scheduler secret — protects /api/v1/internal/* endpoints
    # called by Cloud Scheduler in production. Generate with: openssl rand -hex 32
    internal_scheduler_secret: str = ""

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
        # All environments use GCP Secret Manager as the single source of truth for secrets.
        # Credentials are resolved via Application Default Credentials (ADC):
        #   - Local dev: run `gcloud auth application-default login`
        #   - Docker local: set GOOGLE_APPLICATION_CREDENTIALS to a mounted service account key
        #   - GCP (Cloud Run / GCE): workload identity / attached service account (automatic)
        secrets_to_fetch = [
            "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
            "SENDGRID_API_KEY", "SENDGRID_FROM_EMAIL", "STAFF_NOTIFICATION_EMAIL",
            "WHATSAPP_API_TOKEN", "WHATSAPP_APP_SECRET",
            "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER",
            "DATABASE_URL", "JWT_SECRET", "WHATSAPP_VERIFY_TOKEN",
            "WHATSAPP_PHONE_NUMBER_ID", "FERNET_ENCRYPTION_KEY", "ADMIN_PASSWORD",
            "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY",
            "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET",
            "INTERNAL_SCHEDULER_SECRET",
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
                    fetched_val = response.payload.data.decode("UTF-8").strip().lstrip("\ufeff")

                    setattr(self, key.lower(), fetched_val)
                    logger.info(f"Successfully loaded {key} from GCP Secret Manager.")
                except Exception as e:
                    logger.warning(
                        f"Could not load {key} from Secret Manager. "
                        f"Error: {e}"
                    )

        # Post-fetch fixups
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL could not be loaded from GCP Secret Manager and is not set as an environment variable. "
                "Ensure GCP Application Default Credentials are configured and the secret exists in project nocturn-ai-487207."
            )

    class Config:
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton settings instance."""
    return Settings()
