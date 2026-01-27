# Complete Job Workflow - Implementation Summary

## ✅ Job Status Flow

```
1. DRAFT → Client creates job
2. BOOKED → Client confirms booking
3. CREW_DISPATCHED → Admin assigns crew (auto/manual)
4. ARRIVED_AT_PICKUP → Crew arrives at property
5. WORK_IN_PROGRESS → OTP verified, work starts
6. LOADING_COMPLETED → Packing done, checklist complete
7. ARRIVED_AT_DELIVERY → Crew reaches delivery location
8. COMPLETED → Job submitted for verification
9. VERIFIED → Admin approves, invoice generated
10. REJECTED → Admin rejects, sent back
```

---

## 📋 Crew Workflow Endpoints

### 1. Update Job Status
**POST** `/api/crew/jobs/{job_id}/update-status`

**Body:**
```json
{
  "status": "arrived_at_pickup"
}
```

**Valid Statuses:**
- `arrived_at_pickup` - Crew reached pickup location
- `work_in_progress` - Work started (after OTP)
- `loading_completed` - Packing complete
- `arrived_at_delivery` - Reached delivery location
- `completed` - Job done

---

### 2. Generate OTP (Start Work)
**POST** `/api/crew/jobs/{job_id}/generate-otp`

**Purpose:** Generate 4-digit OTP and send to client email

**Response:**
```json
{
  "message": "OTP generated and sent to client",
  "job_id": "uuid",
  "otp": "1234"
}
```

---

### 3. Verify OTP
**POST** `/api/crew/jobs/{job_id}/verify-otp`

**Body:**
```json
{
  "otp": "1234"
}
```

**Action:** Verifies OTP, updates status to `work_in_progress`

---

### 4. Upload Photos (Multiple)
**POST** `/api/crew/jobs/{job_id}/upload-photos`

**Body:**
```json
{
  "photo_urls": [
    "https://example.com/photo1.jpg",
    "https://example.com/photo2.jpg",
    "https://example.com/photo3.jpg"
  ],
  "type": "before"
}
```

**Types:**
- `before` - Before photos at pickup
- `after` - After photos at delivery

**Supports multiple photos per upload**

---

### 5. Get Checklist
**GET** `/api/crew/jobs/{job_id}/checklist`

**Returns:**
```json
[
  {
    "id": "uuid",
    "item_name": "Verify property access",
    "is_completed": false,
    "completed_at": null
  },
  {
    "id": "uuid",
    "item_name": "Pack and remove all items",
    "is_completed": false,
    "completed_at": null
  },
  {
    "id": "uuid",
    "item_name": "Clean property",
    "is_completed": false,
    "completed_at": null
  },
  {
    "id": "uuid",
    "item_name": "Get council sign-off",
    "is_completed": false,
    "completed_at": null
  }
]
```

---

### 6. Complete Checklist Item
**POST** `/api/crew/jobs/{job_id}/checklist/{item_id}/complete`

**Action:** Marks checklist item as completed with timestamp

---

### 7. Submit for Verification
**POST** `/api/crew/jobs/{job_id}/submit-for-verification`

**Validation:**
- All checklist items must be completed
- Before photos must exist
- After photos must exist

**Action:**
- Updates status to `completed`
- Sets crew status to `available`
- Job ready for admin verification

---

## 🔄 Complete Workflow Steps

### Step 1: Client Creates Job
- Status: `DRAFT` → `BOOKED`

### Step 2: Admin Assigns Crew
- **POST** `/api/jobs/{job_id}/assign-crew` or `/api/jobs/{job_id}/auto-assign`
- Status: `CREW_DISPATCHED`

### Step 3: Crew Arrives at Pickup
- **POST** `/api/crew/jobs/{job_id}/update-status`
- Body: `{"status": "arrived_at_pickup"}`

### Step 4: Upload Before Photos
- **POST** `/api/crew/jobs/{job_id}/upload-photos`
- Body: `{"photo_urls": [...], "type": "before"}`

### Step 5: Generate & Verify OTP
- **POST** `/api/crew/jobs/{job_id}/generate-otp`
- Client receives 4-digit OTP via email
- **POST** `/api/crew/jobs/{job_id}/verify-otp`
- Body: `{"otp": "1234"}`
- Status: `WORK_IN_PROGRESS`

### Step 6: Complete Checklist
- **GET** `/api/crew/jobs/{job_id}/checklist`
- **POST** `/api/crew/jobs/{job_id}/checklist/{item_id}/complete` (for each item)
  - ✅ Verify property access
  - ✅ Pack and remove all items
  - ✅ Clean property
  - ✅ Get council sign-off

### Step 7: Loading Complete
- **POST** `/api/crew/jobs/{job_id}/update-status`
- Body: `{"status": "loading_completed"}`

### Step 8: Arrive at Delivery
- **POST** `/api/crew/jobs/{job_id}/update-status`
- Body: `{"status": "arrived_at_delivery"}`

### Step 9: Upload After Photos
- **POST** `/api/crew/jobs/{job_id}/upload-photos`
- Body: `{"photo_urls": [...], "type": "after"}`

### Step 10: Submit for Verification
- **POST** `/api/crew/jobs/{job_id}/submit-for-verification`
- Status: `COMPLETED`
- Crew: `AVAILABLE`

### Step 11: Admin Verifies
- **GET** `/api/admin/jobs/{job_id}/verification`
- **POST** `/api/admin/jobs/{job_id}/verify`
- Status: `VERIFIED`
- Invoice auto-generated

---

## 🗂️ Database Changes

### Job Model - New Fields:
- `otp` - 4-digit OTP code
- `otp_verified` - Boolean
- `otp_verified_at` - Timestamp

### Job Model - New Statuses:
- `CREW_DISPATCHED`
- `ARRIVED_AT_PICKUP`
- `WORK_IN_PROGRESS`
- `LOADING_COMPLETED`
- `ARRIVED_AT_DELIVERY`

---

## 📸 Photo Upload

**Multiple photos supported:**
- Before photos: Upload multiple at pickup location
- After photos: Upload multiple at delivery location
- Each photo stored with URL, type, and timestamp

---

## ✅ Checklist Items

**Default checklist (4 items):**
1. Verify property access
2. Pack and remove all items
3. Clean property
4. Get council sign-off

**Crew marks each as complete**
**Admin verifies all completed before approval**

---

## 🔐 Security

- All endpoints require JWT authentication
- Crew can only access their assigned jobs
- Admin can access all jobs
- OTP verification required before work starts

---

## 🚀 Next Steps

1. Delete database: `rm crew_admin.db`
2. Restart server: `poetry run python main.py`
3. Test complete workflow from job creation to invoice generation

---

## 📊 API Summary

**Crew Endpoints (8):**
- POST /api/crew/jobs/{job_id}/update-status
- POST /api/crew/jobs/{job_id}/generate-otp
- POST /api/crew/jobs/{job_id}/verify-otp
- POST /api/crew/jobs/{job_id}/upload-photos
- GET /api/crew/jobs/{job_id}/checklist
- POST /api/crew/jobs/{job_id}/checklist/{item_id}/complete
- POST /api/crew/jobs/{job_id}/submit-for-verification
- GET /api/crew/jobs

**Admin Endpoints:**
- GET /api/admin/jobs/{job_id}/verification
- POST /api/admin/jobs/{job_id}/verify
- POST /api/admin/jobs/{job_id}/reject
- GET /api/admin/jobs/verified
