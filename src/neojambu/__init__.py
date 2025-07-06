"""
NeoJambu Linguistics Webapp

A Flask-based web application for exploring etymological data with 313k lemmas across 615 languages.
Provides interactive visualization and search capabilities for linguistic research.
"""

__version__ = "1.0.0"
__author__ = "Aryaman Arora"
__email__ = "aryaman.arora2020@gmail.com"

from .app import app

__all__ = ["app"]