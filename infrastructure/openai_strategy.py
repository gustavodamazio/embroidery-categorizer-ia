
"""
OpenAI categorization strategy implementation.
"""
import base64
import os
import time
from typing import Optional
from openai import OpenAI
from loguru import logger

from domain.repositories import CategorizationRepository
from domain.value_objects import FilePath, Category
from domain.exceptions import CategorizationError, ConfigurationError


class OpenAICategorizationStrategy(CategorizationRepository):
    """
    OpenAI Vision API categorization strategy implementation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_key:
            raise ConfigurationError("OpenAI API key not found. Set OPENAI_API_KEY.")
        
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)
        
        # Prompt for embroidery categorization
        self.categorization_prompt = """
        Analyze this embroidery image and categorize it into ONE of the following main categories:

        - teddy_bears (teddy bears, bears)
        - angels (angels)
        - names (names, text, letters)
        - cars (cars, vehicles)
        - flowers (flowers, floral)
        - animals (animals, pets)
        - hearts (hearts, love)
        - stars (stars)
        - butterflies (butterflies)
        - babies (babies, children)
        - christmas (christmas, holiday)
        - easter (easter)
        - sports (sports)
        - food (food)
        - nature (nature, trees)
        - other (other)

        Respond ONLY with the category name in English, as one word, without additional explanations.
        Valid response examples: "teddy_bears", "flowers", "names", "cars"
        """
    
    def categorize_image(self, image_path: FilePath) -> Optional[Category]:
        """
        Categorizes an image using OpenAI Vision API with retry and timeout.
        """
        logger.info(f"Categorizing image: {image_path.path.name}")
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            return None
        
        # Encode image to base64 once
        try:
            with open(str(image_path), "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error reading image {image_path.path.name}: {e}")
            return Category("other")
        
        # Attempt categorization with retry
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries} for {image_path.path.name}")
                
                # Make request to OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self.categorization_prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "low"  # Use low resolution to save tokens
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=50,
                    temperature=0.1  # Low temperature for more consistent responses
                )
                
                # Extract category from response
                category_text = response.choices[0].message.content.strip().lower()
                
                # Clean and validate response
                category = Category.from_ai_response(category_text)
                
                if category.is_valid():
                    logger.info(f"Category identified: {category.name}")
                    return category
                else:
                    logger.warning(f"Invalid category returned by AI: {category_text}")
                    return Category("other")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {image_path.path.name}: {e}")
                
                if attempt < self.max_retries - 1:
                    # Wait progressively longer between attempts
                    wait_time = (attempt + 1) * 2
                    logger.info(f"Waiting {wait_time}s before next attempt...")
                    time.sleep(wait_time)
                else:
                    # Last attempt failed
                    logger.error(f"All attempts failed for {image_path.path.name}: {e}")
                    logger.info(f"Categorizing {image_path.path.name} as 'other' and continuing processing")
                    return Category("other")
    
    def is_available(self) -> bool:
        """
        Checks if the categorization service is available.
        """
        try:
            # Test simple request with timeout
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for testing
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                timeout=10  # Short timeout for quick check
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI service not available: {e}")
            return False
    
    def get_supported_categories(self) -> list[str]:
        """
        Returns the list of supported categories.
        """
        return [
            "teddy_bears", "angels", "names", "cars", "flowers",
            "animals", "hearts", "stars", "butterflies", "babies",
            "christmas", "easter", "sports", "food", "nature", "other"
        ]
