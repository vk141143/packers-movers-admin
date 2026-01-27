"""
Test script for Job Verification API endpoints
Run this after starting the server to verify all endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8001/api"

# Replace with actual admin token after login
ADMIN_TOKEN = "YOUR_ADMIN_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def test_verification_stats():
    """Test getting verification statistics"""
    print("\n=== Testing Verification Stats ===")
    response = requests.get(f"{BASE_URL}/admin/verification/stats", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_pending_verifications():
    """Test getting all pending verifications"""
    print("\n=== Testing Get Pending Verifications ===")
    response = requests.get(f"{BASE_URL}/admin/verification/jobs", headers=headers)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} jobs pending verification")
    if data:
        print(f"First job: {json.dumps(data[0], indent=2)}")
    return response.status_code == 200, data

def test_get_job_details(job_id):
    """Test getting job verification details"""
    print(f"\n=== Testing Get Job Details for {job_id} ===")
    response = requests.get(f"{BASE_URL}/admin/verification/jobs/{job_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Job ID: {data['job_id']}")
        print(f"Client: {data['client_name']}")
        print(f"Crew: {data['crew_name']}")
        print(f"Before Photos: {len(data['before_photos'])}")
        print(f"After Photos: {len(data['after_photos'])}")
        print(f"Checklist Completed: {data['checklist_completed']}")
    else:
        print(f"Response: {response.json()}")
    return response.status_code == 200

def test_approve_job(job_id):
    """Test approving a job"""
    print(f"\n=== Testing Approve Job {job_id} ===")
    payload = {
        "final_price": 2500.00,
        "rating": 4.5
    }
    response = requests.post(
        f"{BASE_URL}/admin/verification/jobs/{job_id}/approve",
        headers=headers,
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_reject_job(job_id):
    """Test rejecting a job"""
    print(f"\n=== Testing Reject Job {job_id} ===")
    response = requests.post(
        f"{BASE_URL}/admin/verification/jobs/{job_id}/reject",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def run_all_tests():
    """Run all verification endpoint tests"""
    print("=" * 60)
    print("JOB VERIFICATION API TESTS")
    print("=" * 60)
    
    if ADMIN_TOKEN == "YOUR_ADMIN_TOKEN_HERE":
        print("\n⚠️  ERROR: Please set ADMIN_TOKEN in the script first!")
        print("1. Login as admin using POST /api/auth/login/admin")
        print("2. Copy the access_token from the response")
        print("3. Replace ADMIN_TOKEN in this script")
        return
    
    # Test 1: Get stats
    stats_ok = test_verification_stats()
    
    # Test 2: Get pending verifications
    pending_ok, jobs = test_get_pending_verifications()
    
    # Test 3: Get job details (if jobs exist)
    if pending_ok and jobs:
        job_id = jobs[0]['job_id']
        details_ok = test_get_job_details(job_id)
        
        # Test 4 & 5: Approve/Reject (commented out to avoid modifying data)
        print("\n⚠️  Approve/Reject tests are commented out to avoid modifying data")
        print(f"To test approval: test_approve_job('{job_id}')")
        print(f"To test rejection: test_reject_job('{job_id}')")
        
        # Uncomment to test (WARNING: This will modify the job status!)
        # approve_ok = test_approve_job(job_id)
        # reject_ok = test_reject_job(job_id)
    else:
        print("\n⚠️  No jobs pending verification. Create a test job first.")
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
