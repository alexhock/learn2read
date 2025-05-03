"""
Tests for the TextReader class.
"""

import os
import tempfile
import pytest
from publisher.input.text_reader import TextReader

def test_text_reader_empty_file():
    """Test reading an empty file."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp_path = temp.name
    
    try:
        reader = TextReader()
        result = reader.read(temp_path)
        assert result == []
    finally:
        os.unlink(temp_path)

def test_text_reader_basic_content():
    """Test reading a file with basic content."""
    content = "Title\n\nParagraph 1\n\nParagraph 2"
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write(content)
        temp_path = temp.name
    
    try:
        reader = TextReader()
        result = reader.read(temp_path)
        assert result == ["Title", "Paragraph 1", "Paragraph 2"]
    finally:
        os.unlink(temp_path)
