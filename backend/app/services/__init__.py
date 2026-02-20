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
    if settings.gemini_api_key and gemini_client:
        # Use sync client for now as google-genai async support might be complex, 
        # or use the genai client synchronously (it's fast enough for demo)
        response = gemini_client.models.embed_content(
            model=settings.gemini_embedding_model,
            contents=text_content,
        )
        return response.embeddings[0].values
        
    if settings.openai_api_key and openai_client:
        response = await openai_client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text_content,
        )
        return response.data[0].embedding
        
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
        doc_type: One of: rates, rooms, facilities, faqs, directions, policies
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
    Semantic search over a property's knowledge base using pgvector.

    Uses cosine distance for similarity ranking.
    Returns the top `limit` most relevant documents.
    """
    try:
        query_embedding = await generate_embedding(query)

        # pgvector cosine distance operator: <=>
        result = await db.execute(
            select(KBDocument)
            .where(KBDocument.property_id == property_id)
            # Filter low-relevance results (cosine distance < 0.3 approx similarity > 0.7)
            .where(KBDocument.embedding.cosine_distance(query_embedding) < 0.3)
            .order_by(KBDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        return list(result.scalars().all())
    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Knowledge base search failed", error=str(e))
        return []
