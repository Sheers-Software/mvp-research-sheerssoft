"""
PII Encryption Service — Field-level encryption for guest data (PDPA 2010 compliance).

Uses Fernet symmetric encryption to protect sensitive fields:
- Guest name, phone, email in leads
- Guest identifiers in conversations

If FERNET_ENCRYPTION_KEY is not set, operates in passthrough mode (dev only).
"""

import base64
import structlog
from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

logger = structlog.get_logger()


class PIIEncryptionService:
    """Handles encryption/decryption of Personally Identifiable Information."""

    def __init__(self):
        settings = get_settings()
        self._key = settings.fernet_encryption_key
        self._fernet = None

        if self._key:
            try:
                self._fernet = Fernet(self._key.encode() if isinstance(self._key, str) else self._key)
                logger.info("PII encryption initialized")
            except Exception as e:
                logger.error("Invalid Fernet key", error=str(e))
                self._fernet = None
        else:
            if settings.is_production:
                logger.warning("PII encryption disabled in production — set FERNET_ENCRYPTION_KEY")
            else:
                logger.info("PII encryption disabled (no key set — passthrough mode)")

    @property
    def is_active(self) -> bool:
        return self._fernet is not None

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        Returns the ciphertext as a base64-encoded string.
        In passthrough mode, returns the original string unchanged.
        """
        if not plaintext:
            return plaintext

        if not self._fernet:
            return plaintext

        try:
            return self._fernet.encrypt(plaintext.encode()).decode()
        except Exception as e:
            logger.error("PII encryption failed", error=str(e))
            return plaintext

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a ciphertext string.
        Returns the original plaintext.
        In passthrough mode, returns the string unchanged.
        """
        if not ciphertext:
            return ciphertext

        if not self._fernet:
            return ciphertext

        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            # Already plaintext or encrypted with different key
            logger.debug("Decryption failed — returning as-is (may be plaintext)")
            return ciphertext
        except Exception as e:
            logger.error("PII decryption failed", error=str(e))
            return ciphertext

    def encrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """Encrypt specified fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result

    def decrypt_dict(self, data: dict, fields: list[str]) -> dict:
        """Decrypt specified fields in a dictionary."""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.decrypt(str(result[field]))
        return result


# Singleton instance
_pii_service = None


def get_pii_service() -> PIIEncryptionService:
    """Get the singleton PII encryption service."""
    global _pii_service
    if _pii_service is None:
        _pii_service = PIIEncryptionService()
    return _pii_service


# PII field definitions per model
PII_FIELDS = {
    "lead": ["guest_name", "guest_phone", "guest_email"],
    "conversation": ["guest_name"],
}


def encrypt_pii(model_type: str, data: dict) -> dict:
    """Encrypt PII fields for storage."""
    fields = PII_FIELDS.get(model_type, [])
    return get_pii_service().encrypt_dict(data, fields)


def decrypt_pii(model_type: str, data: dict) -> dict:
    """Decrypt PII fields for reading."""
    fields = PII_FIELDS.get(model_type, [])
    return get_pii_service().decrypt_dict(data, fields)
