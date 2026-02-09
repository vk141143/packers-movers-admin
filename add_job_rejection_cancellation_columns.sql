-- Add cancellation_reason column to jobs table

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;
