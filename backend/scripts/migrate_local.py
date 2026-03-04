"""Run the migration SQL on local docker postgres."""
import asyncio
import asyncpg

DB_URL = "postgresql://sheerssoft:sheerssoft_dev_password@localhost:5433/sheerssoft"

MIGRATION_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL, subscription_tier VARCHAR(20) NOT NULL DEFAULT 'pilot',
    subscription_status VARCHAR(20) NOT NULL DEFAULT 'trialing',
    pilot_start_date TIMESTAMPTZ, pilot_end_date TIMESTAMPTZ,
    stripe_customer_id VARCHAR(255), assigned_account_manager VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL, phone VARCHAR(30),
    is_superadmin BOOLEAN NOT NULL DEFAULT FALSE, last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS tenant_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id), tenant_id UUID NOT NULL REFERENCES tenants(id),
    role VARCHAR(20) NOT NULL DEFAULT 'staff', accessible_property_ids JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), CONSTRAINT uq_user_tenant UNIQUE (user_id, tenant_id)
);
CREATE INDEX IF NOT EXISTS ix_membership_tenant ON tenant_memberships(tenant_id);
CREATE INDEX IF NOT EXISTS ix_membership_user ON tenant_memberships(user_id);

CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL, whatsapp_number VARCHAR(20),
    whatsapp_provider VARCHAR(20) NOT NULL DEFAULT 'meta', twilio_phone_number VARCHAR(20),
    notification_email VARCHAR(255), website_url VARCHAR(500),
    operating_hours JSONB, knowledge_base_config JSONB,
    adr NUMERIC(10,2) DEFAULT 230.00, ota_commission_pct NUMERIC(5,2) DEFAULT 20.00,
    conversion_rate NUMERIC(5,2) NOT NULL DEFAULT 0.20, hourly_rate NUMERIC(10,2) NOT NULL DEFAULT 25.00,
    brand_vocabulary TEXT, required_questions JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    slug VARCHAR(255) UNIQUE, timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Kuala_Lumpur',
    plan_tier VARCHAR(20) NOT NULL DEFAULT 'pilot', is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), property_id UUID NOT NULL REFERENCES properties(id),
    channel VARCHAR(20) NOT NULL, guest_identifier VARCHAR(255), guest_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active', is_after_hours BOOLEAN DEFAULT FALSE,
    ai_mode VARCHAR(20) DEFAULT 'concierge',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_interaction_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    follow_up_stage INTEGER NOT NULL DEFAULT 0, ended_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ,
    message_count INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role VARCHAR(10) NOT NULL, content TEXT NOT NULL, metadata JSONB,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    property_id UUID NOT NULL REFERENCES properties(id),
    guest_name VARCHAR(255), guest_phone VARCHAR(20), guest_email VARCHAR(255),
    intent VARCHAR(30) DEFAULT 'general', source_channel VARCHAR(20),
    is_after_hours BOOLEAN, status VARCHAR(20) DEFAULT 'new',
    estimated_value NUMERIC(10,2), actual_revenue NUMERIC(10,2),
    notes TEXT, priority VARCHAR(20) NOT NULL DEFAULT 'standard', flag_reason VARCHAR(255),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), deleted_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS kb_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    doc_type VARCHAR(30) NOT NULL, title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL, embedding vector(768),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    report_date DATE NOT NULL, total_inquiries INTEGER DEFAULT 0,
    after_hours_inquiries INTEGER DEFAULT 0, after_hours_responded INTEGER DEFAULT 0,
    leads_captured INTEGER DEFAULT 0, handoffs INTEGER DEFAULT 0,
    inquiries_handled_by_ai INTEGER DEFAULT 0, inquiries_handled_manually INTEGER DEFAULT 0,
    avg_response_time_sec NUMERIC(8,2) DEFAULT 0,
    estimated_revenue_recovered NUMERIC(12,2) DEFAULT 0,
    actual_revenue_recovered NUMERIC(12,2) DEFAULT 0, cost_savings NUMERIC(12,2) DEFAULT 0,
    channel_breakdown JSONB,
    CONSTRAINT ix_analytics_property_date UNIQUE (property_id, report_date)
);
CREATE TABLE IF NOT EXISTS onboarding_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id), property_id UUID NOT NULL REFERENCES properties(id),
    whatsapp_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    email_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    website_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    kb_populated BOOLEAN NOT NULL DEFAULT FALSE,
    first_inquiry_received BOOLEAN NOT NULL DEFAULT FALSE,
    first_lead_captured BOOLEAN NOT NULL DEFAULT FALSE,
    first_morning_report_sent BOOLEAN NOT NULL DEFAULT FALSE,
    owner_first_login BOOLEAN NOT NULL DEFAULT FALSE,
    channel_errors JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_onboarding_tenant_property UNIQUE (tenant_id, property_id)
);
CREATE TABLE IF NOT EXISTS support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    created_by_user_id UUID NOT NULL REFERENCES users(id),
    subject VARCHAR(500) NOT NULL, description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open', priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    assigned_to_user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_name VARCHAR(255) NOT NULL, contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL, phone VARCHAR(30), property_name VARCHAR(255),
    room_count INTEGER, current_channels JSONB, message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'new', notes TEXT,
    converted_to_tenant_id UUID REFERENCES tenants(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SELECT 'Local migration complete' AS status;
"""

async def main():
    print("Connecting to local postgres...")
    conn = await asyncpg.connect(DB_URL)
    print("Running migration...")
    await conn.execute(MIGRATION_SQL)
    tables = await conn.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    )
    print(f"\nTables ({len(tables)}):")
    for t in tables:
        print(f"  ✅ {t['table_name']}")
    await conn.close()
    print("\n✅ Local migration complete!")

if __name__ == "__main__":
    asyncio.run(main())
