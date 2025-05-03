"""
Input module for parsing text and Word documents.
"""

from .text_reader import TextReader
from .docx_reader import DocxReader

__all__ = ['TextReader', 'DocxReader']
