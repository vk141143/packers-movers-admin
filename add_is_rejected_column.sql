-- Add is_rejected column to crew table
ALTER TABLE crew ADD COLUMN is_rejected BOOLEAN DEFAULT FALSE;

-- Verify the column was added
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'crew' AND column_name = 'is_rejected';
