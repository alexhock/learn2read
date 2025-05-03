"""
Module for generating images using OpenAI's DALL-E API.
"""

import os
import requests
from PIL import Image
from io import BytesIO
import openai

class OpenAIGenerator:
    """Generates images using OpenAI's DALL-E API."""
    
    def __init__(self, api_key=None, model="dall-e-3"):
        """
        Initialize OpenAI image generator.
        
        Args:
            api_key (str): OpenAI API key (defaults to environment variable)
            model (str): DALL-E model to use
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model
        openai.api_key = self.api_key
    
    def generate_image(self, prompt, size="1024x1024", quality="standard"):
        """
        Generate an image from a prompt using DALL-E.
        
        Args:
            prompt (str): Image description prompt
            size (str): Image size (e.g., "1024x1024")
            quality (str): Image quality ("standard" or "hd")
            
        Returns:
            Image: PIL Image object
        """
        try:
            response = openai.Image.create(
                prompt=prompt,
                model=self.model,
                size=size,
                quality=quality,
                n=1
            )
            
            # Download the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))
            
            return image
        
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
