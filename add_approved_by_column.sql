-- Add approved_by column to crew table to track which admin approved the crew
ALTER TABLE crew ADD COLUMN approved_by VARCHAR(255);

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'crew' AND column_name = 'approved_by';
