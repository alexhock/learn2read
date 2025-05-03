"""
Text Flow Engine - Manages text flow across pages and around images
"""

from typing import List, Dict, Tuple, Any


class TextFlowEngine:
    """Handles text flow and pagination calculations"""
    
    def __init__(self, config):
        self.config = config
        self.page_width = config.page_size[0] - config.margins['left'] - config.margins['right']
        self.page_height = config.page_size[1] - config.margins['top'] - config.margins['bottom']
        
    def allocate_text_for_page(
        self, 
        content_blocks: List[Dict], 
        with_image: bool = False
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Allocate text content for a single page
        
        Args:
            content_blocks: List of content blocks to allocate
            with_image: Whether the page includes an image
            
        Returns:
            Tuple of (allocated_blocks, remaining_blocks)
        """
        if not content_blocks:
            return [], []
        
        # Calculate available space for text
        available_height = self.page_height
        
        if with_image:
            # When there's an image, assume it takes up the image_text_ratio portion of the page
            available_height *= (1 - self.config.image_text_ratio)
            
        # Calculate how many blocks can fit on this page
        allocated_blocks = []
        remaining_height = available_height
        
        for block in content_blocks:
            block_height = self._estimate_block_height(block, self.page_width)
            
            # Add spacing between blocks
            if allocated_blocks:  # Add spacing after previous block
                block_height += 10  # 10pt spacing between blocks
            
            if block_height <= remaining_height:
                # This block fits
                allocated_blocks.append(block)
                remaining_height -= block_height
            else:
                # This block doesn't fit - we're done
                break
                
        # Return the allocated blocks and the remaining blocks
        remaining_blocks = content_blocks[len(allocated_blocks):]
        return allocated_blocks, remaining_blocks
        
    def _estimate_block_height(self, block: Dict, width: float) -> float:
        """
        Estimate the height required for a content block
        
        Args:
            block: Content block (text or heading)
            width: Available width
            
        Returns:
            Estimated height in points
        """
        text = block.get('text', '')
        style = block.get('style', 'normal')
        
        if not text:
            return 0
        
        # Determine font size based on style
        if style == 'heading':
            font_size = self.config.base_font_size * 1.5
            line_spacing = 1.3
        elif style == 'subheading':
            font_size = self.config.base_font_size * 1.2
            line_spacing = 1.2
        else:  # normal text
            font_size = self.config.base_font_size
            line_spacing = self.config.line_spacing
        
        # Estimate characters per line
        # This is a simplification - actual typesetting would need more precise calculations
        chars_per_line = int(width / (font_size * 0.5))  # Rough estimate
        
        # Calculate number of lines
        # Split by words to avoid breaking within words
        words = text.split()
        line_count = 1
        current_line_chars = 0
        
        for word in words:
            # +1 for space between words
            if current_line_chars + len(word) + 1 > chars_per_line:
                line_count += 1
                current_line_chars = len(word)
            else:
                current_line_chars += len(word) + 1
        
        # Calculate height based on lines and font size
        height = line_count * font_size * line_spacing
        
        return height
