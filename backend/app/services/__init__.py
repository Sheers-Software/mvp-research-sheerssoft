"""
Services package.

Provides lazy re-exports of Knowledge Base helpers so that modules that
import individual services (e.g. twilio_whatsapp, response_formatter) do
NOT trigger the google-genai / openai client initialisation unless they
actually need the KB functions.

Backward-compatible import sites continue to work unchanged:
    from app.services import ingest_knowledge_base, search_knowledge_base
"""

from __future__ import annotations

_KB_EXPORTS = {"ingest_knowledge_base", "search_knowledge_base", "ingest_document", "generate_embedding"}


def __getattr__(name: str):
    if name in _KB_EXPORTS:
        from app.services import kb as _kb  # lazy import — pulls google.genai only now
        return getattr(_kb, name)
    raise AttributeError(f"module 'app.services' has no attribute {name!r}")
