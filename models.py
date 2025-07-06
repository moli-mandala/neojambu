"""
Compatibility module for deployment.
Imports database models from the restructured package.
"""

from src.neojambu.models import *

# Re-export everything for compatibility
__all__ = ["Language", "Lemma", "Concept", "Reference", "LemmaConcept", "LemmaReference", "Base"]