"""
Response Formatter — Adapts AI-generated responses per channel.

Different channels have different constraints:
- WhatsApp: 4096 char limit, no HTML, emojis encouraged
- Email: HTML format, longer responses OK, formal closing
- Web: Markdown-friendly, moderate length
"""

import re
import structlog

logger = structlog.get_logger()


class ResponseFormatter:
    """Format AI responses per-channel for optimal presentation."""

    WHATSAPP_LIMIT = 4096
    WEB_LIMIT = 2000

    @staticmethod
    def for_channel(response: str, channel: str) -> str:
        """Route to the appropriate channel formatter."""
        formatters = {
            "whatsapp": ResponseFormatter.format_whatsapp,
            "email": ResponseFormatter.format_email,
            "web": ResponseFormatter.format_web,
        }
        formatter = formatters.get(channel, ResponseFormatter.format_web)
        return formatter(response)

    @staticmethod
    def format_whatsapp(response: str) -> str:
        """
        WhatsApp formatting:
        - Strip HTML tags
        - Convert markdown bold (**text**) to WhatsApp bold (*text*)
        - Truncate to 4096 chars
        - Preserve emojis
        """
        text = response

        # Strip HTML
        text = re.sub(r'<[^>]+>', '', text)

        # Convert markdown bold **text** to WhatsApp *text*
        text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)

        # Convert markdown headers to bold
        text = re.sub(r'^#{1,3}\s+(.+)$', r'*\1*', text, flags=re.MULTILINE)

        # Convert markdown bullet lists to WhatsApp-friendly format
        text = re.sub(r'^[-*]\s+', '• ', text, flags=re.MULTILINE)

        # Truncate if needed
        if len(text) > ResponseFormatter.WHATSAPP_LIMIT:
            text = text[:ResponseFormatter.WHATSAPP_LIMIT - 50]
            last_sentence = text.rfind('.')
            if last_sentence > len(text) * 0.5:
                text = text[:last_sentence + 1]
            text += "\n\n_(Message truncated. Please call us for details.)_"

        return text.strip()

    @staticmethod
    def format_email(response: str) -> str:
        """
        Email formatting:
        - Keep HTML if present
        - Add paragraph wrapping
        - Add professional closing
        - Longer responses OK
        """
        text = response.strip()

        # Convert line breaks to paragraphs if no HTML present
        if '<p>' not in text and '<br' not in text:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            text = ''.join(f'<p>{p}</p>' for p in paragraphs)

        # Convert remaining single newlines to <br>
        text = text.replace('\n', '<br>')

        # Convert markdown bold to HTML bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        return text

    @staticmethod
    def format_web(response: str) -> str:
        """
        Web widget formatting:
        - Strip HTML for security
        - Keep moderate length
        - Preserve emojis and markdown-style formatting
        """
        text = response

        # Strip HTML for XSS prevention
        text = re.sub(r'<[^>]+>', '', text)

        # Truncate very long responses
        if len(text) > ResponseFormatter.WEB_LIMIT:
            text = text[:ResponseFormatter.WEB_LIMIT - 30]
            last_sentence = text.rfind('.')
            if last_sentence > len(text) * 0.5:
                text = text[:last_sentence + 1]
            text += "\n\n(Ask me for more details!)"

        return text.strip()


def format_response(response: str, channel: str) -> str:
    """Convenience function for formatting AI responses."""
    return ResponseFormatter.for_channel(response, channel)
