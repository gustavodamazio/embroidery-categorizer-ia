
"""
Application services for the embroidery categorizer.
"""
from typing import List, Optional
from loguru import logger

from domain.entities import EmbroideryFile
from domain.value_objects import FilePath, Category
from domain.repositories import EmbroideryFileRepository, ImageConverterRepository
from infrastructure.pyembroidery_converter import PyEmbroideryConverter
from application.strategies import CategorizationContext


class CategorizationService:
    """
    Application service for embroidery file categorization.
    """
    
    def __init__(
        self,
        file_repository: EmbroideryFileRepository,
        image_converter: ImageConverterRepository,
        categorization_context: CategorizationContext
    ):
        self.file_repository = file_repository
        self.image_converter = image_converter
        self.categorization_context = categorization_context
        self.temp_images: List[FilePath] = []
    
    def categorize_files_in_directory(
        self,
        input_directory: FilePath,
        output_directory: FilePath,
        start_after: int = None,
        language: str = "en"
    ) -> dict:
        """
        Categorizes all .PES files in a directory.
        """
        logger.info(f"Starting file categorization in: {input_directory}")
        
        results = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "categories_found": set(),
            "errors": []
        }
        
        try:
            # Check if categorization service is available
            if not self.categorization_context.is_available():
                raise RuntimeError("Categorization service is not available")
            
            # Find all .PES files
            embroidery_files = self.file_repository.find_pes_files_in_directory(input_directory)
            results["total_files"] = len(embroidery_files)
            
            if not embroidery_files:
                logger.warning("No .PES files found in directory")
                return results
            
            # Implement start_after logic
            if start_after is not None:
                logger.info(f"Starting processing from file number {start_after + 1}")
                results["skipped_files"] = start_after
            else:
                results["skipped_files"] = 0
            
            # Process each file
            for index, file in enumerate(embroidery_files, 1):
                # Skip files if start_after was specified
                if start_after is not None and index <= start_after:
                    logger.debug(f"Skipping file {index}: {file.name}")
                    continue
                
                logger.info(f"Processing file {index}/{len(embroidery_files)}: {file.name}")
                
                try:
                    success = self._process_single_file(file, output_directory, index, language)
                    if success:
                        results["processed_files"] += 1
                        if file.category:
                            results["categories_found"].add(file.category.name)
                    else:
                        results["failed_files"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing file {index} - {file.name}: {e}")
                    results["failed_files"] += 1
                    results["errors"].append(f"{file.name}: {str(e)}")
            
            # Clean up temporary images
            self._cleanup_temp_images()
            
            logger.info(f"Categorization completed. Processed: {results['processed_files']}, "
                       f"Failed: {results['failed_files']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during categorization: {e}")
            self._cleanup_temp_images()
            results["errors"].append(str(e))
            return results
    
    def _process_single_file(self, file: EmbroideryFile, output_directory: FilePath, file_number: int = None, language: str = "en") -> bool:
        """
        Processes a single embroidery file.
        """
        logger.debug(f"Processing file: {file.name}")
        
        try:
            # Convert .PES to JPG
            temp_jpg_path = self._create_temp_jpg_path(file.name)
            self.temp_images.append(temp_jpg_path)
            
            # Add process number to log
            if file_number:
                logger.info(f"[Process {file_number}] Converting {file.name} to JPG")
            
            conversion_success = self.image_converter.convert_pes_to_jpg(
                file.original_path,
                temp_jpg_path
            )
            
            if not conversion_success:
                logger.error(f"Failed to convert file {file.name}")
                return False
            
            file.set_jpg_path(temp_jpg_path)
            
            # Categorize the image
            if file_number:
                logger.info(f"[Process {file_number}] Categorizing image: {file.name}")
            
            category = self.categorization_context.categorize_image(temp_jpg_path)
            
            if not category:
                logger.warning(f"Could not categorize {file.name}")
                category = Category("other")
            
            file.assign_category(category)
            
            # Copy file to category folder (includes .PES and .JPG)
            if file_number:
                logger.info(f"[Process {file_number}] Copying {file.name} to category: {category.name}")
            
            copy_success = self.file_repository.copy_file_to_category_folder(
                file,
                output_directory,
                language
            )
            
            if not copy_success:
                logger.error(f"Failed to copy file {file.name}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing file {file.name}: {e}")
            return False
    
    def _create_temp_jpg_path(self, pes_file_name: str) -> FilePath:
        """
        Creates a temporary path for the JPG image.
        """
        if isinstance(self.image_converter, PyEmbroideryConverter):
            return self.image_converter.create_temp_jpg_path(pes_file_name)
        else:
            # Fallback for other converters
            import tempfile
            from pathlib import Path
            
            temp_dir = Path(tempfile.gettempdir()) / "embroidery_categorizer"
            temp_dir.mkdir(exist_ok=True)
            
            jpg_name = Path(pes_file_name).stem + ".jpg"
            temp_path = temp_dir / jpg_name
            
            return FilePath(temp_path)
    
    def _cleanup_temp_images(self) -> None:
        """
        Removes all temporary images created.
        """
        if self.temp_images:
            self.image_converter.cleanup_temporary_images(self.temp_images)
            self.temp_images.clear()
    
    def get_categorization_stats(self, results: dict) -> str:
        """
        Generates categorization statistics.
        """
        stats = []
        stats.append(f"📊 Categorization Statistics:")
        stats.append(f"   Total files: {results['total_files']}")
        stats.append(f"   Successfully processed: {results['processed_files']}")
        stats.append(f"   Failed: {results['failed_files']}")
        
        if results['categories_found']:
            stats.append(f"   Categories found: {len(results['categories_found'])}")
            for category in sorted(results['categories_found']):
                stats.append(f"     - {category}")
        
        if results['errors']:
            stats.append(f"   Errors:")
            for error in results['errors'][:5]:  # Show only first 5 errors
                stats.append(f"     - {error}")
            if len(results['errors']) > 5:
                stats.append(f"     ... and {len(results['errors']) - 5} more errors")
        
        return "\n".join(stats)
