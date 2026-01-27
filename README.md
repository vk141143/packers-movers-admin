# Crew & Admin Management API

FastAPI backend for UK-based Crew & Admin Management platform.

## Project Structure

```
crew_admin_backend/
├── app/
│   ├── core/
│   │   └── security.py          # JWT & password hashing
│   ├── database/
│   │   └── db.py                # Database connection
│   ├── models/
│   │   └── user.py              # User model
│   ├── routers/
│   │   └── auth.py              # Authentication endpoints
│   └── schemas/
│       └── auth.py              # Pydantic schemas
├── main.py                      # Application entry point
├── pyproject.toml               # Poetry dependencies
└── .env.example                 # Environment variables template
```

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Run the application:
```bash
poetry run python main.py
```

The API will be available at `http://localhost:8001`

## API Endpoints

### Authentication

#### Crew Registration
**POST** `/api/auth/register/crew`

Request body:
```json
{
  "email": "crew@example.com",
  "full_name": "John Smith",
  "password": "securepassword"
}
```

#### Admin Registration
**POST** `/api/auth/register/admin`

Request body:
```json
{
  "email": "admin@example.com",
  "full_name": "Jane Doe",
  "password": "securepassword"
}
```

#### Crew Login
**POST** `/api/auth/login/crew`

Request body:
```json
{
  "email": "crew@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Admin Login
**POST** `/api/auth/login/admin`

Request body:
```json
{
  "email": "admin@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Job Verification (Admin)

#### Get Verification Statistics
**GET** `/api/admin/verification/stats`

Returns pending verification count, total value, and average job value.

#### Get All Jobs Pending Verification
**GET** `/api/admin/verification/jobs`

Returns list of all jobs submitted by crew for admin verification.

#### Get Job Verification Details
**GET** `/api/admin/verification/jobs/{job_id}`

Returns detailed job information including before/after photos, checklist status, and crew details.

#### Approve Job Verification
**POST** `/api/admin/verification/jobs/{job_id}/approve`

Request body:
```json
{
  "final_price": 2500.00,
  "rating": 4.5
}
```

Approves the job and marks it as completed.

#### Reject Job Verification
**POST** `/api/admin/verification/jobs/{job_id}/reject`

Rejects the job and sends it back to crew for resubmission.

### Crew Management (Admin)

#### Get Pending Crew Approvals
**GET** `/api/admin/crew/pending`

Returns list of crew members awaiting approval.

#### Approve Crew
**PUT** `/api/admin/crew/{crew_id}/approve`

Approves a crew member for job assignments.

#### Reject Crew
**DELETE** `/api/admin/crew/{crew_id}/reject`

Rejects and removes a crew member.

### Job Management (Admin)

#### Get Active Jobs Dashboard
**GET** `/api/admin/dashboard/active-jobs`

Returns all active jobs with their current status.

#### Get Available Crew
**GET** `/api/admin/crew/available`

Returns list of available crew members for job assignment.

#### Assign Crew to Job
**POST** `/api/admin/jobs/{job_id}/assign-crew/{crew_id}`

Assigns a crew member to a specific job.

### Crew Workflow

#### Get My Jobs
**GET** `/api/crew/jobs`

Returns all jobs assigned to the logged-in crew member.

#### Mark Arrival
**PATCH** `/api/crew/jobs/{job_id}/arrive`

Marks crew as arrived at job location.

#### Upload Before Photos
**POST** `/api/crew/jobs/{job_id}/upload-before-photo`

Uploads before photos of the property.

#### Update Job Checklist
**PATCH** `/api/crew/jobs/{job_id}/checklist`

Updates the job safety checklist.

#### Start Clearance
**PATCH** `/api/crew/jobs/{job_id}/start-clearance`

Marks the start of clearance work.

#### Upload After Photos
**POST** `/api/crew/jobs/{job_id}/upload-after-photo`

Uploads after photos of the completed work.

#### Complete Work
**PATCH** `/api/crew/jobs/{job_id}/complete-work`

Submits the job for admin verification.

## Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Detailed Documentation

- [Job Verification API](./JOB_VERIFICATION_API.md) - Complete guide for admin job verification workflow
