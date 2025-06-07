
"""
Use cases for the embroidery categorizer application.
"""
from typing import Dict, Any
from loguru import logger

from domain.value_objects import FilePath
from domain.repositories import EmbroideryFileRepository, ImageConverterRepository
from infrastructure.file_system_repository import FileSystemRepository
from infrastructure.pyembroidery_converter import PyEmbroideryConverter
from infrastructure.openai_strategy import OpenAICategorizationStrategy
from application.strategies import CategorizationContext
from application.services import CategorizationService


class CategorizeFilesUseCase:
    """
    Main use case for embroidery file categorization.
    """
    
    def __init__(
        self,
        file_repository: EmbroideryFileRepository = None,
        image_converter: ImageConverterRepository = None,
        categorization_strategy = None
    ):
        # Use default implementations if not provided
        self.file_repository = file_repository or FileSystemRepository()
        self.image_converter = image_converter or PyEmbroideryConverter()
        
        # Configure categorization strategy
        if categorization_strategy is None:
            categorization_strategy = OpenAICategorizationStrategy()
        
        self.categorization_context = CategorizationContext(categorization_strategy)
        
        # Create categorization service
        self.categorization_service = CategorizationService(
            self.file_repository,
            self.image_converter,
            self.categorization_context
        )
    
    def execute(
        self,
        input_directory: str,
        output_directory: str = None,
        start_after: int = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Executes the categorization use case.
        
        Args:
            input_directory: Directory containing .PES files
            output_directory: Directory where to create categorized folders
            start_after: Process number from which to start (skips previous ones)
            language: Language for folder names ("en" or "pt-BR")
        
        Returns:
            Dictionary with operation results
        """
        logger.info("Starting use case: CategorizeFiles")
        
        # Convert strings to FilePath
        input_path = FilePath.from_string(input_directory)
        
        if output_directory is None:
            output_directory = str(input_path.join("categorized"))
        
        output_path = FilePath.from_string(output_directory)
        
        # Validate directories
        if not input_path.exists():
            error_msg = f"Input directory does not exist: {input_directory}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "categories_found": set(),
                "errors": [error_msg]
            }
        
        if not input_path.is_directory():
            error_msg = f"Input path is not a directory: {input_directory}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "categories_found": set(),
                "errors": [error_msg]
            }
        
        # Create output directory if it doesn't exist
        try:
            output_path.path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory: {output_directory}")
        except Exception as e:
            error_msg = f"Error creating output directory: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "categories_found": set(),
                "errors": [error_msg]
            }
        
        # Execute categorization
        try:
            results = self.categorization_service.categorize_files_in_directory(
                input_path,
                output_path,
                start_after,
                language
            )
            
            # Add success information
            results["success"] = results["failed_files"] < results["total_files"]
            results["input_directory"] = input_directory
            results["output_directory"] = output_directory
            
            # Generate statistics
            results["stats"] = self.categorization_service.get_categorization_stats(results)
            
            logger.info("CategorizeFiles use case completed")
            return results
            
        except Exception as e:
            error_msg = f"Error during use case execution: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0,
                "categories_found": set(),
                "errors": [error_msg],
                "input_directory": input_directory,
                "output_directory": output_directory
            }
    
    def validate_prerequisites(self) -> Dict[str, bool]:
        """
        Validates if all prerequisites are met.
        """
        validation_results = {}
        
        # Check if categorization service is available
        try:
            validation_results["categorization_service"] = self.categorization_context.is_available()
        except Exception as e:
            logger.error(f"Error validating categorization service: {e}")
            validation_results["categorization_service"] = False
        
        # Check if dependencies are installed
        try:
            import pyembroidery
            validation_results["pyembroidery"] = True
        except ImportError:
            validation_results["pyembroidery"] = False
        
        try:
            from PIL import Image
            validation_results["pillow"] = True
        except ImportError:
            validation_results["pillow"] = False
        
        try:
            import openai
            validation_results["openai"] = True
        except ImportError:
            validation_results["openai"] = False
        
        return validation_results
