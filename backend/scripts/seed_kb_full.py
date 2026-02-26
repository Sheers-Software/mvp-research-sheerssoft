"""
Full Knowledge Base Seeder — Ingests all 3 segments into the demo property.
Uses the existing kb.py ingest function which handles embedding via Gemini or OpenAI fallback.

Segments:
  A: Hotel & Resort (kb_hotel_resort_1/2/3.py)
  B: Homestay, Villa, Chalet, Inn (kb_homestay_villa_1.py)
  C: Malaysian Festive Seasonality (kb_festive_seasonal_1.py)

Usage:
  docker exec mvp-research-sheerssoft-demo-backend-1 python scripts/seed_kb_full.py
"""

import asyncio
import sys
import os
import time

# Ensure app modules are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select, delete, text
from app.database import async_session, engine
from app.models import Property, KBDocument
from app.config import get_settings
from app.services.kb import generate_embedding

# ── Import all KB data files ─────────────────────────────────
from scripts.kb_hotel_resort_1 import DOCS as HOTEL_1
from scripts.kb_hotel_resort_2 import DOCS as HOTEL_2
from scripts.kb_hotel_resort_3 import DOCS as HOTEL_3
from scripts.kb_hotel_resort_4 import DOCS as HOTEL_4
from scripts.kb_hotel_resort_5 import DOCS as HOTEL_5
from scripts.kb_hotel_resort_6 import DOCS as HOTEL_6
from scripts.kb_hotel_resort_7 import DOCS as HOTEL_7
from scripts.kb_hotel_resort_8 import DOCS as HOTEL_8
from scripts.kb_hotel_resort_9 import DOCS as HOTEL_9
from scripts.kb_hotel_resort_10 import DOCS as HOTEL_10
from scripts.kb_hotel_resort_11 import DOCS as HOTEL_11
from scripts.kb_hotel_resort_12 import DOCS as HOTEL_12
from scripts.kb_hotel_resort_13 import DOCS as HOTEL_13
from scripts.kb_hotel_resort_14 import DOCS as HOTEL_14
from scripts.kb_hotel_resort_15 import DOCS as HOTEL_15
from scripts.kb_hotel_resort_16 import DOCS as HOTEL_16
from scripts.kb_hotel_resort_17 import DOCS as HOTEL_17
from scripts.kb_hotel_resort_18 import DOCS as HOTEL_18
from scripts.kb_hotel_resort_19 import DOCS as HOTEL_19
from scripts.kb_homestay_villa_1 import DOCS as HOMESTAY_1
from scripts.kb_homestay_villa_2 import DOCS as HOMESTAY_2
from scripts.kb_homestay_villa_3 import DOCS as HOMESTAY_3
from scripts.kb_homestay_villa_4 import DOCS as HOMESTAY_4
from scripts.kb_homestay_villa_5 import DOCS as HOMESTAY_5
from scripts.kb_homestay_villa_6 import DOCS as HOMESTAY_6
from scripts.kb_homestay_villa_7 import DOCS as HOMESTAY_7
from scripts.kb_homestay_villa_8 import DOCS as HOMESTAY_8
from scripts.kb_homestay_villa_9 import DOCS as HOMESTAY_9
from scripts.kb_homestay_villa_10 import DOCS as HOMESTAY_10
from scripts.kb_festive_seasonal_1 import DOCS as FESTIVE_1
from scripts.kb_festive_seasonal_2 import DOCS as FESTIVE_2
from scripts.kb_festive_seasonal_3 import DOCS as FESTIVE_3
from scripts.kb_festive_seasonal_4 import DOCS as FESTIVE_4
from scripts.kb_festive_seasonal_5 import DOCS as FESTIVE_5
from scripts.kb_festive_seasonal_6 import DOCS as FESTIVE_6
from scripts.kb_festive_seasonal_7 import DOCS as FESTIVE_7
from scripts.kb_festive_seasonal_8 import DOCS as FESTIVE_8
from scripts.kb_festive_seasonal_9 import DOCS as FESTIVE_9
from scripts.kb_general_faqs_1 import DOCS as FAQS_1

