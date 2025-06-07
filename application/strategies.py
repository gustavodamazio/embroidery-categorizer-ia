
"""
Strategy pattern implementations for categorization services.
"""
from abc import ABC, abstractmethod
from typing import Optional
from domain.value_objects import FilePath, Category


class CategorizationStrategy(ABC):
    """
    Interface for categorization strategies.
    """
    
    @abstractmethod
    def categorize_image(self, image_path: FilePath) -> Optional[Category]:
        """
        Categorizes an image and returns the category.
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Checks if the strategy is available for use.
        """
        pass


class CategorizationContext:
    """
    Context for the categorization Strategy pattern.
    """
    
    def __init__(self, strategy: CategorizationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: CategorizationStrategy) -> None:
        """
        Sets a new categorization strategy.
        """
        self._strategy = strategy
    
    def categorize_image(self, image_path: FilePath) -> Optional[Category]:
        """
        Executes categorization using the current strategy.
        """
        if not self._strategy.is_available():
            raise RuntimeError("Categorization strategy is not available")
        
        return self._strategy.categorize_image(image_path)
    
    def is_available(self) -> bool:
        """
        Checks if the current strategy is available.
        """
        return self._strategy.is_available()
