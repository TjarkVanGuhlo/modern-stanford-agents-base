"""
Django settings initialization.

Loading order:
1. base.py - Core settings shared across all environments
2. local.py - Development overrides (if present)
3. production.py - Production settings (if local.py is absent)

For production deployments, ensure DJANGO_SECRET_KEY is set.
"""

# ruff: noqa: F403, F405 - Star imports are idiomatic for Django settings
from .base import *

try:
    from .local import *

    live = False
except ImportError:
    live = True

if live:
    from .production import *

# Validate SECRET_KEY is set after all settings are loaded
if not SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY environment variable is required. "
        'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )
