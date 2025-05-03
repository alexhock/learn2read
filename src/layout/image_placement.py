"""
Image Placement Engine - Determines optimal image placement relative to text
"""

from typing import List, Dict, Any


class ImagePlacementEngine:
    """Handles the positioning of images in relation to text"""
    
    def __init__(self, config):
        self.config = config
        
    def calculate_image_position(self, text_chunks: List[Dict], image: Any) -> Dict[str, Any]:
        """
        Calculate the optimal position for an image based on text content
        
        Args:
            text_chunks: Text content for the page
            image: Image object or reference
            
        Returns:
            Dictionary with image position information
        """
        # Get image aspect ratio (if available)
        # This would be more sophisticated in a real implementation
        aspect_ratio = self._get_image_aspect_ratio(image)
        
        # Determine positioning strategy based on text and LLM recommendations
        total_text = sum(len(chunk.get('text', '')) for chunk in text_chunks)
        
        # For very young readers, prefer images on top or left
        if self.config.age_group.startswith(('3-', '4-', '5-')):
            if aspect_ratio > 1.2:  # Wider image
                position = 'top'
            else:
                position = 'left'
                
        # For slightly older readers, we can use more varied layouts
        elif self.config.age_group.startswith(('6-', '7-', '8-')):
            if total_text < 100:  # Short text, give image prominence
                position = 'top' if aspect_ratio > 1 else 'left'
            else:
                # Alternate between positions for visual interest
                import random
                position = random.choice(['top', 'bottom', 'left', 'right'])
                
        # For older readers
        else:
            if aspect_ratio > 1.5:  # Very wide image
                position = 'top'
            elif aspect_ratio < 0.7:  # Very tall image
                position = 'right'
            else:
                # Prefer side-by-side layout for older readers
                position = 'left'
        
        # Calculate size - adjust based on the image_text_ratio in config
        size = self.config.image_text_ratio
        
        # For SEND adaptations, we might want more consistency
        if self.config.is_send_adapted:
            # More predictable layouts for SEND readers
            position = 'top'  # Consistent position
            
        return {
            'position': position,
            'size': size,
            'aspect_ratio': aspect_ratio,
            'alt_text': self._generate_alt_text(image, text_chunks)
        }
        
    def _get_image_aspect_ratio(self, image: Any) -> float:
        """
        Calculate image aspect ratio (width/height)
        
        In a real implementation, this would extract the actual dimensions
        from the image file or object.
        """
        # Default to square if we can't determine
        return getattr(image, 'aspect_ratio', 1.0)
        
    def _generate_alt_text(self, image: Any, text_chunks: List[Dict]) -> str:
        """
        Generate alt text for the image based on context
        
        In a production implementation, this might use the LLM to generate
        descriptive alt text based on the image and surrounding content.
        """
        # Use existing alt text if available
        if hasattr(image, 'alt_text') and image.alt_text:
            return image.alt_text
            
        # For a simple implementation, use the first sentence of text
        for chunk in text_chunks:
            text = chunk.get('text', '')
            if text:
                # Extract first sentence or up to 100 chars
                alt_text = text.split('.')[0]
                if len(alt_text) > 100:
                    alt_text = alt_text[:97] + "..."
                return f"Image: {alt_text}"
                
        # Fallback
        return "Illustration for the story"
