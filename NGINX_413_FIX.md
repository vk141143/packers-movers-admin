# Fix for 413 Request Entity Too Large Error

## Problem
Crew registration fails in production with 413 error when uploading documents.
This is because nginx has a default 1MB limit for request body size.

## Solution: Update Nginx Configuration

### Step 1: SSH into your production server
```bash
ssh root@admin.voidworksgroup.co.uk
```

### Step 2: Edit nginx configuration
```bash
sudo nano /etc/nginx/nginx.conf
```

### Step 3: Add this inside the `http` block:
```nginx
http {
    # ... existing config ...
    
    # Increase upload size limit to 50MB
    client_max_body_size 50M;
    
    # ... rest of config ...
}
```

### Step 4: Or add to your site-specific config:
```bash
sudo nano /etc/nginx/sites-available/admin.voidworksgroup.co.uk
```

Add inside the `server` block:
```nginx
server {
    # ... existing config ...
    
    # Allow larger file uploads (50MB)
    client_max_body_size 50M;
    
    # ... rest of config ...
}
```

### Step 5: Test nginx configuration
```bash
sudo nginx -t
```

### Step 6: Reload nginx
```bash
sudo systemctl reload nginx
```

## Alternative: Quick Fix (if you have access to nginx config)

Add to `/etc/nginx/conf.d/upload.conf`:
```nginx
client_max_body_size 50M;
```

Then reload:
```bash
sudo systemctl reload nginx
```

## Recommended Limits

- **Development**: 50MB
- **Production**: 20-50MB (depending on your needs)
- **For crew documents**: 10MB should be enough
- **For job photos**: 20MB is safe

## Why 50MB?

Crew registration uploads:
- Drivers License (max 5MB)
- DBS Certificate (max 5MB)
- Proof of Address (max 5MB)
- Insurance Certificate (max 5MB)
- Right to Work (max 5MB)
- Profile Photo (max 5MB)

Total: ~30MB max, so 50MB gives buffer.

## Verify the Fix

After updating nginx, test crew registration again:
```
POST https://admin.voidworksgroup.co.uk/api/auth/register/crew
```

Should now accept larger file uploads without 413 error.

---

**Note**: This is a server configuration issue, not a code issue. Your FastAPI code is fine.
