"""
Compatibility module for deployment.
Imports the main Flask app from the restructured package.
"""

from src.neojambu.app import app, get_session

# Expose for compatibility
__all__ = ["app", "get_session"]