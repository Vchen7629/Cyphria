"""
Test configuration that runs before any test imports.
Sets required environment variables for Settings validation.
"""
import os

# Set environment variables BEFORE any imports
# This must happen at module level, not in a fixture, because Settings()
# is instantiated at module level in settings_config.py
os.environ.setdefault("PRODUCT_CATEGORY", "GPU")
os.environ.setdefault("POLLING_INTERVAL", "5.0")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("DB_USER", "test_user")
os.environ.setdefault("DB_PASS", "test_pass")
