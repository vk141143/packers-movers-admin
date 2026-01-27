# Job Verification System - Visual Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Stats Cards  │  │  Job Cards   │  │ Detail Modal │          │
│  │ - Pending    │  │ - List View  │  │ - Photos     │          │
│  │ - Total $    │  │ - Client     │  │ - Checklist  │          │
│  │ - Avg $      │  │ - Crew       │  │ - Approve    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
└─────────┼─────────────────┼──────────────────┼───────────────────┘
          │                 │                  │
          │ GET /stats      │ GET /jobs        │ GET /jobs/{id}
          │                 │                  │ POST /approve
          │                 │                  │ POST /reject
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Admin Router (admin.py)                     │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Verification Endpoints                            │  │   │
│  │  │  - get_verification_stats()                        │  │   │
│  │  │  - get_jobs_pending_verification()                 │  │   │
│  │  │  - get_job_verification_details()                  │  │   │
│  │  │  - approve_job_verification()                      │  │   │
│  │  │  - reject_job_verification()                       │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              │ JWT Auth Check                    │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Security (security.py)                      │   │
│  │  - get_current_user()                                    │   │
│  │  - Verify admin role                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Jobs       │  │  Job Photos  │  │  Checklist   │          │
│  │ - id         │  │ - job_id     │  │ - job_id     │          │
│  │ - status     │  │ - photo_url  │  │ - completed  │          │
│  │ - price      │  │ - type       │  │ - items      │          │
│  │ - rating     │  │ - timestamp  │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │   Crew       │  │   Clients    │                            │
│  │ - id         │  │ - id         │                            │
│  │ - name       │  │ - name       │                            │
│  │ - status     │  │ - company    │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

### 1. Loading Dashboard

```
┌──────────┐
│ Frontend │
│ Loads    │
└────┬─────┘
     │
     │ 1. GET /api/admin/verification/stats
     ▼
┌──────────────┐
│ Backend      │
│ - Check auth │
│ - Query DB   │
└────┬─────────┘
     │
     │ 2. Query: SELECT COUNT(*), SUM(price) FROM jobs
     │           WHERE status = 'work_completed'
     ▼
┌──────────────┐
│ Database     │
│ Returns data │
└────┬─────────┘
     │
     │ 3. Response: { pending_count: 3, total_value: 9500 }
     ▼
┌──────────────┐
│ Frontend     │
│ Display stats│
└──────────────┘
```

### 2. Viewing Job Details

```
┌──────────┐
│ User     │
│ Clicks   │
│ Job Card │
└────┬─────┘
     │
     │ 1. GET /api/admin/verification/jobs/{job_id}
     ▼
┌──────────────┐
│ Backend      │
│ - Check auth │
│ - Validate   │
└────┬─────────┘
     │
     │ 2. Query job, photos, checklist
     ▼
┌──────────────┐
│ Database     │
│ - Job table  │
│ - Photos     │
│ - Checklist  │
└────┬─────────┘
     │
     │ 3. Response with all data
     ▼
┌──────────────┐
│ Frontend     │
│ Show modal   │
│ - Photos     │
│ - Details    │
└──────────────┘
```

### 3. Approving Job

```
┌──────────┐
│ Admin    │
│ Clicks   │
│ Approve  │
└────┬─────┘
     │
     │ 1. POST /api/admin/verification/jobs/{job_id}/approve
     │    Body: { final_price: 2500, rating: 4.5 }
     ▼
┌──────────────┐
│ Backend      │
│ - Check auth │
│ - Validate   │
└────┬─────────┘
     │
     │ 2. UPDATE jobs SET status='job_completed',
     │                    final_price=2500, rating=4.5
     │    UPDATE crew SET status='available'
     ▼
┌──────────────┐
│ Database     │
│ Updates done │
└────┬─────────┘
     │
     │ 3. Response: { message: "Success", status: "job_completed" }
     ▼
┌──────────────┐
│ Frontend     │
│ - Show toast │
│ - Refresh    │
│ - Update UI  │
└──────────────┘
```

---

## Status State Machine

```
                    ┌─────────────────┐
                    │  job_created    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  quote_sent     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ quote_accepted  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ crew_assigned   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ crew_arrived    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  before_photo   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ clearance_in_   │
                    │   progress      │◄───────┐
                    └────────┬────────┘        │
                             │                 │
                             ▼                 │
                    ┌─────────────────┐        │
                    │  after_photo    │        │
                    └────────┬────────┘        │
                             │                 │
                             ▼                 │
                    ┌─────────────────┐        │
                    │ work_completed  │        │
                    │ (PENDING        │        │
                    │  VERIFICATION)  │        │
                    └────────┬────────┘        │
                             │                 │
                    ┌────────┴────────┐        │
                    │                 │        │
                    ▼                 ▼        │
          ┌─────────────────┐  ┌──────────────┤
          │ job_completed   │  │   REJECTED   │
          │   (APPROVED)    │  └──────────────┘
          └─────────────────┘
```

---

## Component Hierarchy

```
AdminDashboard
│
├── VerificationStats
│   ├── StatCard (Pending Count)
│   ├── StatCard (Total Value)
│   └── StatCard (Avg Value)
│
├── JobVerificationList
│   ├── JobCard
│   │   ├── JobBadge (ID)
│   │   ├── StatusBadge
│   │   ├── ClientInfo
│   │   ├── CrewInfo
│   │   ├── AddressInfo
│   │   ├── ValueDisplay
│   │   └── PhotoCount
│   │
│   └── JobCard (repeated)
│
└── JobDetailModal
    ├── JobHeader
    │   ├── JobID
    │   └── StatusBadge
    │
    ├── JobInfo
    │   ├── ClientName
    │   ├── PropertyAddress
    │   ├── ServiceType
    │   ├── ScheduledDate
    │   └── CrewName
    │
    ├── PhotoGallery (Before)
    │   └── PhotoCard (multiple)
    │
    ├── PhotoGallery (After)
    │   └── PhotoCard (multiple)
    │
    ├── ChecklistStatus
    │   └── CompletionIndicator
    │
    └── ApprovalForm
        ├── FinalPriceInput
        ├── RatingInput
        ├── ApproveButton
        └── RejectButton
```

