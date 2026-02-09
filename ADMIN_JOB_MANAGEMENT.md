# Admin Job Management Endpoints

## Overview
New endpoints added for admin to reject quote requests and cancel ongoing jobs.

## Endpoints

### 1. Reject Quote Request
**POST** `/api/admin/quotes/{job_id}/reject`

Allows admin to reject a quote request when the job is in `job_created` status.

**Request:**
```
Form Data:
- rejection_reason: string (required)
```

**Response:**
```json
{
  "message": "Quote request rejected successfully",
  "job_id": "uuid",
  "status": "admin_rejected",
  "rejection_reason": "Reason text"
}
```

**Business Logic:**
- Only works for jobs with status `job_created`
- Sets job status to `admin_rejected`
- Stores rejection reason in database

---

### 2. Cancel Job
**POST** `/api/admin/jobs/{job_id}/cancel`

Allows admin to cancel an ongoing job at any stage (except completed/already cancelled).

**Request:**
```
Form Data:
- cancellation_reason: string (required)
```

**Response:**
```json
{
  "message": "Job cancelled successfully",
  "job_id": "uuid",
  "status": "cancelled",
  "cancellation_reason": "Reason text"
}
```

**Business Logic:**
- Cannot cancel jobs with status: `job_completed`, `cancelled`, `admin_rejected`
- If crew was assigned, sets crew status back to `available`
- Sets job status to `cancelled`
- Stores cancellation reason in database

---

### 3. Get Rejected and Cancelled Jobs
**GET** `/api/admin/jobs/rejected-cancelled`

Retrieves all jobs that were rejected or cancelled by admin.

**Response:**
```json
[
  {
    "job_id": "uuid",
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "property_address": "123 Main St",
    "service_type": "Garden Clearance",
    "status": "Quote Rejected" | "Job Cancelled",
    "reason": "Reason text",
    "action_date": "29 Jan 2026"
  }
]
```

**Business Logic:**
- Returns jobs with status `admin_rejected` or `cancelled`
- Shows appropriate status display text
- Includes rejection/cancellation reason
- Ordered by most recent first

---

## Database Changes

### New Columns Added to `jobs` Table:
```sql
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;
```

### New Job Statuses:
- `admin_rejected` - Quote request rejected by admin
- `cancelled` - Job cancelled by admin or client

---

## Use Cases

### Admin Dashboard Workflow:

1. **Quote Management:**
   - Admin receives new quote request (`job_created`)
   - Admin can either:
     - Send quote → `/api/admin/quotes/{job_id}/send`
     - Reject request → `/api/admin/quotes/{job_id}/reject`

2. **Job Management:**
   - Admin can cancel any ongoing job → `/api/admin/jobs/{job_id}/cancel`
   - View all rejected/cancelled jobs → `/api/admin/jobs/rejected-cancelled`

3. **Crew Management:**
   - When job is cancelled, assigned crew automatically becomes available

---

## Integration Notes

- Both endpoints require admin authentication
- Form data is used for reasons (not JSON body)
- Crew status is automatically managed when jobs are cancelled
- All actions are logged with timestamps in `updated_at` field
