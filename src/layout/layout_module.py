"""
Layout Module - Responsible for generating book layouts with LLM assistance
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Literal
import json

from .templates import TitlePageTemplate, ContentPageTemplate, ImageTextPageTemplate
from .llm_advisor import LayoutLLMAdvisor
from .text_flow import TextFlowEngine
from .image_placement import ImagePlacementEngine


@dataclass
class LayoutConfig:
    """Configuration for layout generation"""
    page_size: Tuple[float, float] = (8.5, 11.0)  # Width, height in inches
    margins: Dict[str, float] = None
    font_family: str = "Arial"
    base_font_size: float = 12.0
    line_spacing: float = 1.5
    image_text_ratio: float = 0.5  # Default ratio of image to text
    age_group: str = "5-8"  # Target age group
    is_send_adapted: bool = False  # Special Educational Needs and Disabilities
    output_format: Literal["pdf", "epub", "both"] = "both"  # New field for output format
    
    def __post_init__(self):
        if self.margins is None:
            # Default margins in inches (left, right, top, bottom)
            self.margins = {"left": 1.0, "right": 1.0, "top": 1.0, "bottom": 1.0}


@dataclass
class PageLayout:
    """Represents a complete layout for a single page"""
    template_type: str
    content: Dict
    page_number: int
    

class BookLayout:
    """Main class for handling the overall book layout"""
    
    def __init__(self, config: LayoutConfig = None):
        self.config = config or LayoutConfig()
        self.pages = []
        self.llm_advisor = LayoutLLMAdvisor()
        self.text_engine = TextFlowEngine(self.config)
        self.image_engine = ImagePlacementEngine(self.config)
        # New fields for EPUB content
        self.epub_sections = []
        self.metadata = {}
        
    def analyze_content(self, content_blocks, images):
        """Analyze content and get LLM recommendations for layout"""
        content_type = self._determine_content_type(content_blocks)
        
        # Get layout recommendations from LLM
        recommendations = self.llm_advisor.get_layout_recommendations(
            content_blocks, 
            content_type=content_type,
            age_group=self.config.age_group,
            is_send=self.config.is_send_adapted
        )
        
        # Update configuration based on LLM recommendations
        self._apply_recommendations(recommendations)
        
        return recommendations
        
    def _determine_content_type(self, content_blocks):
        """Determine the general type of content (story, educational, etc.)"""
        # Simple heuristic based on content length and structure
        # Could be enhanced with more sophisticated analysis
        total_words = sum(len(block.get('text', '').split()) for block in content_blocks)
        
        if total_words < 200:
            return "early_reader"
        elif total_words < 500:
            return "picture_book"
        else:
            return "chapter_book"
    
    def _apply_recommendations(self, recommendations):
        """Apply LLM recommendations to the layout configuration"""
        if 'font_size' in recommendations:
            self.config.base_font_size = recommendations['font_size']
        
        if 'image_text_ratio' in recommendations:
            self.config.image_text_ratio = recommendations['image_text_ratio']
            
        if 'line_spacing' in recommendations:
            self.config.line_spacing = recommendations['line_spacing']
            
        if 'font_family' in recommendations:
            self.config.font_family = recommendations['font_family']
    
    def generate_layout(self, content_blocks, images):
        """
        Generate complete book layout from content blocks and images
        
        Args:
            content_blocks: List of dictionaries with text content
            images: List of image objects/paths
        
        Returns:
            List of PageLayout objects
        """
        # Get layout advice from LLM
        layout_recommendations = self.analyze_content(content_blocks, images)
        
        # Create title page
        self._add_title_page(content_blocks[0].get('title', 'Untitled'))
        
        # Extract metadata for EPUB
        if self.config.output_format in ["epub", "both"]:
            self._extract_metadata(content_blocks[0], layout_recommendations)
        
        # Process remaining content
        remaining_content = content_blocks[1:]
        current_page = 1
        
        while remaining_content or images:
            # Determine if this page should have an image (based on LLM recommendations)
            should_include_image = self._should_include_image(current_page, layout_recommendations)
            
            if should_include_image and images:
                # Create a page with text and image
                image = images.pop(0)
                text_chunks, remaining_content = self.text_engine.allocate_text_for_page(
                    remaining_content, 
                    with_image=True
                )
                
                page = self._create_image_text_page(text_chunks, image, current_page)
            else:
                # Create text-only page
                text_chunks, remaining_content = self.text_engine.allocate_text_for_page(
                    remaining_content, 
                    with_image=False
                )
                
                page = self._create_text_page(text_chunks, current_page)
            
            self.pages.append(page)
            current_page += 1
            
            # For EPUB, create HTML content sections
            if self.config.output_format in ["epub", "both"]:
                self._add_epub_section(text_chunks, image if should_include_image and images else None)
        
        return self.pages
    
    def _should_include_image(self, page_number, recommendations):
        """Determine if this page should include an image"""
        # Get image frequency from recommendations or use default
        image_frequency = recommendations.get('image_frequency', 2)  # Default: every other page
        
        # For early readers, we might want images on almost every page
        if recommendations.get('content_type') == 'early_reader':
            return True
            
        # Simple logic: include image every N pages (N=image_frequency)
        return page_number % image_frequency == 1
    
    def _add_title_page(self, title, subtitle=None, author=None, cover_image=None):
        """Add title page to the layout"""
        template = TitlePageTemplate(self.config)
        page = PageLayout(
            template_type="title",
            content={
                'title': title,
                'subtitle': subtitle,
                'author': author,
                'cover_image': cover_image
            },
            page_number=0  # Title page is typically not numbered
        )
        self.pages.append(page)
    
    def _create_text_page(self, text_chunks, page_number):
        """Create a text-only page"""
        template = ContentPageTemplate(self.config)
        return PageLayout(
            template_type="text",
            content={'text_chunks': text_chunks},
            page_number=page_number
        )
    
    def _create_image_text_page(self, text_chunks, image, page_number):
        """Create a page with both image and text"""
        template = ImageTextPageTemplate(self.config)
        # Use the image placement engine to determine optimal image position
        image_placement = self.image_engine.calculate_image_position(
            text_chunks, 
            image
        )
        
        return PageLayout(
            template_type="image_text",
            content={
                'text_chunks': text_chunks,
                'image': image,
                'image_placement': image_placement
            },
            page_number=page_number
        )
        
    def _extract_metadata(self, title_block, recommendations):
        """Extract metadata for EPUB"""
        self.metadata = {
            "title": title_block.get('title', 'Untitled'),
            "creator": title_block.get('author', 'Unknown Author'),
            "language": "en",  # Default language
            "identifier": f"publisher-{hash(title_block.get('title', 'Untitled'))}",  # Simple unique ID
            "publisher": "Auto Publisher",
            # Additional metadata fields can be added here
        }
        
    def _add_epub_section(self, text_chunks, image=None):
        """Add a section to the EPUB content"""
        section = {
            "text_chunks": text_chunks,
            "image": image,
            "id": f"section_{len(self.epub_sections)}"
        }
        self.epub_sections.append(section)
        
    def export_epub_content(self):
        """Export content structured for EPUB generation"""
        return {
            "metadata": self.metadata,
            "sections": self.epub_sections
        }
        
    def export_layout(self, output_path):
        """Export the layout to a JSON file for debugging/review"""
        layout_data = [
            {
                'template': page.template_type,
                'page_number': page.page_number,
                'content': {k: str(v) for k, v in page.content.items()}  # Convert content to strings for serialization
            }
            for page in self.pages
        ]
        
        with open(output_path, 'w') as f:
            json.dump(layout_data, f, indent=2)
        
        # If EPUB content is available, also export EPUB structure
        if self.config.output_format in ["epub", "both"]:
            epub_path = output_path.replace('.json', '_epub.json')
            with open(epub_path, 'w') as f:
                json.dump(self.export_epub_content(), f, indent=2)
            
        return output_path


if __name__ == "__main__":
    # Simple test
    config = LayoutConfig(age_group="3-6", is_send_adapted=True)
    layout_engine = BookLayout(config)
    
    # Test with dummy content
    test_content = [
        {'title': 'My First Book'},
        {'text': 'Once upon a time, there was a little rabbit.'},
        {'text': 'The rabbit loved to hop and play in the garden.'}
    ]
    
    test_images = ['rabbit.jpg', 'garden.jpg']
    
    pages = layout_engine.generate_layout(test_content, test_images)
    layout_engine.export_layout('test_layout.json')
    print(f"Generated {len(pages)} pages")
