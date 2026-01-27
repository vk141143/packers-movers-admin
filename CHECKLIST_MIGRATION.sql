-- Update job_checklists table structure
-- Run this on crew_admin_backend database

-- Drop old columns
ALTER TABLE job_checklists DROP COLUMN IF EXISTS pack_and_remove_items;
ALTER TABLE job_checklists DROP COLUMN IF EXISTS clean_property;

-- Add new columns
ALTER TABLE job_checklists ADD COLUMN IF NOT EXISTS document_property_condition BOOLEAN DEFAULT FALSE;
ALTER TABLE job_checklists ADD COLUMN IF NOT EXISTS remove_all_items_urgently BOOLEAN DEFAULT FALSE;
ALTER TABLE job_checklists ADD COLUMN IF NOT EXISTS secure_property BOOLEAN DEFAULT FALSE;
ALTER TABLE job_checklists ADD COLUMN IF NOT EXISTS deep_clean_property BOOLEAN DEFAULT FALSE;
ALTER TABLE job_checklists ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;

-- Rename column
ALTER TABLE job_checklists RENAME COLUMN get_council_signoff TO get_council_signoff;

COMMENT ON COLUMN job_checklists.completed_at IS 'Timestamp when all checklist items were completed';
