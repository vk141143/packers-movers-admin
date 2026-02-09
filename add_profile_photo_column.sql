-- Add profile_photo column to crew table
-- Note: This column already exists in your current schema
-- Use this command only if you need to add it to a fresh database

ALTER TABLE crew ADD COLUMN profile_photo VARCHAR(500);

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'crew' AND column_name = 'profile_photo';
