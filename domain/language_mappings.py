"""
Language mappings for category names.
"""
from typing import Dict, Optional


class LanguageMapper:
    """
    Maps category names between languages for folder creation.
    """
    
    # Mapping from English (AI response) to other languages
    CATEGORY_MAPPINGS: Dict[str, Dict[str, str]] = {
        "en": {
            "teddy_bears": "teddy_bears",
            "angels": "angels", 
            "names": "names",
            "cars": "cars",
            "flowers": "flowers",
            "animals": "animals",
            "hearts": "hearts",
            "stars": "stars",
            "butterflies": "butterflies",
            "babies": "babies",
            "christmas": "christmas",
            "easter": "easter",
            "sports": "sports",
            "food": "food",
            "nature": "nature",
            "other": "other"
        },
        "pt-BR": {
            "teddy_bears": "ursinhos",
            "angels": "anjos", 
            "names": "nomes",
            "cars": "carrinhos",
            "flowers": "flores",
            "animals": "animais",
            "hearts": "coracoes",
            "stars": "estrelas",
            "butterflies": "borboletas",
            "babies": "bebes",
            "christmas": "natal",
            "easter": "pascoa",
            "sports": "esportes",
            "food": "comida",
            "nature": "natureza",
            "other": "outros"
        }
    }
    
    @classmethod
    def get_folder_name(cls, english_category: str, language: str = "en") -> str:
        """
        Get the folder name for a category in the specified language.
        
        Args:
            english_category: The category name in English (as returned by AI)
            language: Target language code ("en" or "pt-BR")
        
        Returns:
            The folder name in the target language
        """
        if language not in cls.CATEGORY_MAPPINGS:
            # Default to English if language not supported
            language = "en"
        
        mapping = cls.CATEGORY_MAPPINGS[language]
        return mapping.get(english_category, english_category)
    
    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of supported language codes
        """
        return list(cls.CATEGORY_MAPPINGS.keys())
    
    @classmethod
    def is_language_supported(cls, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language: Language code to check
        
        Returns:
            True if language is supported, False otherwise
        """
        return language in cls.CATEGORY_MAPPINGS