
"""
Value objects for the embroidery categorizer domain.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Union
from .language_mappings import LanguageMapper


@dataclass(frozen=True)
class FilePath:
    """
    Value object representing a file path.
    """
    path: Path
    
    def __post_init__(self):
        if not isinstance(self.path, Path):
            object.__setattr__(self, 'path', Path(self.path))
    
    @classmethod
    def from_string(cls, path_str: str) -> 'FilePath':
        """Creates a FilePath from a string."""
        return cls(Path(path_str))
    
    def exists(self) -> bool:
        """Checks if the file exists."""
        return self.path.exists()
    
    def is_file(self) -> bool:
        """Checks if it's a file."""
        return self.path.is_file()
    
    def is_directory(self) -> bool:
        """Checks if it's a directory."""
        return self.path.is_dir()
    
    def parent(self) -> 'FilePath':
        """Returns the parent directory."""
        return FilePath(self.path.parent)
    
    def join(self, *parts: str) -> 'FilePath':
        """Joins path parts."""
        return FilePath(self.path.joinpath(*parts))
    
    def __str__(self) -> str:
        return str(self.path)


@dataclass(frozen=True)
class Category:
    """
    Value object representing an embroidery category.
    """
    name: str
    confidence: float = 1.0
    
    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Category name cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Normalize category name
        normalized_name = self.name.strip().lower().replace(' ', '_')
        object.__setattr__(self, 'name', normalized_name)
    
    @classmethod
    def from_ai_response(cls, ai_response: str, confidence: float = 1.0) -> 'Category':
        """
        Creates a category from AI response.
        """
        # Remove special characters and normalize
        clean_name = ai_response.strip().lower()
        # Remove common punctuation
        for char in '.,!?;:"()[]{}':
            clean_name = clean_name.replace(char, '')
        
        return cls(clean_name, confidence)
    
    def is_valid(self) -> bool:
        """Checks if the category is valid."""
        return bool(self.name and self.name.strip())
    
    def get_folder_name(self, language: str = "en") -> str:
        """Gets the folder name in the specified language."""
        return LanguageMapper.get_folder_name(self.name, language)
    
    def __str__(self) -> str:
        return self.name
