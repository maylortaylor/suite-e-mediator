"""
Metadata Package

Provides metadata extraction, writing, and standardization capabilities
for the Suite E Studios media processing workflow.
"""

from .extractor import MetadataExtractor
from .writer import MetadataWriter

__all__ = ["MetadataExtractor", "MetadataWriter"]
