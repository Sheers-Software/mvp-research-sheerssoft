"""
Billing and subscription endpoints.
"""

import asyncio
import logging
import uuid

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models import Tenant
from app.services.stripe_service import create_checkout_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing")


class CheckoutRequest(BaseModel):
    hotel_id: str    # maps to tenant_id / client_reference_id in Stripe
    success_url: str
    cancel_url: str


@router.post("/checkout", summary="Generate a Stripe Checkout Session")
async def generate_checkout(
    request: CheckoutRequest,
    _user=Depends(get_current_user),
):
    """
    Generates a Stripe Checkout Session for the hotel setup fee.
    Requires authentication.
    """
    try:
        url = await create_checkout_session(
            hotel_id=request.hotel_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"checkout_url": url}
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Error generating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate checkout session")


@router.post("/webhook", summary="Stripe Webhook Listener")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives and verifies Stripe webhook events.
    On checkout.session.completed: activates the tenant account.

    Stripe signature is verified using the webhook secret from GCP Secret Manager.
    """
    settings = get_settings()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.stripe_webhook_secret:
        logger.error("Stripe webhook secret not configured")
        raise HTTPException(status_code=500, detail="Webhook endpoint not configured")

    try:
        event = await asyncio.to_thread(
            stripe.Webhook.construct_event,
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except stripe.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Stripe webhook parsing error: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    event_type = event["type"]
    logger.info(f"Stripe webhook received: {event_type}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        tenant_id_str = session.get("client_reference_id")
        stripe_customer_id = session.get("customer")

        if tenant_id_str:
            try:
                tenant_uuid = uuid.UUID(tenant_id_str)
                result = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid))
                tenant = result.scalar_one_or_none()

                if tenant:
                    tenant.subscription_status = "active"
                    if stripe_customer_id:
                        tenant.stripe_customer_id = stripe_customer_id
                    await db.commit()
                    logger.info(f"Tenant {tenant_id_str} activated via Stripe payment")
                else:
                    logger.warning(
                        f"Tenant not found for Stripe client_reference_id: {tenant_id_str}"
                    )
            except Exception as e:
                logger.error(f"Failed to activate tenant {tenant_id_str}: {e}")
                await db.rollback()

    return {"status": "received"}
