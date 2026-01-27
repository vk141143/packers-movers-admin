# Frontend Integration Guide - Verify & Generate Button

## Quick Start for Frontend Developers

### Admin Panel - Single Button Implementation

#### HTML Button
```html
<button 
  onclick="verifyAndGenerate('job-id-here')"
  class="btn-verify-generate"
>
  ✅ Verify & Generate Invoice
</button>
```

#### JavaScript/TypeScript
```javascript
async function verifyAndGenerate(jobId) {
  // Show loading state
  const button = event.target;
  button.disabled = true;
  button.textContent = '⏳ Processing...';
  
  try {
    const response = await fetch(
      `http://localhost:8001/api/admin/jobs/${jobId}/verify-and-generate`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }
    
    const result = await response.json();
    
    // Success!
    alert(`✅ Success!\n\nJob Status: ${result.status}\nInvoice: ${result.invoice_number}`);
    
    // Refresh the job list or redirect
    window.location.reload();
    
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
    button.disabled = false;
    button.textContent = '✅ Verify & Generate Invoice';
  }
}
```

#### React Component
```jsx
import { useState } from 'react';

function VerifyGenerateButton({ jobId }) {
  const [loading, setLoading] = useState(false);
  
  const handleVerifyGenerate = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(
        `http://localhost:8001/api/admin/jobs/${jobId}/verify-and-generate`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const result = await response.json();
      
      if (response.ok) {
        alert(`✅ Job completed! Invoice: ${result.invoice_number}`);
        // Refresh or update state
      } else {
        alert(`❌ Error: ${result.detail}`);
      }
    } catch (error) {
      alert(`❌ Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <button 
      onClick={handleVerifyGenerate}
      disabled={loading}
      className="btn-primary"
    >
      {loading ? '⏳ Processing...' : '✅ Verify & Generate'}
    </button>
  );
}
```

---

## Client Portal - Status Display

### Status Badge Component

#### React
```jsx
function JobStatusBadge({ status }) {
  const statusConfig = {
    'job_created': { label: 'Created', color: 'gray', icon: '📝' },
    'crew_assigned': { label: 'Crew Assigned', color: 'blue', icon: '👷' },
    'pending_verification': { label: 'Pending Verification', color: 'orange', icon: '⏳' },
    'admin_verified': { label: 'Admin Verified', color: 'green', icon: '✅' },
    'invoice_generated': { label: 'Invoice Generated', color: 'purple', icon: '📄' },
    'job_completed': { label: 'Completed', color: 'green', icon: '✔️' }
  };
  
  const config = statusConfig[status] || { label: status, color: 'gray', icon: '❓' };
  
  return (
    <span className={`badge badge-${config.color}`}>
      {config.icon} {config.label}
    </span>
  );
}
```

#### HTML/CSS
```html
<div class="status-badge status-completed">
  ✔️ Job Completed
</div>

<style>
.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  display: inline-block;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.status-verified {
  background: #cce5ff;
  color: #004085;
}

.status-invoice {
  background: #e2d9f3;
  color: #5a2d82;
}
</style>
```

### Real-time Status Updates

#### Polling Approach
```javascript
// Poll every 5 seconds for status updates
function startStatusPolling(jobId) {
  const pollInterval = setInterval(async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/jobs/${jobId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('client_token')}`
          }
        }
      );
      
      const job = await response.json();
      
      // Update UI
      document.getElementById('job-status').textContent = job.status;
      
      // Stop polling if job is completed
      if (job.status === 'job_completed') {
        clearInterval(pollInterval);
        showCompletionNotification(job);
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, 5000); // Poll every 5 seconds
  
  return pollInterval;
}

// Usage
const pollInterval = startStatusPolling('job-id-123');

// Stop polling when component unmounts
// clearInterval(pollInterval);
```

---

## API Endpoints Reference

### Admin Backend (Port 8001)

#### Verify & Generate (NEW - Single Button)
```
POST /api/admin/jobs/{job_id}/verify-and-generate
Authorization: Bearer {admin_token}

Response:
{
  "success": true,
  "message": "Job verified, invoice generated, and job completed",
  "job_id": "...",
  "status": "job_completed",
  "invoice_id": "...",
  "invoice_number": "INV-12345678"
}
```

#### Get Job for Verification
```
GET /api/admin/jobs/{job_id}/verification
Authorization: Bearer {admin_token}

