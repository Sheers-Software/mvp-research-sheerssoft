"""
Knowledge Base service — handles document ingestion and RAG retrieval via pgvector.
"""

import uuid
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
from google import genai

from app.models import KBDocument
from app.config import get_settings

settings = get_settings()

openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

async def generate_embedding(text_content: str) -> list[float]:
    """Generate an embedding vector for a text chunk using Gemini or OpenAI."""
    # Attempt 1: Gemini
    if settings.gemini_api_key and gemini_client:
        try:
            response = gemini_client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=text_content,
            )
            return response.embeddings[0].values
        except Exception:
            pass  # Fall through to OpenAI

    # Attempt 2: OpenAI
    if settings.openai_api_key and openai_client:
        try:
            response = await openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text_content,
            )
            return response.data[0].embedding
        except Exception:
            pass  # Fall through to zero vector

    # Return a zero vector for mock/demo mode to avoid timeouts
    return [0.0] * settings.embedding_dimensions


async def ingest_document(
    db: AsyncSession,
    property_id: uuid.UUID,
    doc_type: str,
    title: str,
    content: str,
) -> KBDocument:
    """
    Ingest a single KB document: generate embedding + store in PostgreSQL.

    Args:
        db: Database session
        property_id: The property this document belongs to
        doc_type: One of the valid document type categories
        title: Short descriptive title
        content: The full text content of the document chunk
    """
    embedding = await generate_embedding(f"{title}\n{content}")

    doc = KBDocument(
        property_id=property_id,
        doc_type=doc_type,
        title=title,
        content=content,
        embedding=embedding,
    )
    db.add(doc)
    await db.flush()
    return doc


async def ingest_knowledge_base(
    db: AsyncSession,
    property_id: uuid.UUID,
    documents: list[dict],
) -> int:
    """
    Bulk ingest a property's knowledge base.

    Args:
        documents: List of dicts with keys: doc_type, title, content

    Returns:
        Number of documents ingested
    """
    # Clear existing KB for this property (full refresh)
    await db.execute(
        text("DELETE FROM kb_documents WHERE property_id = :pid"),
        {"pid": property_id},
    )

    count = 0
    for doc in documents:
        await ingest_document(
            db=db,
            property_id=property_id,
            doc_type=doc["doc_type"],
            title=doc["title"],
            content=doc["content"],
        )
        count += 1

    return count


async def search_knowledge_base(
    db: AsyncSession,
    property_id: uuid.UUID,
    query: str,
    limit: int = 5,
) -> list[KBDocument]:
    """
    Search a property's knowledge base using semantic search with keyword fallback.

    Strategy:
    1. Try pgvector cosine distance (semantic search)
    2. If no results (e.g. zero-vector embeddings), fall back to keyword/ILIKE search
    """
    import structlog
    logger = structlog.get_logger()

    # --- Strategy 1: Semantic search via pgvector ---
    try:
        query_embedding = await generate_embedding(query)
        has_real_embedding = any(v != 0.0 for v in query_embedding[:10])

        if has_real_embedding:
            result = await db.execute(
                select(KBDocument)
                .where(KBDocument.property_id == property_id)
                .where(KBDocument.embedding.cosine_distance(query_embedding) < 0.3)
                .order_by(KBDocument.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            docs = list(result.scalars().all())
            if docs:
                return docs
    except Exception as e:
        logger.warning("Semantic KB search failed, trying keyword fallback", error=str(e))

    # --- Strategy 2: Keyword fallback (ILIKE search on title + content) ---
    try:
        # Extract meaningful keywords from query (skip short/common words)
        stop_words = {"the", "a", "an", "is", "are", "do", "you", "have", "can", "i",
                      "we", "my", "your", "what", "how", "when", "where", "for", "and",
                      "or", "to", "in", "at", "of", "it", "this", "that", "any", "ada",
                      "boleh", "apa", "saya", "nak", "ke", "di", "yang", "ini", "itu"}
        words = [w.strip("?!.,") for w in query.lower().split() if len(w) > 2]
        keywords = [w for w in words if w not in stop_words][:5]  # Max 5 keywords

        if not keywords:
            keywords = words[:3]  # Fallback to raw words if all filtered

        from sqlalchemy import or_
        conditions = []
        for kw in keywords:
            pattern = f"%{kw}%"
            conditions.append(KBDocument.title.ilike(pattern))
            conditions.append(KBDocument.content.ilike(pattern))

        result = await db.execute(
            select(KBDocument)
            .where(KBDocument.property_id == property_id)
            .where(or_(*conditions))
            .limit(limit)
        )
        docs = list(result.scalars().all())
        if docs:
            logger.info("KB keyword fallback returned results", count=len(docs), keywords=keywords)
            return docs
    except Exception as e:
        logger.error("KB keyword fallback also failed", error=str(e))

    return []

