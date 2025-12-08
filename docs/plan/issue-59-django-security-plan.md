# Implementation Plan: Issue #59 - Fix Django Security Vulnerabilities

## Overview

This plan addresses the critical Django security vulnerabilities identified in the frontend server settings. The fixes follow Django security best practices and maintain backward compatibility with existing development workflows.

## Current State Analysis

### Files Involved
- `environment/frontend_server/frontend_server/settings/base.py` - Main settings (shared between local/production)
- `environment/frontend_server/frontend_server/settings/local.py` - Local development overrides (duplicates base.py)
- `environment/frontend_server/frontend_server/settings/__init__.py` - Settings loader
- `environment/frontend_server/translator/views.py` - Contains POST endpoints that need CSRF handling

### Settings Loading Flow
```
__init__.py imports:
1. base.py (always)
2. local.py (if exists, sets live=False)
3. production.py (if local.py doesn't exist, sets live=True) - FILE MISSING
```

### POST Endpoints Requiring CSRF Handling
1. `process_environment()` - AJAX endpoint from frontend simulation
2. `update_environment()` - AJAX endpoint for backend updates
3. `path_tester_update()` - AJAX endpoint for path testing

These are internal AJAX endpoints called from JavaScript in the same domain. They need `@csrf_exempt` if we enable CSRF middleware, or we implement proper CSRF token handling in the frontend JavaScript.

---

## Implementation Steps

### Step 1: Fix base.py Security Settings

**File:** `environment/frontend_server/frontend_server/settings/base.py`

**Changes:**

1. **SECRET_KEY** - Load from environment with validation
   ```python
   SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
   if not SECRET_KEY:
       raise ValueError("DJANGO_SECRET_KEY environment variable is required")
   ```

2. **DEBUG** - Load from environment, default to False (secure by default)
   ```python
   DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
   ```

3. **ALLOWED_HOSTS** - Load from environment with sensible default
   ```python
   ALLOWED_HOSTS = [
       host.strip()
       for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
       if host.strip()
   ]
   ```

4. **CSRF Middleware** - Re-enable in middleware list
   ```python
   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       "django.contrib.sessions.middleware.SessionMiddleware",
       "corsheaders.middleware.CorsMiddleware",  # Move before CommonMiddleware
       "django.middleware.common.CommonMiddleware",
       "django.middleware.csrf.CsrfViewMiddleware",  # Re-enabled
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       "django.contrib.messages.middleware.MessageMiddleware",
       "django.middleware.clickjacking.XFrameOptionsMiddleware",
   ]
   ```

### Step 2: Update local.py for Development

**File:** `environment/frontend_server/frontend_server/settings/local.py`

**Purpose:** Override security settings for local development only.

**Changes:**
- Remove duplicate settings that are already in base.py
- Add development-friendly overrides:
  ```python
  from .base import *  # noqa: F403

  # Development overrides
  DEBUG = True

  # For development, generate a random key if not set
  import secrets
  SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", secrets.token_urlsafe(50))

  # Accept all hosts in development
  ALLOWED_HOSTS = ["*"]
  ```

### Step 3: Add CSRF Exemption to AJAX Endpoints

**File:** `environment/frontend_server/translator/views.py`

**Approach:** Use `@csrf_exempt` decorator for internal AJAX endpoints. These endpoints:
- Are called only by JavaScript from the same origin
- Do not handle user authentication or sensitive data
- Are used for simulation data transfer between frontend and backend

**Changes:**
```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_environment(request):
    ...

@csrf_exempt
def update_environment(request):
    ...

@csrf_exempt
def path_tester_update(request):
    ...
```

**Rationale:** These endpoints are internal simulation data handlers, not user-facing APIs. Adding proper CSRF token handling to the frontend JavaScript would require modifying template files and JavaScript code, which is out of scope for this security fix. The `@csrf_exempt` decorator explicitly acknowledges these endpoints do not need CSRF protection.

### Step 4: Create .env.example File

**File:** `.env.example` (project root)

**Content:**
```bash
# Django Configuration
# Generate a secret key with: python -c "import secrets; print(secrets.token_urlsafe(50))"
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI Configuration (existing)
OPENAI_API_KEY=your-api-key-here
KEY_OWNER=Your Name

# Model Configuration (optional)
# MODEL_PRESET=balanced
```

### Step 5: Update CLAUDE.md Documentation

**File:** `CLAUDE.md`

**Add section under Environment Variables:**
```markdown
## Django Frontend Configuration

Required for production:
```bash
DJANGO_SECRET_KEY=<generated-secret-key>  # Required
DJANGO_DEBUG=False                         # Optional, defaults to False
DJANGO_ALLOWED_HOSTS=yourdomain.com        # Optional, defaults to localhost,127.0.0.1
```

For local development, these can be omitted - sensible defaults are applied automatically.
```

---

## Testing Plan

### Manual Testing Steps

1. **Test without environment variables (local development):**
   ```bash
   cd environment/frontend_server
   uv run python manage.py check
   uv run python manage.py runserver
   ```
   - Should start successfully with auto-generated secret key
   - Should accept requests on localhost

2. **Test with environment variables (production mode):**
   ```bash
   export DJANGO_SECRET_KEY="test-secret-key-for-testing"
   export DJANGO_DEBUG=False
   export DJANGO_ALLOWED_HOSTS=localhost
   uv run python manage.py check
   uv run python manage.py runserver
   ```
   - Should start with provided secret key
   - Should only accept requests from allowed hosts

3. **Test missing SECRET_KEY in production:**
   - Remove local.py temporarily
   - Verify ValueError is raised when SECRET_KEY is missing

4. **Test CSRF protection:**
   - Verify POST to AJAX endpoints works (csrf_exempt)
   - Verify CSRF middleware is active (check middleware loading)

### Automated Test (Optional)

Create `tests/test_django_settings.py`:
```python
import os
import sys
from unittest.mock import patch

def test_secret_key_required_in_production():
    """Verify SECRET_KEY is required when local.py is absent."""
    # This would require more complex test setup
    pass

def test_debug_defaults_to_false():
    """Verify DEBUG defaults to False (secure by default)."""
    pass
```

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| SECRET_KEY from env | Low | local.py provides fallback for dev |
| DEBUG=False default | Low | local.py overrides to True |
| ALLOWED_HOSTS from env | Low | Default includes localhost |
| Enable CSRF middleware | Medium | Add @csrf_exempt to AJAX endpoints |

---

## Rollback Plan

If issues occur:
1. Revert the branch changes
2. Original files are preserved in git history
3. No database migrations or data changes involved

---

## Acceptance Criteria Checklist

From issue #59:
- [ ] SECRET_KEY loaded from environment variable
- [ ] CSRF middleware enabled (with appropriate exemptions)
- [ ] DEBUG controlled by environment variable, defaults to False
- [ ] ALLOWED_HOSTS configurable via environment variable
- [ ] Add `.env.example` file documenting required Django environment variables
- [ ] Update CLAUDE.md with Django configuration instructions

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `settings/base.py` | Modify | Load security settings from environment |
| `settings/local.py` | Modify | Simplify to dev-only overrides |
| `translator/views.py` | Modify | Add @csrf_exempt to AJAX endpoints |
| `.env.example` | Create | Document required environment variables |
| `CLAUDE.md` | Modify | Add Django configuration docs |
| `pyproject.toml` | Modify | Bump patch version |