Response:
{
  "job_id": "...",
  "service_type": "Emergency",
  "before_photos": ["url1", "url2"],
  "after_photos": ["url3", "url4"]
}
```

### Client Backend (Port 8000)

#### Get Job Status
```
GET /api/jobs/{job_id}
Authorization: Bearer {client_token}

Response:
{
  "id": "...",
  "status": "job_completed",
  "service_type": "Emergency",
  "price": 2500.00
}
```

#### Get All Jobs
```
GET /api/jobs
Authorization: Bearer {client_token}

Response: [
  {
    "id": "...",
    "status": "job_completed",
    ...
  }
]
```

---

## Error Handling

### Common Errors

#### 1. Missing Photos
```json
{
  "detail": "Before and after photos are required"
}
```
**Solution:** Ensure crew uploaded both before and after photos

#### 2. Wrong Status
```json
{
  "detail": "Job must be in pending_verification status"
}
```
**Solution:** Check current job status, might already be processed

#### 3. Unauthorized
```json
{
  "detail": "Admin access required"
}
```
**Solution:** Verify admin token is valid and not expired

### Error Handling Example
```javascript
try {
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!response.ok) {
    // Handle specific errors
    if (response.status === 400) {
      alert(`Validation Error: ${data.detail}`);
    } else if (response.status === 403) {
      alert('Access Denied: Admin login required');
      window.location.href = '/admin/login';
    } else if (response.status === 404) {
      alert('Job not found');
    } else {
      alert(`Error: ${data.detail}`);
    }
    return;
  }
  
  // Success handling
  console.log('Success:', data);
  
} catch (error) {
  alert(`Network Error: ${error.message}`);
}
```

---

## Testing Checklist

### Admin Panel Testing
- [ ] Button appears for jobs in `pending_verification` status
- [ ] Button disabled during processing
- [ ] Success message shows invoice number
- [ ] Job list refreshes after success
- [ ] Error messages display correctly
- [ ] Button re-enables after error

### Client Portal Testing
- [ ] Status updates from `pending_verification` to `job_completed`
- [ ] Status badge shows correct color and icon
- [ ] Invoice appears in invoice history
- [ ] Can download invoice PDF
- [ ] Real-time updates work (if using polling)

---

## Environment Variables

### Admin Frontend
```env
REACT_APP_ADMIN_API_URL=http://localhost:8001
```

### Client Frontend
```env
REACT_APP_CLIENT_API_URL=http://localhost:8000
```

---

## Complete Example: Admin Job Verification Page

```jsx
import React, { useState, useEffect } from 'react';

function JobVerificationPage({ jobId }) {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);
  
  const fetchJobDetails = async () => {
    const response = await fetch(
      `http://localhost:8001/api/admin/jobs/${jobId}/verification`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        }
      }
    );
    const data = await response.json();
    setJob(data);
  };
  
  const handleVerifyGenerate = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(
        `http://localhost:8001/api/admin/jobs/${jobId}/verify-and-generate`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
          }
        }
      );
      
      const result = await response.json();
      
      if (response.ok) {
        alert(`✅ Success! Invoice: ${result.invoice_number}`);
        window.location.href = '/admin/jobs';
      } else {
        alert(`❌ Error: ${result.detail}`);
      }
    } catch (error) {
      alert(`❌ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  
  if (!job) return <div>Loading...</div>;
  
  return (
    <div className="verification-page">
      <h2>Job Verification</h2>
      
      <div className="job-details">
        <p><strong>Job ID:</strong> {job.job_id}</p>
        <p><strong>Service:</strong> {job.service_type}</p>
        <p><strong>SLA Level:</strong> {job.sla_level}</p>
      </div>
      
      <div className="photos">
        <h3>Before Photos</h3>
        <div className="photo-grid">
          {job.before_photos.map((url, i) => (
            <img key={i} src={url} alt={`Before ${i+1}`} />
          ))}
        </div>
        
        <h3>After Photos</h3>
        <div className="photo-grid">
          {job.after_photos.map((url, i) => (
            <img key={i} src={url} alt={`After ${i+1}`} />
          ))}
        </div>
      </div>
      
      <button 
        onClick={handleVerifyGenerate}
        disabled={loading}
        className="btn-verify-generate"
      >
        {loading ? '⏳ Processing...' : '✅ Verify & Generate Invoice'}
      </button>
    </div>
  );
}

export default JobVerificationPage;
```

---

## Support

For issues or questions:
1. Check job status in database
2. Verify authentication tokens
3. Check backend logs
4. Review error messages in browser console
