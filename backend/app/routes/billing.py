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
from app.services.stripe_service import create_checkout_session, create_subscription_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing")

# Stripe subscription.status → our subscription_status values
_STRIPE_STATUS_MAP = {
    "active": "active",
    "trialing": "trialing",
    "past_due": "past_due",
    "canceled": "cancelled",   # Stripe spells it "canceled"
    "unpaid": "past_due",
    "incomplete": "past_due",
    "incomplete_expired": "cancelled",
    "paused": "past_due",
}


class CheckoutRequest(BaseModel):
    hotel_id: str    # maps to tenant_id / client_reference_id in Stripe
    success_url: str
    cancel_url: str


async def _get_tenant_by_customer(db: AsyncSession, customer_id: str) -> Tenant | None:
    """Look up a Tenant by their Stripe customer ID."""
    result = await db.execute(
        select(Tenant).where(Tenant.stripe_customer_id == customer_id)
    )
    return result.scalar_one_or_none()


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


class SubscribeRequest(BaseModel):
    tenant_id: str
    success_url: str
    cancel_url: str


@router.post("/subscribe", summary="Start RM 199/month recurring subscription")
async def subscribe(
    request: SubscribeRequest,
    _user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a Stripe Checkout Session (mode=subscription) for the RM 199/month
    platform fee. Redirects to Stripe-hosted page; webhook completes activation.
    """
    try:
        result = await db.execute(
            select(Tenant).where(Tenant.id == uuid.UUID(request.tenant_id))
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        if tenant.subscription_status == "active" and tenant.stripe_subscription_id:
            raise HTTPException(status_code=400, detail="Tenant already has an active subscription")

        url = await create_subscription_session(
            tenant_id=request.tenant_id,
            stripe_customer_id=tenant.stripe_customer_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return {"checkout_url": url}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating subscription session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription session")


@router.post("/webhook", summary="Stripe Webhook Listener")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives and verifies Stripe webhook events.

    Handled events:
      - checkout.session.completed       → activate tenant, store customer ID
      - customer.subscription.created   → store subscription ID
      - customer.subscription.updated   → sync subscription status + tier
      - customer.subscription.deleted   → mark tenant as cancelled
      - invoice.payment_succeeded       → confirm active status
      - invoice.payment_failed          → mark tenant as past_due
      - customer.subscription.trial_will_end → logged (notification hook)

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
    data_obj = event["data"]["object"]
    logger.info(f"Stripe webhook received: {event_type}")

    # ── checkout.session.completed ─────────────────────────────────────────────
    if event_type == "checkout.session.completed":
        tenant_id_str = data_obj.get("client_reference_id")
        customer_id = data_obj.get("customer")

        if tenant_id_str:
            try:
                result = await db.execute(
                    select(Tenant).where(Tenant.id == uuid.UUID(tenant_id_str))
                )
                tenant = result.scalar_one_or_none()
                if tenant:
                    tenant.subscription_status = "active"
                    if customer_id:
                        tenant.stripe_customer_id = customer_id
                    await db.commit()
                    logger.info(f"Tenant {tenant_id_str} activated via Stripe checkout")
                else:
                    logger.warning(f"Tenant not found for client_reference_id: {tenant_id_str}")
            except Exception as e:
                logger.error(f"Failed to activate tenant {tenant_id_str}: {e}")
                await db.rollback()

    # ── customer.subscription.created ─────────────────────────────────────────
    elif event_type == "customer.subscription.created":
        customer_id = data_obj.get("customer")
        subscription_id = data_obj.get("id")
        stripe_status = data_obj.get("status", "trialing")

        tenant = await _get_tenant_by_customer(db, customer_id)
        if tenant:
            try:
                tenant.stripe_subscription_id = subscription_id
                tenant.subscription_status = _STRIPE_STATUS_MAP.get(stripe_status, stripe_status)
                await db.commit()
                logger.info(f"Subscription {subscription_id} linked to tenant {tenant.id}")
            except Exception as e:
                logger.error(f"Failed to link subscription to tenant: {e}")
                await db.rollback()

    # ── customer.subscription.updated ─────────────────────────────────────────
    elif event_type == "customer.subscription.updated":
        customer_id = data_obj.get("customer")
        stripe_status = data_obj.get("status", "active")
        subscription_id = data_obj.get("id")

        # Tier can be stored in subscription metadata: {"tier": "boutique"}
        tier = (data_obj.get("metadata") or {}).get("tier")

        tenant = await _get_tenant_by_customer(db, customer_id)
        if tenant:
            try:
                tenant.stripe_subscription_id = subscription_id
                tenant.subscription_status = _STRIPE_STATUS_MAP.get(stripe_status, stripe_status)
                if tier and tier in ("pilot", "boutique", "independent", "premium"):
                    tenant.subscription_tier = tier
                await db.commit()
                logger.info(f"Tenant {tenant.id} subscription updated → {stripe_status}")
            except Exception as e:
                logger.error(f"Failed to update subscription for tenant: {e}")
                await db.rollback()

    # ── customer.subscription.deleted ─────────────────────────────────────────
    elif event_type == "customer.subscription.deleted":
        customer_id = data_obj.get("customer")

        tenant = await _get_tenant_by_customer(db, customer_id)
        if tenant:
            try:
                tenant.subscription_status = "cancelled"
                tenant.stripe_subscription_id = None
                await db.commit()
                logger.info(f"Tenant {tenant.id} subscription cancelled")
            except Exception as e:
                logger.error(f"Failed to cancel tenant subscription: {e}")
                await db.rollback()

    # ── invoice.payment_succeeded ──────────────────────────────────────────────
    elif event_type == "invoice.payment_succeeded":
        customer_id = data_obj.get("customer")
        billing_reason = data_obj.get("billing_reason", "")

        # Skip the initial setup fee invoice (handled by checkout.session.completed)
        if billing_reason != "subscription_create":
            tenant = await _get_tenant_by_customer(db, customer_id)
            if tenant and tenant.subscription_status != "active":
                try:
                    tenant.subscription_status = "active"
                    await db.commit()
                    logger.info(f"Tenant {tenant.id} restored to active after successful payment")
                except Exception as e:
                    logger.error(f"Failed to restore tenant status: {e}")
                    await db.rollback()

    # ── invoice.payment_failed ─────────────────────────────────────────────────
    elif event_type == "invoice.payment_failed":
        customer_id = data_obj.get("customer")

        tenant = await _get_tenant_by_customer(db, customer_id)
        if tenant:
            try:
                tenant.subscription_status = "past_due"
                await db.commit()
                logger.warning(f"Tenant {tenant.id} marked past_due after payment failure")
            except Exception as e:
                logger.error(f"Failed to mark tenant past_due: {e}")
                await db.rollback()

    # ── customer.subscription.trial_will_end ──────────────────────────────────
    elif event_type == "customer.subscription.trial_will_end":
        customer_id = data_obj.get("customer")
        trial_end = data_obj.get("trial_end")
        logger.info(f"Trial ending soon for customer {customer_id} at {trial_end}")
        # TODO: send notification email to tenant owner

    else:
        logger.debug(f"Unhandled Stripe event type: {event_type}")

    return {"status": "received"}
