"""
Email Service — SendGrid integration with HTML formatting and CC support.

3-tier branching: demo (simulator) → dev (console log) → production (SendGrid API).
"""

import re
import asyncio

import structlog
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Cc

from app.config import get_settings
from app.services.response_formatter import format_response

settings = get_settings()
logger = structlog.get_logger()


# ─── Email HTML Template ──────────────────────────────────

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; line-height: 1.6; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 24px; }}
    .header {{ background: #0f172a; color: white; padding: 20px 24px; border-radius: 10px 10px 0 0; }}
    .header h2 {{ margin: 0; font-size: 18px; }}
    .body {{ background: #ffffff; padding: 24px; border: 1px solid #e2e8f0; }}
    .footer {{ background: #f8fafc; padding: 16px 24px; border-radius: 0 0 10px 10px; font-size: 12px; color: #64748b; border: 1px solid #e2e8f0; border-top: none; }}
    a {{ color: #0f172a; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header"><h2>{hotel_name}</h2></div>
    <div class="body">{body}</div>
    <div class="footer">
      This is an automated response from our AI concierge.<br>
      A member of our team will follow up if needed.
    </div>
  </div>
</body>
</html>
"""


async def send_email(
    to_email: str,
    subject: str,
    content: str,
    is_html: bool = False,
    cc_email: str = None,
    hotel_name: str = "Hotel Concierge",
) -> dict:
    """
    Send an email via SendGrid.
    Applies response formatting for the email channel.
    """
    # Format content for email channel
    formatted = format_response(content, "email")

    # Demo mode: use channel simulator
    if settings.is_demo:
        from app.services.channel_simulator import simulate_channel_send
        return await simulate_channel_send("email", to_email, f"[{subject}] {content[:100]}")

    # Dev mode: console log
    if not settings.sendgrid_api_key:
        if not settings.is_production:
            logger.info("MOCK_EMAIL", to=to_email, subject=subject, content_preview=content[:50])
            return {"status": "mock_sent"}

        logger.warning("SendGrid API key not configured in production", to_email=to_email, subject=subject)
        return {"status": "skipped", "reason": "not_configured"}

    # Build HTML email
    html_body = EMAIL_TEMPLATE.format(
        hotel_name=hotel_name,
        body=formatted,
    )

    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        from_email = Email(settings.sendgrid_from_email)
        to = To(to_email)
        content_obj = Content("text/html", html_body)

        mail = Mail(from_email, to, subject, content_obj)

        # CC reservations team if configured
        if cc_email:
            mail.add_cc(Cc(cc_email))

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, sg.send, mail)

        logger.info("Email sent", to_email=to_email, status_code=response.status_code)
        return {"status": "sent", "status_code": response.status_code}

    except Exception as e:
        logger.error("SendGrid email failed", error=str(e), to_email=to_email)
        return {"status": "error", "detail": str(e)}


async def send_email_reply(
    to_email: str,
    subject: str,
    content: str,
    cc_reservations: bool = True,
    hotel_name: str = "Hotel Concierge",
) -> dict:
    """
    Send an email reply to a guest inquiry, optionally CC'ing the reservations team.
    """
    cc = settings.sendgrid_from_email if cc_reservations and settings.sendgrid_from_email else None

    return await send_email(
        to_email=to_email,
        subject=f"Re: {subject}",
        content=content,
        cc_email=cc,
        hotel_name=hotel_name,
    )


async def notify_staff_handoff(
    property_id: str,
    conversation_id: str,
    guest_identifier: str,
    channel: str,
    guest_name: str | None,
    conversation_summary: str,
):
    """
    Send an email alert to staff when a guest needs human assistance.
    Also publishes to the realtime dashboard.
    """
    subject = f"🚨 HANDOFF ALERT: Guest on {channel.title()}"
    content = (
        f"<p><strong>A guest needs assistance.</strong></p>"
        f"<p>Guest: {guest_name or 'Unknown'} ({guest_identifier})<br>"
        f"Channel: {channel.title()}<br>"
        f"Conversation: <a href='/conversations/{conversation_id}'>View in Dashboard</a></p>"
        f"<p><strong>Context:</strong><br>{conversation_summary}</p>"
        f"<p>Please check the dashboard to reply immediately.</p>"
    )

    # Send email notification
    notification_email = getattr(settings, 'staff_notification_email', settings.sendgrid_from_email)
    if notification_email:
        await send_email(
            to_email=notification_email,
            subject=subject,
            content=content,
            is_html=True,
        )

    # Also publish to realtime dashboard
    try:
        from app.services.realtime import realtime_service
        await realtime_service.publish_handoff(
            property_id=property_id,
            conversation_id=conversation_id,
            guest_name=guest_name or "Guest",
            channel=channel,
            summary=conversation_summary,
        )
    except Exception as e:
        logger.warning("Realtime handoff publish failed", error=str(e))


def normalize_email_message(form_data: dict) -> dict:
    """
    Normalize SendGrid Inbound Parse payload.
    """
    try:
        from_address = form_data.get("from")
        to_address = form_data.get("to")
        subject = form_data.get("subject", "No Subject")
        text = form_data.get("text", "")

        if not text:
            return None

        # Parse Name <email>
        email_match = re.search(r'<([^>]+)>', from_address)
        guest_email = email_match.group(1) if email_match else from_address
        guest_name = from_address.split('<')[0].strip() if '<' in from_address else None

        return {
            "channel": "email",
            "guest_identifier": guest_email,
            "guest_name": guest_name,
            "content": f"Subject: {subject}\n\n{text}",
            "metadata": {
                "to_address": to_address,
                "subject": subject,
            },
        }
    except Exception as e:
        logger.error("Error normalizing email payload", error=str(e))
        return None
