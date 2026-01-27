-- Run this in defaultdb database to create all tables
-- Database: defaultdb
-- Schema: public

-- 1. Clients table
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    full_name VARCHAR,
    company_name VARCHAR,
    phone_number VARCHAR,
    client_type VARCHAR,
    address VARCHAR,
    profile_photo VARCHAR,
    is_verified BOOLEAN DEFAULT FALSE,
    otp VARCHAR,
    otp_expiry TIMESTAMP,
    otp_method VARCHAR,
    reset_otp VARCHAR,
    reset_otp_expiry TIMESTAMP,
    reset_token VARCHAR,
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Admins table
CREATE TABLE IF NOT EXISTS admins (
    id VARCHAR PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    full_name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    reset_otp VARCHAR,
    reset_otp_expiry TIMESTAMP,
    reset_token VARCHAR,
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Crew table
CREATE TABLE IF NOT EXISTS crew (
    id VARCHAR PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    full_name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    phone_number VARCHAR,
    profile_photo VARCHAR,
    drivers_license VARCHAR,
    dbs_certificate VARCHAR,
    proof_of_address VARCHAR,
    insurance_certificate VARCHAR,
    right_to_work VARCHAR,
    is_approved BOOLEAN DEFAULT FALSE,
    status VARCHAR DEFAULT 'pending',
    reset_otp VARCHAR,
    reset_otp_expiry TIMESTAMP,
    reset_token VARCHAR,
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Services table
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Service Levels table
CREATE TABLE IF NOT EXISTS service_levels (
    id VARCHAR PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    sla_hours INTEGER NOT NULL,
    price_gbp INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR PRIMARY KEY,
    client_id VARCHAR,
    service_type VARCHAR NOT NULL,
    service_level VARCHAR NOT NULL,
    vehicle_type VARCHAR,
    property_address TEXT NOT NULL,
    scheduled_date VARCHAR NOT NULL,
    scheduled_time VARCHAR NOT NULL,
    property_photos TEXT,
    price FLOAT NOT NULL,
    additional_notes TEXT,
    status VARCHAR DEFAULT 'job_created',
    assigned_crew_id VARCHAR,
    assigned_by VARCHAR,
    otp VARCHAR,
    otp_verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR,
    verified_at TIMESTAMP,
    rejected_by VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR PRIMARY KEY,
    job_id VARCHAR NOT NULL,
    client_id UUID,
    invoice_number VARCHAR UNIQUE NOT NULL,
    pdf_path VARCHAR,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR DEFAULT 'generated',
    generated_by VARCHAR NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- 8. Job Photos table
CREATE TABLE IF NOT EXISTS job_photos (
    id VARCHAR PRIMARY KEY,
    job_id VARCHAR NOT NULL,
    photo_url VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- 9. Job Checklists table
CREATE TABLE IF NOT EXISTS job_checklists (
    id VARCHAR PRIMARY KEY,
    job_id VARCHAR NOT NULL UNIQUE,
    verify_property_access BOOLEAN DEFAULT FALSE,
    pack_and_remove_items BOOLEAN DEFAULT FALSE,
    clean_property BOOLEAN DEFAULT FALSE,
    get_council_signoff BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default services
INSERT INTO services (name, description) VALUES
    ('Emergency', 'Emergency property clearance services'),
    ('Void Property', 'Void property clearance and cleaning'),
    ('Hoarder Clean', 'Professional hoarder property cleaning'),
    ('Fire/Flood', 'Fire and flood damage clearance')
ON CONFLICT DO NOTHING;

-- Insert default service levels
INSERT INTO service_levels (id, name, sla_hours, price_gbp) VALUES
    (gen_random_uuid()::text, 'emergency_24h', 24, 2500),
    (gen_random_uuid()::text, 'standard_48h', 48, 1800),
    (gen_random_uuid()::text, 'scheduled_5_7_days', 168, 1200)
ON CONFLICT (name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_client_id ON jobs(client_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_assigned_crew ON jobs(assigned_crew_id);
CREATE INDEX IF NOT EXISTS idx_invoices_job_id ON invoices(job_id);
CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_job_photos_job_id ON job_photos(job_id);

PRINT 'All tables created successfully!';
