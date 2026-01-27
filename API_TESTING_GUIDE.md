# API Testing Guide - Verify & Generate Invoice

## Quick Test Commands

### 1. Admin Login (Get Token)

```bash
curl -X POST http://localhost:8001/api/auth/login/admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

**Save the access_token for next steps!**

---

### 2. Get Job Details for Verification

```bash
curl -X GET http://localhost:8001/api/admin/jobs/{JOB_ID}/verification \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Replace:**
- `{JOB_ID}` with actual job ID
- `YOUR_ACCESS_TOKEN` with token from step 1

**Response:**
```json
{
  "job_id": "f0db35cf-f3a7-4c58-8eb0-0392e6a1001d",
  "service_type": "Emergency",
  "sla_level": "emergency_24h",
  "scheduled_date": "2024-01-15",
  "before_photos": [
    "http://localhost:8001/uploads/job_photos/before_1.jpg"
  ],
  "after_photos": [
    "http://localhost:8001/uploads/job_photos/after_1.jpg"
  ]
}
```

---

### 3. Verify & Generate Invoice (NEW - Single Button)

```bash
curl -X POST http://localhost:8001/api/admin/jobs/{JOB_ID}/verify-and-generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Success Response:**
```json
{
  "success": true,
  "message": "Job verified, invoice generated, and job completed",
  "job_id": "f0db35cf-f3a7-4c58-8eb0-0392e6a1001d",
  "status": "job_completed",
  "invoice_id": "abc123-def456",
  "invoice_number": "INV-f0db35cf",
  "verified_by": "admin-id-123",
  "verified_at": "2024-01-15T10:30:00"
}
```

**Error Response (Missing Photos):**
```json
{
  "detail": "Before and after photos are required"
}
```

**Error Response (Wrong Status):**
```json
{
  "detail": "Job must be in pending_verification status"
}
```

---

### 4. Verify Status from Client Side

```bash
# First, login as client
curl -X POST http://localhost:8000/api/auth/login/client \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "password": "your-password"
  }'

# Then check job status
curl -X GET http://localhost:8000/api/jobs/{JOB_ID} \
  -H "Authorization: Bearer CLIENT_ACCESS_TOKEN"
