
"""
Domain entities for the embroidery categorizer.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .value_objects import Category, FilePath


@dataclass
class EmbroideryFile:
    """
    Main entity representing an embroidery file.
    """
    original_path: FilePath
    name: str
    category: Optional[Category] = None
    jpg_path: Optional[FilePath] = None
    
    @property
    def file_extension(self) -> str:
        """Returns the file extension."""
        return self.original_path.path.suffix.lower()
    
    @property
    def is_pes_file(self) -> bool:
        """Checks if it's a .PES file."""
        return self.file_extension == '.pes'
    
    def assign_category(self, category: Category) -> None:
        """Assigns a category to the file."""
        self.category = category
    
    def set_jpg_path(self, jpg_path: FilePath) -> None:
        """Sets the path of the converted JPG image."""
        self.jpg_path = jpg_path
    
    def __str__(self) -> str:
        return f"EmbroideryFile(name={self.name}, category={self.category})"
