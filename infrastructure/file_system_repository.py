
"""
File system repository implementation.
"""
import shutil
from pathlib import Path
from typing import List
from loguru import logger

from domain.repositories import EmbroideryFileRepository
from domain.entities import EmbroideryFile
from domain.value_objects import FilePath, Category
from domain.exceptions import FileNotFoundError, RepositoryError


class FileSystemRepository(EmbroideryFileRepository):
    """
    File system repository implementation.
    """
    
    def find_pes_files_in_directory(self, directory_path: FilePath) -> List[EmbroideryFile]:
        """
        Finds all .PES files in a directory.
        """
        logger.info(f"Searching for .PES files in: {directory_path}")
        
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory_path.is_directory():
            raise RepositoryError(f"Path is not a directory: {directory_path}")
        
        pes_files = []
        try:
            # Search recursively for .pes files
            for file_path in directory_path.path.rglob("*.pes"):
                if file_path.is_file():
                    embroidery_file = EmbroideryFile(
                        original_path=FilePath(file_path),
                        name=file_path.stem
                    )
                    pes_files.append(embroidery_file)
                    logger.debug(f".PES file found: {file_path}")
            
            # Also search for uppercase .PES files
            for file_path in directory_path.path.rglob("*.PES"):
                if file_path.is_file():
                    embroidery_file = EmbroideryFile(
                        original_path=FilePath(file_path),
                        name=file_path.stem
                    )
                    pes_files.append(embroidery_file)
                    logger.debug(f"Arquivo .PES encontrado: {file_path}")
            
            logger.info(f"Total .PES files found: {len(pes_files)}")
            return pes_files
            
        except Exception as e:
            logger.error(f"Error searching for .PES files: {e}")
            raise RepositoryError(f"Error searching for .PES files: {e}")
    
    def copy_file_to_category_folder(self, file: EmbroideryFile, output_directory: FilePath, language: str = "en") -> bool:
        """
        Copies a file to its category folder.
        """
        if not file.category:
            logger.warning(f"File {file.name} has no category defined")
            return False
        
        try:
            # Create category directory if it doesn't exist
            category_dir = self.create_category_directory(file.category, output_directory, language)
            
            # Copy the original .PES file
            pes_destination_path = category_dir.join(file.original_path.path.name)
            shutil.copy2(str(file.original_path), str(pes_destination_path))
            
            # Also copy the JPG image if available
            folder_name = file.category.get_folder_name(language)
            if file.jpg_path and file.jpg_path.exists():
                jpg_destination_path = category_dir.join(file.jpg_path.path.name)
                shutil.copy2(str(file.jpg_path), str(jpg_destination_path))
                logger.info(f"Files copied: {file.name} (.pes + .jpg) -> {folder_name}/")
            else:
                logger.info(f"File copied: {file.name} (.pes) -> {folder_name}/")
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying file {file.name}: {e}")
            return False
    
    def create_category_directory(self, category: Category, base_path: FilePath, language: str = "en") -> FilePath:
        """
        Creates a directory for a category.
        """
        folder_name = category.get_folder_name(language)
        category_path = base_path.join(folder_name)
        
        try:
            category_path.path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory created/verified: {category_path}")
            return category_path
            
        except Exception as e:
            logger.error(f"Error creating category directory {category.name}: {e}")
            raise RepositoryError(f"Error creating category directory: {e}")
    
    def file_exists(self, file_path: FilePath) -> bool:
        """
        Checks if a file exists.
        """
        return file_path.exists() and file_path.is_file()
