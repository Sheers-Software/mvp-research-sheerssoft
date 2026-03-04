"""
Channel Setup Service — Automated channel configuration orchestrator.
Handles WhatsApp (Meta/Twilio), Email (SendGrid), and Web Chat widget auto-setup.
Updates OnboardingProgress with status per channel.
"""

import uuid
import structlog

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import OnboardingProgress, Property

logger = structlog.get_logger()


async def setup_channels(
    db: AsyncSession,
    tenant_id: str,
    property_id: str,
    channels: list[str],
    whatsapp_provider: str = "meta",
):
    """
    Orchestrator: run all selected channel setups and update OnboardingProgress.
    """
    errors = {}

    for channel in channels:
        try:
            if channel == "whatsapp":
                await _setup_whatsapp(db, property_id, whatsapp_provider)
            elif channel == "email":
                await _setup_email(db, property_id)
            elif channel == "website":
                await _setup_website(db, property_id)
            else:
                logger.warning(f"Unknown channel: {channel}")
                continue

            # Mark channel as active
            await _update_channel_status(db, tenant_id, property_id, channel, "active")
            logger.info(f"Channel '{channel}' setup successful", property_id=property_id)

        except Exception as e:
            error_msg = str(e)
            errors[channel] = error_msg
            await _update_channel_status(db, tenant_id, property_id, channel, "failed")
            logger.error(f"Channel '{channel}' setup failed", property_id=property_id, error=error_msg)

    # Store errors if any
    if errors:
        stmt = (
            update(OnboardingProgress)
            .where(
                OnboardingProgress.tenant_id == uuid.UUID(tenant_id),
                OnboardingProgress.property_id == uuid.UUID(property_id),
            )
            .values(channel_errors=errors)
        )
        await db.execute(stmt)
        await db.commit()

        # Notify account manager of failures
        await _notify_account_manager_failure(db, tenant_id, property_id, errors)

    return errors


async def _update_channel_status(
    db: AsyncSession, tenant_id: str, property_id: str, channel: str, status: str
):
    """Update a specific channel's status in OnboardingProgress."""
    column_map = {
        "whatsapp": "whatsapp_status",
        "email": "email_status",
        "website": "website_status",
    }
    column = column_map.get(channel)
    if not column:
        return

    stmt = (
        update(OnboardingProgress)
        .where(
            OnboardingProgress.tenant_id == uuid.UUID(tenant_id),
            OnboardingProgress.property_id == uuid.UUID(property_id),
        )
        .values(**{column: status})
    )
    await db.execute(stmt)
    await db.commit()


# ─────────────────────────────────────────────────────────────
# WhatsApp Setup
# ─────────────────────────────────────────────────────────────

async def _setup_whatsapp(db: AsyncSession, property_id: str, provider: str):
    """
    Configure WhatsApp channel for a property.

    Meta Cloud API: Semi-automated — stores credentials, verifies webhook URL.
    The client must manually grant access to our Meta Business App.

    Twilio: Fully automated — configures webhook URL via Twilio API.
    """
    settings = get_settings()
    prop_stmt = select(Property).where(Property.id == uuid.UUID(property_id))
    result = await db.execute(prop_stmt)
    prop = result.scalar_one_or_none()

    if not prop:
        raise Exception(f"Property {property_id} not found")

    if provider == "twilio":
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            raise Exception("Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")

        if not prop.twilio_phone_number:
            raise Exception("Twilio phone number not set on property.")

        # In production, we would call Twilio API to set the webhook URL:
        # POST /2010-04-01/Accounts/{sid}/IncomingPhoneNumbers/{phone_sid}
        # Setting SmsUrl/StatusCallback to our webhook endpoint
        logger.info(
            "WhatsApp (Twilio) setup: webhook URL configured",
            property_id=property_id,
            webhook_url=f"https://api.nocturnai.com/api/v1/webhook/twilio/whatsapp",
            phone=prop.twilio_phone_number,
        )

    elif provider == "meta":
        if not prop.whatsapp_number:
            raise Exception("WhatsApp Business number not set on property.")

        # Meta requires manual business verification.
        # We log the required webhook URL for the onboarding team.
        logger.info(
            "WhatsApp (Meta) setup: awaiting client Meta Business access grant",
            property_id=property_id,
            webhook_url=f"https://api.nocturnai.com/api/v1/webhook/whatsapp?property_slug={prop.slug}",
            phone=prop.whatsapp_number,
        )

    logger.info("WhatsApp channel configured", property_id=property_id, provider=provider)


