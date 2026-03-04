-- Add stripe_subscription_id to tenants for subscription lifecycle tracking
ALTER TABLE tenants
    ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);
