"""
Custom exceptions for the AI Cover Letter Generator application.
"""

class CoverLetterGeneratorException(Exception):
    """Base exception for all cover letter generator errors."""
    pass

class ValidationError(CoverLetterGeneratorException):
    """Raised when input validation fails."""
    pass

class DocumentParsingError(CoverLetterGeneratorException):
    """Raised when document parsing fails."""
    pass

class LLMServiceError(CoverLetterGeneratorException):
    """Raised when LLM service encounters an error."""
    pass

class LLMConnectionError(LLMServiceError):
    """Raised when LLM service cannot connect."""
    pass

class LLMTimeoutError(LLMServiceError):
    """Raised when LLM service times out."""
    pass

class LLMRateLimitError(LLMServiceError):
    """Raised when LLM service rate limit is exceeded."""
    pass

class CompanyResearchError(CoverLetterGeneratorException):
    """Raised when company research fails."""
    pass

class CompanyResearchTimeoutError(CompanyResearchError):
    """Raised when company research times out."""
    pass

class CompanyResearchRateLimitError(CompanyResearchError):
    """Raised when company research rate limit is exceeded."""
    pass

class RAGServiceError(CoverLetterGeneratorException):
    """Raised when RAG service encounters an error."""
    pass

class EmbeddingError(RAGServiceError):
    """Raised when embedding generation fails."""
    pass

class DatabaseError(CoverLetterGeneratorException):
    """Raised when database operations fail."""
    pass

class FileProcessingError(CoverLetterGeneratorException):
    """Raised when file processing fails."""
    pass

class ConfigurationError(CoverLetterGeneratorException):
    """Raised when configuration is invalid."""
    pass