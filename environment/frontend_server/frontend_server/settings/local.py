"""
Local development settings.

This file overrides base.py settings for local development.
It provides sensible defaults so developers don't need to configure
environment variables for basic local testing.
"""

import os
import secrets

# ruff: noqa: F403, F405 - Star imports are idiomatic for Django settings
from .base import *

# Override SECRET_KEY requirement for local development
# Generate a random key if not provided via environment
# Note: This regenerates on each restart, which invalidates sessions. For persistent
# sessions in development, set DJANGO_SECRET_KEY in your .env file.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", secrets.token_urlsafe(50))

# Enable debug mode for local development
DEBUG = True

# Accept all hosts in development
ALLOWED_HOSTS = ["*"]