---

## Database Schema Relationships

```
┌─────────────────────┐
│      Clients        │
│ ─────────────────── │
│ id (PK)             │
│ company_name        │
│ email               │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────┐         ┌─────────────────────┐
│       Jobs          │         │       Crew          │
│ ─────────────────── │         │ ─────────────────── │
│ id (PK)             │◄────────│ id (PK)             │
│ client_id (FK)      │   N:1   │ full_name           │
│ assigned_crew_id(FK)│         │ status              │
│ status              │         │ is_approved         │
│ estimated_price     │         └─────────────────────┘
│ final_price         │
│ rating              │
└──────────┬──────────┘
           │
           │ 1:N
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────┐
│    Job Photos       │  │   Job Checklist     │
│ ─────────────────── │  │ ─────────────────── │
│ id (PK)             │  │ id (PK)             │
│ job_id (FK)         │  │ job_id (FK)         │
│ photo_url           │  │ completed_at        │
│ type (before/after) │  │ access_gained       │
│ timestamp           │  │ waste_verified      │
└─────────────────────┘  │ no_hazardous        │
                         │ property_protected  │
                         │ loading_started     │
                         └─────────────────────┘
```

---

## API Request/Response Flow

### Get Verification Stats

```
REQUEST:
GET /api/admin/verification/stats
Headers: Authorization: Bearer <token>

↓

BACKEND PROCESSING:
1. Verify JWT token
2. Check admin role
3. Query: SELECT COUNT(*), SUM(estimated_price), AVG(estimated_price)
          FROM jobs WHERE status = 'work_completed'
4. Calculate statistics

↓

RESPONSE:
{
  "pending_count": 3,
  "total_value": 9500.00,
  "avg_job_value": 3166.67
}
```

### Approve Job

```
REQUEST:
POST /api/admin/verification/jobs/754714ee.../approve
Headers: Authorization: Bearer <token>
         Content-Type: application/json
Body: {
  "final_price": 2500.00,
  "rating": 4.5
}

↓

BACKEND PROCESSING:
1. Verify JWT token
2. Check admin role
3. Validate job exists
4. Validate status = 'work_completed'
5. Validate rating (1-5)
6. UPDATE jobs SET status='job_completed',
                   final_price=2500,
                   rating=4.5
7. UPDATE crew SET status='available'
8. Commit transaction

↓

RESPONSE:
{
  "message": "Job verified and approved successfully",
  "job_id": "754714ee-e821-48f0-a11c-0ebb61d98cec",
  "final_price": 2500.00,
  "rating": 4.5,
  "status": "job_completed"
}
```

---

## Security Flow

```
┌──────────────┐
│ Client       │
│ Request      │
└──────┬───────┘
       │
       │ Authorization: Bearer <JWT>
       ▼
┌──────────────────┐
│ FastAPI          │
│ Middleware       │
└──────┬───────────┘
       │
       │ Extract token
       ▼
┌──────────────────┐
│ get_current_user │
│ Dependency       │
└──────┬───────────┘
       │
       │ Decode JWT
       │ Verify signature
       │ Check expiration
       ▼
┌──────────────────┐
│ Database         │
│ Query Admin      │
└──────┬───────────┘
       │
       │ Admin found?
       ▼
┌──────────────────┐
│ Endpoint         │
│ Handler          │
└──────┬───────────┘
       │
       │ Process request
       ▼
┌──────────────────┐
│ Response         │
└──────────────────┘
```

---

## Error Handling Flow

```
┌──────────────┐
│ Request      │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Auth Check       │
└──────┬───────────┘
       │
       ├─ No token ──────────► 401 Unauthorized
       │
       ├─ Invalid token ─────► 401 Unauthorized
       │
       ├─ Not admin ─────────► 403 Forbidden
       │
       ▼
┌──────────────────┐
│ Validation       │
└──────┬───────────┘
       │
       ├─ Job not found ─────► 404 Not Found
       │
       ├─ Wrong status ──────► 400 Bad Request
       │
       ├─ Invalid rating ────► 400 Bad Request
       │
       ▼
┌──────────────────┐
│ Process Request  │
└──────┬───────────┘
       │
       ├─ DB error ──────────► 500 Internal Error
       │
       ▼
┌──────────────────┐
│ Success Response │
└──────────────────┘
```

---

## Performance Optimization

```
┌─────────────────────────────────────────────┐
│ Request: Get All Pending Verifications      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Single Query with Filters                   │
│ SELECT * FROM jobs                          │
│ WHERE status = 'work_completed'             │
│ ORDER BY updated_at DESC                    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ For Each Job (in memory):                   │
│ - Lookup client (cached)                    │
│ - Lookup crew (cached)                      │
│ - Count photos (subquery)                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│ Return Formatted Response                   │
└─────────────────────────────────────────────┘

Total DB Queries: 1 main + N client lookups + N crew lookups
Optimization: Add caching for client/crew lookups
```

---

These diagrams provide a complete visual understanding of the job verification system architecture, data flow, and component relationships.
