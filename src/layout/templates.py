"""
Page templates for different types of book pages
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class PageTemplate(ABC):
    """Base class for all page templates"""
    
    def __init__(self, config):
        self.config = config
        self.width, self.height = config.page_size
        self.margins = config.margins
        
    @abstractmethod
    def create_layout(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a layout specification from content"""
        pass
        
    def get_content_area(self) -> Tuple[float, float, float, float]:
        """Calculate the content area based on margins"""
        left = self.margins["left"]
        top = self.margins["top"]
        right = self.width - self.margins["right"]
        bottom = self.height - self.margins["bottom"]
        return (left, top, right, bottom)


class TitlePageTemplate(PageTemplate):
    """Template for book title pages"""
    
    def create_layout(self, content: Dict[str, Any]) -> Dict[str, Any]:
        left, top, right, bottom = self.get_content_area()
        width = right - left
        height = bottom - top
        
        # Get content elements
        title = content.get('title', 'Untitled')
        subtitle = content.get('subtitle', '')
        author = content.get('author', '')
        cover_image = content.get('cover_image')
        
        # Calculate positions
        if cover_image:
            # With cover image: image at top, text below
            image_height = height * 0.6
            title_y = top + image_height + 20
            image_box = {
                'x': left + (width / 2) - (width * 0.4),  # Centered
                'y': top + 20,
                'width': width * 0.8,
                'height': image_height,
                'image': cover_image
            }
        else:
            # Text only: title centered vertically
            title_y = top + height * 0.4
            image_box = None
            
        # Text layout
        title_box = {
            'x': left,
            'y': title_y,
            'width': width,
            'height': 40,
            'text': title,
            'font_size': self.config.base_font_size * 2,
            'alignment': 'center'
        }
        
        subtitle_box = {
            'x': left,
            'y': title_y + 50,
            'width': width,
            'height': 30,
            'text': subtitle,
            'font_size': self.config.base_font_size * 1.3,
            'alignment': 'center'
        } if subtitle else None
        
        author_box = {
            'x': left,
            'y': title_y + (80 if subtitle else 50),
            'width': width,
            'height': 20,
            'text': author,
            'font_size': self.config.base_font_size,
            'alignment': 'center'
        } if author else None
        
        # Compile layout
        elements = [title_box]
        if subtitle_box:
            elements.append(subtitle_box)
        if author_box:
            elements.append(author_box)
        if image_box:
            elements.append(image_box)
            
        return {
            'type': 'title_page',
            'elements': elements
        }


class ContentPageTemplate(PageTemplate):
    """Template for text-only content pages"""
    
    def create_layout(self, content: Dict[str, Any]) -> Dict[str, Any]:
        left, top, right, bottom = self.get_content_area()
        width = right - left
        height = bottom - top
        
        # Get text content
        text_chunks = content.get('text_chunks', [])
        
        # Create text boxes
        text_boxes = []
        current_y = top
        
        for chunk in text_chunks:
            chunk_text = chunk.get('text', '')
            chunk_style = chunk.get('style', 'normal')
            
            # Calculate font size and spacing based on style
            if chunk_style == 'heading':
                font_size = self.config.base_font_size * 1.5
                line_height = font_size * 1.3
            elif chunk_style == 'subheading':
                font_size = self.config.base_font_size * 1.2
                line_height = font_size * 1.2
            else:  # normal text
                font_size = self.config.base_font_size
                line_height = font_size * self.config.line_spacing
            
            # Estimate height based on text length and width
            # This is a simplified calculation - in a real implementation, 
            # you'd use proper text measurement
            approx_chars_per_line = int(width / (font_size * 0.5))  # Rough estimate
            lines = max(1, len(chunk_text) / approx_chars_per_line)
            box_height = lines * line_height
            
            text_box = {
                'x': left,
                'y': current_y,
                'width': width,
                'height': box_height,
                'text': chunk_text,
                'font_size': font_size,
                'style': chunk_style
            }
            
            text_boxes.append(text_box)
            current_y += box_height + (10 if chunk_style in ['heading', 'subheading'] else 5)
        
        # Add page number
        page_number_box = {
            'x': left + width / 2,
            'y': bottom + 10,
            'width': 20,
            'height': 15,
            'text': str(content.get('page_number', '')),
            'font_size': self.config.base_font_size * 0.8,
            'alignment': 'center'
        }
        
        return {
            'type': 'content_page',
            'elements': text_boxes + [page_number_box]
        }


