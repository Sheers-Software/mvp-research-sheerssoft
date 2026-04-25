#!/usr/bin/env python3
"""
Master Rebuild Script for Nocturn AI Supabase Database.
Performs the following steps:
1. Ensures 'vector' extension is enabled.
2. Creates all tables defined in `app/models.py`.
3. Applies RLS policies from the initial schema SQL.
4. Seeds the database with demo data (Vivatel KL).

Usage:
    python backend/rebuild_supabase.py
"""

import asyncio
import os
import sys
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.models import Base
from seed_demo_data import seed_demo_data

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def run_rebuild():
    settings = get_settings()
    db_url = os.environ.get("DATABASE_URL_ADMIN") or settings.database_url
    
    if not db_url:
        logger.error("DATABASE_URL not found in environment or settings.")
        sys.exit(1)

    # Ensure we use asyncpg driver for the engine
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    logger.info("Connecting to Supabase (Admin/Postgres)...")
    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            # 1. Enable Extensions
            logger.info("Step 1: Enabling 'vector' extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

            # 2. Apply Core SQL Migrations (Initial Schema + RLS)
            # We run this BEFORE create_all so that core RLS and existing schema are established first.
            logger.info("Step 2: Applying core SQL migrations and RLS policies from initial_schema.sql...")
            migration_path = os.path.join(os.path.dirname(__file__), "supabase/migrations/20260303000000_initial_schema.sql")
            
            if os.path.exists(migration_path):
                # Migration file is UTF-16 Little Endian
                with open(migration_path, "r", encoding="utf-16le") as f:
                    sql_content = f.read()
                
                try:
                    # Run the raw SQL. Since the DB is assumed deleted/clean, this should succeed.
                    await conn.execute(text(sql_content))
                    logger.info("   ✓ Core SQL migration applied.")
                except Exception as sql_err:
                    logger.warning(f"   ⚠ SQL migration warning (might already exist): {sql_err}")
            else:
                logger.error(f"FATAL: Migration file not found at {migration_path}")
                sys.exit(1)

            # 3. Generate Remaining Tables from SQLAlchemy
            # This will create tables that ARE in models.py but NOT in initial_schema.sql (Tenants, Users, etc.)
            logger.info("Step 3: Generating missing tables from SQLAlchemy models...")
            # run_sync for Base.metadata.create_all
            await conn.run_sync(Base.metadata.create_all)
            logger.info("   ✓ All tables finalized.")

            # 4. Grant nocturn_app role permissions on all tables
            # Required so the app's restricted role can read/write after schema rebuild.
            logger.info("Step 4: Granting permissions to nocturn_app role...")
            try:
                await conn.execute(text(
                    "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO nocturn_app"
                ))
                await conn.execute(text(
                    "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nocturn_app"
                ))
                logger.info("   ✓ Permissions granted to nocturn_app.")
            except Exception as grant_err:
                logger.warning(f"   ⚠ Could not grant nocturn_app permissions (role may not exist): {grant_err}")

        # 4. Seed Data
        logger.info("Step 4: Seeding demo data...")
        await seed_demo_data()
        logger.info("   ✓ Demo data seeded.")

        logger.info("\n🎉 Database rebuild complete!")
        logger.info("You can now connect to your new Supabase database.")

    except Exception as e:
        logger.error(f"FATAL: Database rebuild failed: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_rebuild())
