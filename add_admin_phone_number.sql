-- Add phone_number column to admins table

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='admins' AND column_name='phone_number') THEN
        ALTER TABLE admins ADD COLUMN phone_number VARCHAR;
    END IF;
END $$;