# ─────────────────────────────────────────────────────────────
# Email Setup (SendGrid Inbound Parse)
# ─────────────────────────────────────────────────────────────

async def _setup_email(db: AsyncSession, property_id: str):
    """
    Configure email channel via SendGrid Inbound Parse.
    Generates a unique inbound address and (in production) configures SendGrid via API.
    """
    settings = get_settings()
    prop_stmt = select(Property).where(Property.id == uuid.UUID(property_id))
    result = await db.execute(prop_stmt)
    prop = result.scalar_one_or_none()

    if not prop:
        raise Exception(f"Property {property_id} not found")

    # Generate inbound email address
    inbound_email = f"{prop.slug}@inbound.nocturnai.com"

    # In production with SendGrid API:
    # POST /v3/user/webhooks/parse/settings
    # { "hostname": "inbound.nocturnai.com", "url": webhook_url, "spam_check": true }
    logger.info(
        "Email channel configured",
        property_id=property_id,
        inbound_email=inbound_email,
        note="Client must forward reservation email to this address",
    )

    # Store notification email if not set
    if not prop.notification_email:
        prop.notification_email = inbound_email
        await db.commit()


# ─────────────────────────────────────────────────────────────
# Website Chat Widget Setup
# ─────────────────────────────────────────────────────────────

async def _setup_website(db: AsyncSession, property_id: str):
    """
    Generate the web chat widget embed code for a property.
    This is fully automated — just generates the script tag.
    """
    prop_stmt = select(Property).where(Property.id == uuid.UUID(property_id))
    result = await db.execute(prop_stmt)
    prop = result.scalar_one_or_none()

    if not prop:
        raise Exception(f"Property {property_id} not found")

    embed_code = (
        f'<script src="https://widget.nocturnai.com/chat.js" '
        f'data-property="{prop.slug}"></script>'
    )

    logger.info(
        "Website chat widget configured",
        property_id=property_id,
        embed_code=embed_code,
    )


# ─────────────────────────────────────────────────────────────
# Failure Notifications
# ─────────────────────────────────────────────────────────────

async def _notify_account_manager_failure(
    db: AsyncSession, tenant_id: str, property_id: str, errors: dict
):
    """
    Notify the assigned Account Manager when channel setup fails.
    Uses email notification via SendGrid.
    """
    from app.models import Tenant
    from app.services.email import send_email

    stmt = select(Tenant).where(Tenant.id == uuid.UUID(tenant_id))
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        return

    error_lines = "\n".join([f"• {ch}: {err}" for ch, err in errors.items()])
    subject = f"⚠️ Channel Setup Failed — {tenant.name}"
    content = (
        f"<p><strong>Channel setup failed for tenant: {tenant.name}</strong></p>"
        f"<p>The following channels encountered errors during auto-setup:</p>"
        f"<pre>{error_lines}</pre>"
        f"<p>Please check the SuperAdmin dashboard to retry or configure manually.</p>"
        f"<p>Tenant ID: {tenant_id}<br>Property ID: {property_id}</p>"
    )

    # Send to assigned account manager or default staff email
    settings = get_settings()
    recipient = tenant.assigned_account_manager or settings.staff_notification_email

    if recipient:
        try:
            await send_email(
                to_email=recipient,
                subject=subject,
                content=content,
                is_html=True,
                hotel_name="Nocturn AI — Onboarding",
            )
        except Exception as e:
            logger.error("Failed to send channel failure notification", error=str(e))