ALL_SEGMENTS = [
    ("Segment A — Hotel & Resort (Part 1)",  HOTEL_1),
    ("Segment A — Hotel & Resort (Part 2)",  HOTEL_2),
    ("Segment A — Hotel & Resort (Part 3)",  HOTEL_3),
    ("Segment A — Hotel & Resort (Part 4)",  HOTEL_4),
    ("Segment A — Hotel & Resort (Part 5)",  HOTEL_5),
    ("Segment A — Hotel & Resort (Part 6)",  HOTEL_6),
    ("Segment A — Hotel & Resort (Part 7)",  HOTEL_7),
    ("Segment A — Hotel & Resort (Part 8)",  HOTEL_8),
    ("Segment A — Hotel & Resort (Part 9)",  HOTEL_9),
    ("Segment A — Hotel & Resort (Part 10)", HOTEL_10),
    ("Segment A — Hotel & Resort (Part 11)", HOTEL_11),
    ("Segment A — Hotel & Resort (Part 12)", HOTEL_12),
    ("Segment A — Hotel & Resort (Part 13)", HOTEL_13),
    ("Segment A — Hotel & Resort (Part 14)", HOTEL_14),
    ("Segment A — Hotel & Resort (Part 15)", HOTEL_15),
    ("Segment A — Hotel & Resort (Part 16)", HOTEL_16),
    ("Segment A — Hotel & Resort (Part 17)", HOTEL_17),
    ("Segment A — Hotel & Resort (Part 18)", HOTEL_18),
    ("Segment A — Hotel & Resort (Part 19)", HOTEL_19),
    ("Segment B — Homestay / Villa (Part 1)", HOMESTAY_1),
    ("Segment B — Homestay / Villa (Part 2)", HOMESTAY_2),
    ("Segment B — Homestay / Villa (Part 3)", HOMESTAY_3),
    ("Segment B — Homestay / Villa (Part 4)", HOMESTAY_4),
    ("Segment B — Homestay / Villa (Part 5)", HOMESTAY_5),
    ("Segment B — Homestay / Villa (Part 6)", HOMESTAY_6),
    ("Segment B — Homestay / Villa (Part 7)", HOMESTAY_7),
    ("Segment B — Homestay / Villa (Part 8)", HOMESTAY_8),
    ("Segment B — Homestay / Villa (Part 9)", HOMESTAY_9),
    ("Segment B — Homestay / Villa (Part 10)", HOMESTAY_10),
    ("Segment C — Festive Season (Part 1)",  FESTIVE_1),
    ("Segment C — Festive Season (Part 2)",  FESTIVE_2),
    ("Segment C — Festive Season (Part 3)",  FESTIVE_3),
    ("Segment C — Festive Season (Part 4)",  FESTIVE_4),
    ("Segment C — Festive Season (Part 5)",  FESTIVE_5),
    ("Segment C — Festive Season (Part 6)",  FESTIVE_6),
    ("Segment C — Festive Season (Part 7)",  FESTIVE_7),
    ("Segment C — Festive Season (Part 8)",  FESTIVE_8),
    ("Segment C — Festive Season (Part 9)",  FESTIVE_9),
    ("Segment D — General FAQs (Part 1)",    FAQS_1),
]


async def seed_kb():
    settings = get_settings()
    print(f"Embedding model: {settings.gemini_embedding_model} (Gemini) / {settings.openai_embedding_model} (OpenAI fallback)")

    async with async_session() as db:
        # 1. Find demo property
        result = await db.execute(select(Property).limit(1))
        prop = result.scalar_one_or_none()
        if not prop:
            print("No property found. Run seed_demo_data.py first.")
            sys.exit(1)

        print(f"Property: {prop.name} ({prop.id})")

        # 2. Clear existing KB
        deleted = await db.execute(
            delete(KBDocument).where(KBDocument.property_id == prop.id)
        )
        await db.flush()
        print(f"Cleared {deleted.rowcount} existing KB documents")

        # 3. Ingest all segments
        total = 0
        failed = 0
        segment_stats = {}

        for segment_name, docs in ALL_SEGMENTS:
            print(f"\n--- {segment_name} ({len(docs)} docs) ---")
            segment_count = 0

            for i, doc in enumerate(docs):
                embed_text = f"{doc['title']}\n{doc['content']}"

                if i > 0 and i % 5 == 0:
                    print(f"   [{i}/{len(docs)}] processing...")
                    await asyncio.sleep(0.1)

                try:
                    embedding = await generate_embedding(embed_text)
                    has_embedding = embedding and any(v != 0.0 for v in embedding[:5])
                except Exception as e:
                    print(f"   Embedding error at [{i}]: {e}")
                    embedding = [0.0] * settings.embedding_dimensions
                    has_embedding = False

                kb_doc = KBDocument(
                    property_id=prop.id,
                    doc_type=doc["doc_type"],
                    title=doc["title"],
                    content=doc["content"],
                    embedding=embedding,
                )
                db.add(kb_doc)
                segment_count += 1
                total += 1
                if not has_embedding:
                    failed += 1
                
                # Intermediate flush every 50 docs to keep transaction manageable
                if total % 50 == 0:
                    await db.flush()

            # Commit after each segment
            await db.commit()
            print(f"   Committed segment: {segment_name}")
            segment_stats[segment_name] = segment_count

        # 4. Report
        print("\n" + "=" * 60)
        print("Knowledge Base Seeding Complete!")
        print("=" * 60)
        for seg, count in segment_stats.items():
            print(f"   {seg}: {count} docs")
        print(f"\n   Total documents ingested: {total}")
        print(f"   With embeddings: {total - failed}")
        print(f"   Without embeddings (zero vector): {failed}")
        print("=" * 60)


        print("\nAll segments committed successfully.")
        return 0


if __name__ == "__main__":
    start = time.time()
    try:
        asyncio.run(seed_kb())
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)
    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f} seconds")
