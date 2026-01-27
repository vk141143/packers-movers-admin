-- Add bank details columns to crew table

-- Add bank_name column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='crew' AND column_name='bank_name') THEN
        ALTER TABLE crew ADD COLUMN bank_name VARCHAR;
    END IF;
END $$;

-- Add account_number column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='crew' AND column_name='account_number') THEN
        ALTER TABLE crew ADD COLUMN account_number VARCHAR;
    END IF;
END $$;

-- Add sort_code column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='crew' AND column_name='sort_code') THEN
        ALTER TABLE crew ADD COLUMN sort_code VARCHAR;
    END IF;
END $$;
