"""
Stripe integration service for creating payment sessions and handling webhooks.
"""

import asyncio
import logging

import stripe

from app.config import get_settings

logger = logging.getLogger(__name__)


async def create_checkout_session(hotel_id: str, success_url: str, cancel_url: str) -> str:
    """
    Creates a Stripe Checkout Session for the onboarding/setup fee.
    Returns the session URL.

    Uses asyncio.to_thread() because the Stripe SDK is synchronous.
    The stripe.api_key is set lazily here so GCP Secret Manager values
    are always used (not the module-level empty default).
    """
    settings = get_settings()

    if not settings.stripe_api_key:
        raise ValueError("Stripe API key is missing. Cannot create checkout session.")

    # Set lazily so GCP-loaded key is always used
    stripe.api_key = settings.stripe_api_key

    try:
        session = await asyncio.to_thread(
            stripe.checkout.Session.create,
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": settings.stripe_currency,
                        "product_data": {
                            "name": "Nocturn AI Integration & Setup Fee",
                            "description": (
                                "One-time setup fee for custom knowledge base "
                                "and channel integration."
                            ),
                        },
                        "unit_amount": settings.stripe_setup_fee_amount,
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=hotel_id,
        )
        return session.url
    except Exception as e:
        logger.error(f"Failed to create Stripe checkout session: {e}")
        raise
