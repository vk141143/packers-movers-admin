-- Rename vehicle_registration to vehicle_number in crew table
ALTER TABLE crew RENAME COLUMN vehicle_registration TO vehicle_number;

-- Verify the column was renamed
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'crew' AND column_name = 'vehicle_number';
