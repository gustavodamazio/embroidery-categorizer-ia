
"""
Repository interfaces for the embroidery categorizer domain.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import EmbroideryFile
from .value_objects import FilePath, Category


class EmbroideryFileRepository(ABC):
    """
    Interface for embroidery file repository.
    """
    
    @abstractmethod
    def find_pes_files_in_directory(self, directory_path: FilePath) -> List[EmbroideryFile]:
        """
        Finds all .PES files in a directory.
        """
        pass
    
    @abstractmethod
    def copy_file_to_category_folder(self, file: EmbroideryFile, output_directory: FilePath, language: str = "en") -> bool:
        """
        Copies a file to its category folder.
        """
        pass
    
    @abstractmethod
    def create_category_directory(self, category: Category, base_path: FilePath, language: str = "en") -> FilePath:
        """
        Creates a directory for a category.
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: FilePath) -> bool:
        """
        Checks if a file exists.
        """
        pass


class ImageConverterRepository(ABC):
    """
    Interface for converting embroidery files to images.
    """
    
    @abstractmethod
    def convert_pes_to_jpg(self, pes_file_path: FilePath, output_path: FilePath) -> bool:
        """
        Converts a .PES file to JPG.
        """
        pass
    
    @abstractmethod
    def cleanup_temporary_images(self, image_paths: List[FilePath]) -> None:
        """
        Removes temporary images.
        """
        pass


class CategorizationRepository(ABC):
    """
    Interface for AI categorization services.
    """
    
    @abstractmethod
    def categorize_image(self, image_path: FilePath) -> Optional[Category]:
        """
        Categorizes an image using AI.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Checks if the categorization service is available.
        """
        pass
