-- SQL Migrations for Recent Feature Additions

-- 1. Automated Follow-Up Engine Additions
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS last_interaction_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS follow_up_stage INTEGER DEFAULT 0;

-- Backfill existing conversations assuming last_message_at exists
UPDATE conversations SET last_interaction_at = last_message_at WHERE last_interaction_at IS NULL;

-- 2. Staff Conversion Tracking Additions
-- `status` might already exist on leads depending on prior migrations. 
-- Adding if missing:
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='status') THEN
        ALTER TABLE leads ADD COLUMN status VARCHAR(20) DEFAULT 'new';
    END IF;
END $$;

ALTER TABLE leads ADD COLUMN IF NOT EXISTS actual_revenue NUMERIC(10, 2);

-- 3. Actual Revenue Tracking Additions
ALTER TABLE analytics_daily ADD COLUMN IF NOT EXISTS actual_revenue_recovered NUMERIC(12, 2) DEFAULT 0.00;
