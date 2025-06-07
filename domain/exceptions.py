
"""
Domain exceptions for the embroidery categorizer.
"""


class EmbroideryCategorizerException(Exception):
    """Base exception for embroidery categorizer domain."""
    pass


class FileNotFoundError(EmbroideryCategorizerException):
    """Raised when a required file is not found."""
    pass


class InvalidFileFormatError(EmbroideryCategorizerException):
    """Raised when file format is not supported."""
    pass


class ConversionError(EmbroideryCategorizerException):
    """Raised when file conversion fails."""
    pass


class CategorizationError(EmbroideryCategorizerException):
    """Raised when categorization fails."""
    pass


class RepositoryError(EmbroideryCategorizerException):
    """Raised when repository operations fail."""
    pass


class ConfigurationError(EmbroideryCategorizerException):
    """Raised when configuration is invalid."""
    pass
