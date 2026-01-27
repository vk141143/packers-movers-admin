-- Remove bank details and profile_photo columns from crew table
ALTER TABLE crew DROP COLUMN IF EXISTS bank_name;
ALTER TABLE crew DROP COLUMN IF EXISTS account_number;
ALTER TABLE crew DROP COLUMN IF EXISTS sort_code;
ALTER TABLE crew DROP COLUMN IF EXISTS profile_photo;

-- Add address column
ALTER TABLE crew ADD COLUMN IF NOT EXISTS address TEXT;