```

**Response:**
```json
{
  "id": "f0db35cf-f3a7-4c58-8eb0-0392e6a1001d",
  "client_id": "client-uuid",
  "service_type": "Emergency",
  "service_level": "emergency_24h",
  "status": "job_completed",  ← Updated!
  "price": 2500.0,
  "created_at": "2024-01-15T08:00:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

### 5. Check Invoice History (Client)

```bash
curl -X GET http://localhost:8000/api/client/invoices \
  -H "Authorization: Bearer CLIENT_ACCESS_TOKEN"
```

**Response:**
```json
{
  "invoices": [
    {
      "invoice_number": "INV-f0db35cf",
      "job_id": "f0db35cf-f3a7-4c58-8eb0-0392e6a1001d",
      "amount": 2500.0,
      "status": "generated",
      "generated_at": "2024-01-15T10:30:00",
      "action": "/api/client/invoices/abc123-def456/download"
    }
  ]
}
```

---

## Alternative: Old Endpoints (Still Work)

### Step-by-Step Approach

#### Step 1: Verify Only
```bash
curl -X PATCH http://localhost:8001/api/admin/jobs/{JOB_ID}/verify \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "Job verified by admin",
  "job_id": "...",
  "verified_by": "admin-id",
  "status": "admin_verified"
}
```

#### Step 2: Generate Invoice Only
```bash
curl -X PATCH http://localhost:8001/api/admin/jobs/{JOB_ID}/generate-invoice \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "Invoice generated and sent",
  "job_id": "...",
  "invoice_id": "...",
  "invoice_number": "INV-12345678",
  "status": "invoice_generated"
}
```

#### Step 3: Complete Only
```bash
curl -X PATCH http://localhost:8001/api/admin/jobs/{JOB_ID}/complete \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "Job completed",
  "job_id": "...",
  "status": "job_completed"
}
```

---

## Postman Collection

### Import this JSON into Postman:

```json
{
  "info": {
    "name": "Verify & Generate Invoice",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Admin Login",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"admin@example.com\",\n  \"password\": \"your-password\"\n}"
        },
        "url": {
          "raw": "http://localhost:8001/api/auth/login/admin",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8001",
          "path": ["api", "auth", "login", "admin"]
        }
      }
    },
    {
      "name": "2. Get Job Verification Details",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{admin_token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8001/api/admin/jobs/{{job_id}}/verification",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8001",
          "path": ["api", "admin", "jobs", "{{job_id}}", "verification"]
        }
      }
    },
    {
      "name": "3. Verify & Generate Invoice",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{admin_token}}"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "url": {
          "raw": "http://localhost:8001/api/admin/jobs/{{job_id}}/verify-and-generate",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8001",
          "path": ["api", "admin", "jobs", "{{job_id}}", "verify-and-generate"]
        }
      }
    },
    {
      "name": "4. Client - Check Job Status",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{client_token}}"
          }
        ],
        "url": {
          "raw": "http://localhost:8000/api/jobs/{{job_id}}",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "jobs", "{{job_id}}"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "admin_token",
      "value": "YOUR_ADMIN_TOKEN_HERE"
    },
    {
      "key": "client_token",
      "value": "YOUR_CLIENT_TOKEN_HERE"
    },
    {
      "key": "job_id",
      "value": "YOUR_JOB_ID_HERE"
    }
  ]
}
```

---

## Testing Scenarios

### Scenario 1: Happy Path ✅

```bash
# 1. Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login/admin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Verify and generate
curl -X POST http://localhost:8001/api/admin/jobs/JOB_ID/verify-and-generate \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. Check status as client
CLIENT_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/client \
  -H "Content-Type: application/json" \
  -d '{"email":"client@example.com","password":"password"}' \
  | jq -r '.access_token')

curl -X GET http://localhost:8000/api/jobs/JOB_ID \
  -H "Authorization: Bearer $CLIENT_TOKEN"
```

**Expected:** Status = "job_completed", invoice created

---

### Scenario 2: Missing Photos ❌

```bash
# Try to verify job without photos
curl -X POST http://localhost:8001/api/admin/jobs/JOB_ID/verify-and-generate \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected:** 400 error - "Before and after photos are required"

---

### Scenario 3: Wrong Status ❌

```bash
# Try to verify already completed job
curl -X POST http://localhost:8001/api/admin/jobs/COMPLETED_JOB_ID/verify-and-generate \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected:** 400 error - "Job must be in pending_verification status"

---

### Scenario 4: Unauthorized ❌

```bash
# Try without token
curl -X POST http://localhost:8001/api/admin/jobs/JOB_ID/verify-and-generate
```

**Expected:** 401 error - "Not authenticated"

---

## Database Verification

### Check Job Status in Database

```sql
-- Connect to PostgreSQL
psql -h public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com \
     -U dbadmin -d defaultdb

-- Check job status
SELECT id, status, verified_by, verified_at 
FROM jobs 
WHERE id = 'YOUR_JOB_ID';

-- Check invoice
SELECT id, job_id, invoice_number, amount, generated_by 
FROM invoices 
WHERE job_id = 'YOUR_JOB_ID';
```

**Expected After Verify & Generate:**
```
Jobs Table:
- status: job_completed
- verified_by: admin-id
- verified_at: timestamp

Invoices Table:
- job_id: matches job id
- invoice_number: INV-xxxxxxxx
- amount: job price
- generated_by: admin-id
```

---

## Troubleshooting

### Issue: "Job not found"

**Check:**
```bash
# List all jobs
curl -X GET http://localhost:8001/api/admin/jobs \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Issue: "Admin access required"

**Check:**
```bash
# Verify token is valid
curl -X GET http://localhost:8001/api/admin/jobs \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Issue: "Before and after photos are required"

**Check:**
```bash
# Get job photos
curl -X GET http://localhost:8001/api/admin/jobs/JOB_ID/photos \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Issue: Client doesn't see updated status

**Check:**
1. Verify both backends use same database
2. Check database connection
3. Refresh client query
4. Check for caching issues

---

## Performance Testing

### Load Test with Apache Bench

```bash
# Test 100 requests with 10 concurrent
ab -n 100 -c 10 \
   -H "Authorization: Bearer $ADMIN_TOKEN" \
   -p /dev/null \
   http://localhost:8001/api/admin/jobs/JOB_ID/verify-and-generate
```

**Expected:**
- Average response time: <500ms
- Success rate: >99%
- No database errors

---

## Monitoring

### Check Backend Logs

```bash
# Crew Admin Backend
tail -f crew_admin_backend/logs/app.log

# Client Backend
tail -f client_backend/logs/app.log
```

### Check Database Connections

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long running queries
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
```

---

## Summary

✅ **New Endpoint:** `POST /api/admin/jobs/{job_id}/verify-and-generate`  
✅ **Single Action:** Verify + Invoice + Complete  
✅ **Atomic:** All or nothing transaction  
✅ **Real-time:** Client sees update immediately  
✅ **Backward Compatible:** Old endpoints still work  

**Test it now!** 🚀