class ImageTextPageTemplate(PageTemplate):
    """Template for pages with both image and text"""
    
    def create_layout(self, content: Dict[str, Any]) -> Dict[str, Any]:
        left, top, right, bottom = self.get_content_area()
        width = right - left
        height = bottom - top
        
        # Get content
        text_chunks = content.get('text_chunks', [])
        image = content.get('image')
        image_placement = content.get('image_placement', {})
        
        # Determine image position and dimensions
        image_position = image_placement.get('position', 'top')  # top, bottom, left, right
        image_size = image_placement.get('size', 0.5)  # Proportion of content area
        
        # Calculate image and text areas based on position
        if image_position == 'top':
            image_box = {
                'x': left,
                'y': top,
                'width': width,
                'height': height * image_size,
                'image': image
            }
            text_area = (left, top + height * image_size, right, bottom)
        elif image_position == 'bottom':
            image_box = {
                'x': left,
                'y': top + height * (1 - image_size),
                'width': width,
                'height': height * image_size,
                'image': image
            }
            text_area = (left, top, right, top + height * (1 - image_size))
        elif image_position == 'left':
            image_box = {
                'x': left,
                'y': top,
                'width': width * image_size,
                'height': height,
                'image': image
            }
            text_area = (left + width * image_size, top, right, bottom)
        else:  # right
            image_box = {
                'x': left + width * (1 - image_size),
                'y': top,
                'width': width * image_size,
                'height': height,
                'image': image
            }
            text_area = (left, top, left + width * (1 - image_size), bottom)
        
        # Create text boxes within the text area
        text_boxes = []
        t_left, t_top, t_right, t_bottom = text_area
        t_width = t_right - t_left
        current_y = t_top
        
        for chunk in text_chunks:
            chunk_text = chunk.get('text', '')
            chunk_style = chunk.get('style', 'normal')
            
            # Calculate font sizes as in ContentPageTemplate
            if chunk_style == 'heading':
                font_size = self.config.base_font_size * 1.5
                line_height = font_size * 1.3
            elif chunk_style == 'subheading':
                font_size = self.config.base_font_size * 1.2
                line_height = font_size * 1.2
            else:  # normal text
                font_size = self.config.base_font_size
                line_height = font_size * self.config.line_spacing
                
            # Estimate text box height
            approx_chars_per_line = int(t_width / (font_size * 0.5))
            lines = max(1, len(chunk_text) / approx_chars_per_line)
            box_height = lines * line_height
            
            # Make sure we stay within the text area
            if current_y + box_height > t_bottom:
                # Text overflow - in a real implementation you might handle this differently
                box_height = t_bottom - current_y
            
            text_box = {
                'x': t_left,
                'y': current_y,
                'width': t_width,
                'height': box_height,
                'text': chunk_text,
                'font_size': font_size,
                'style': chunk_style
            }
            
            text_boxes.append(text_box)
            current_y += box_height + (10 if chunk_style in ['heading', 'subheading'] else 5)
        
        # Add page number
        page_number_box = {
            'x': left + width / 2,
            'y': bottom + 10,
            'width': 20,
            'height': 15,
            'text': str(content.get('page_number', '')),
            'font_size': self.config.base_font_size * 0.8,
            'alignment': 'center'
        }
        
        return {
            'type': 'image_text_page',
            'elements': [image_box] + text_boxes + [page_number_box]
        }
