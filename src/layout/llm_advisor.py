"""
LLM Advisor - Provides layout recommendations using Large Language Models
"""

import os
import json
from typing import List, Dict, Any, Optional
import requests


class LayoutLLMAdvisor:
    """Uses LLMs to provide intelligent layout recommendations"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            print("Warning: No OpenAI API key provided. LLM recommendations will be simulated.")
    
    def get_layout_recommendations(
        self, 
        content_blocks: List[Dict], 
        content_type: str = "picture_book",
        age_group: str = "5-8", 
        is_send: bool = False,
        output_format: str = "both"  # New parameter for output format
    ) -> Dict[str, Any]:
        """
        Get layout recommendations from LLM based on content analysis
        
        Args:
            content_blocks: List of content block dictionaries
            content_type: Type of content (early_reader, picture_book, chapter_book)
            age_group: Target age group (e.g., "3-5", "6-8")
            is_send: Whether the book is for SEND (Special Educational Needs and Disabilities)
            output_format: Target output format ("pdf", "epub", or "both")
            
        Returns:
            Dictionary with layout recommendations
        """
        if not self.api_key:
            return self._get_default_recommendations(content_type, age_group, is_send, output_format)
            
        # Prepare content sample for analysis (limit size to reduce tokens)
        content_sample = self._prepare_content_sample(content_blocks)
        
        # Create prompt for the LLM
        prompt = self._create_layout_prompt(content_sample, content_type, age_group, is_send, output_format)
        
        # Call the LLM API
        try:
            response = self._call_llm_api(prompt)
            recommendations = self._parse_llm_response(response)
            return recommendations
        except Exception as e:
            print(f"Error getting LLM recommendations: {e}")
            return self._get_default_recommendations(content_type, age_group, is_send, output_format)
    
    def _prepare_content_sample(self, content_blocks: List[Dict]) -> str:
        """Extract a representative sample of content for analysis"""
        # Get the first few blocks and some from the middle if available
        sample_blocks = []
        
        if content_blocks:
            # Add the first block (usually title)
            sample_blocks.append(content_blocks[0])
            
            # Add up to 3 more blocks from beginning
            for i in range(1, min(4, len(content_blocks))):
                sample_blocks.append(content_blocks[i])
                
            # Add a couple from the middle if available
            mid_point = len(content_blocks) // 2
            if mid_point > 4 and mid_point < len(content_blocks):
                sample_blocks.append(content_blocks[mid_point])
                
        # Convert to text
        sample_text = "\n".join([
            block.get('title', '') or block.get('text', '') 
            for block in sample_blocks
        ])
        
        # Limit to reasonable size
        return sample_text[:1000] + ("..." if len(sample_text) > 1000 else "")
        
    def _create_layout_prompt(
        self, 
        content_sample: str, 
        content_type: str,
        age_group: str, 
        is_send: bool,
        output_format: str = "both"
    ) -> str:
        """Create a prompt for the LLM to get layout recommendations"""
        
        special_instructions = ""
        if is_send:
            special_instructions = """
            This book is for children with Special Educational Needs and Disabilities (SEND).
            Consider adaptations such as:
            - Larger, more spaced text
            - Clear, simple layouts
            - Higher contrast
            - More visual supports
            - Simplified language structures
            """
            
        epub_instructions = ""
        if output_format in ["epub", "both"]:
            epub_instructions = """
            This content will be published as an EPUB ebook, which needs responsive layouts.
            Consider:
            - Font sizes that scale well on different devices
            - Responsive image placement
            - Accessibility features (alt text, semantic HTML)
            - Reading flow that works well on various screen sizes
            """
            
        return f"""
        You are an expert book designer specializing in children's books. 
        I need recommendations for designing a {content_type} for children aged {age_group}.
        
        {special_instructions}
        {epub_instructions}
        
        Here's a sample of the content:
        ---
        {content_sample}
        ---
        
        Please provide specific recommendations in JSON format for:
        1. Font size (in points)
        2. Font family (choose child-friendly, readable fonts)
        3. Line spacing (as a multiplier, like 1.5)
        4. Image to text ratio (0.3 means 30% image, 70% text)
        5. Image frequency (how often to include images, e.g., every 1, 2, or 3 pages)
        6. Page margins (in inches)
        7. Special considerations for this content
        8. Any layout patterns to use (e.g., image-left-text-right, image-top-text-bottom)
        9. EPUB-specific recommendations (for responsive layout)
        
        Format your response as valid JSON only, without explanations.
        """
        
    def _call_llm_api(self, prompt: str) -> Dict:
        """Call the LLM API with the given prompt"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,  # Lower temperature for more consistent results
            "response_format": {"type": "json_object"}  # Request JSON response
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status {response.status_code}: {response.text}")
            
        return response.json()
    
    def _parse_llm_response(self, response: Dict) -> Dict:
        """Parse the LLM response to extract recommendations"""
        try:
            content = response["choices"][0]["message"]["content"]
            # The content should be a JSON string
            recommendations = json.loads(content)
            return recommendations
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse LLM response: {e}")
    
    def _get_default_recommendations(
        self, 
        content_type: str, 
        age_group: str, 
        is_send: bool,
        output_format: str = "both"
    ) -> Dict[str, Any]:
        """Provide default recommendations if LLM is not available"""
        # Parse age range to get approximate age
        age_parts = age_group.split('-')
        try:
            min_age = int(age_parts[0])
        except (IndexError, ValueError):
            min_age = 6  # Default
            
        # Adjust font size based on age (younger = larger font)
        font_size = max(18, 30 - min_age * 2)
        
        # Adjust image ratio based on age and content type
        if content_type == "early_reader":
            image_text_ratio = 0.7  # 70% image for early readers
            image_frequency = 1  # Every page
        elif content_type == "picture_book":
            image_text_ratio = 0.5  # 50% image for picture books
            image_frequency = 1  # Every page
        else:  # chapter_book
            image_text_ratio = 0.3  # 30% image for chapter books
            image_frequency = 2  # Every other page
            
        # SEND adaptations
        if is_send:
            font_size += 2  # Larger font
            line_spacing = 2.0  # More space between lines
            margins = {"left": 1.2, "right": 1.2, "top": 1.2, "bottom": 1.2}
        else:
            line_spacing = 1.5
            margins = {"left": 1.0, "right": 1.0, "top": 1.0, "bottom": 1.0}
            
        recommendations = {
            "font_size": font_size,
            "font_family": "Comic Sans MS" if min_age < 8 else "Verdana",
            "line_spacing": line_spacing,
            "image_text_ratio": image_text_ratio,
            "image_frequency": image_frequency,
            "margins": margins,
            "content_type": content_type,
            "layout_pattern": "image-top-text-bottom" if min_age < 6 else "image-left-text-right"
        }
        
        # Add EPUB-specific recommendations if needed
        if output_format in ["epub", "both"]:
            recommendations.update({
                "epub_specific": {
                    "use_responsive_layout": True,
                    "preferred_image_format": "webp",  # More efficient than JPG/PNG for EPUB
                    "max_image_width": "100%",  # Responsive image width
                    "semantic_headings": True,  # Use proper H1, H2, etc.
                    "include_toc": True,  # Include table of contents
                    "accessibility_features": ["alt_text", "semantic_markup", "aria_labels"]
                }
            })
            
        return recommendations
