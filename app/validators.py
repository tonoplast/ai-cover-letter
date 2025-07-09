"""
Input validation utilities for the AI Cover Letter Generator.
"""

import re
import os
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, UploadFile
from app.exceptions import ValidationError

class InputValidator:
    """Comprehensive input validation utilities."""
    
    # File validation constants
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILENAME_LENGTH = 255
    
    # Text validation constants
    MAX_TEXT_LENGTH = 10000
    MIN_TEXT_LENGTH = 5
    MAX_COMPANY_NAME_LENGTH = 100
    MAX_JOB_TITLE_LENGTH = 100
    
    # API validation constants
    MAX_BATCH_SIZE = 10
    MIN_DELAY_SECONDS = 1
    MAX_DELAY_SECONDS = 60
    
    # Regex patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Dangerous file patterns
    DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.sh', '.cmd', '.scr', '.vbs', '.js', '.jar'}
    
    @staticmethod
    def validate_file_upload(file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file."""
        if not file:
            raise ValidationError("No file provided")
        
        if not file.filename:
            raise ValidationError("Filename is required")
        
        # Check filename length
        if len(file.filename) > InputValidator.MAX_FILENAME_LENGTH:
            raise ValidationError(f"Filename too long (max {InputValidator.MAX_FILENAME_LENGTH} characters)")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext in InputValidator.DANGEROUS_EXTENSIONS:
            raise ValidationError(f"Dangerous file type not allowed: {file_ext}")
        
        if file_ext not in InputValidator.ALLOWED_EXTENSIONS:
            raise ValidationError(f"File type not supported: {file_ext}. Allowed: {', '.join(InputValidator.ALLOWED_EXTENSIONS)}")
        
        # Check file size
        if hasattr(file, 'size') and file.size:
            if file.size > InputValidator.MAX_FILE_SIZE:
                raise ValidationError(f"File too large (max {InputValidator.MAX_FILE_SIZE / 1024 / 1024}MB)")
        
        # Validate MIME type if available
        if hasattr(file, 'content_type') and file.content_type:
            InputValidator._validate_mime_type(file.content_type, file_ext)
        
        return {
            "filename": file.filename,
            "extension": file_ext,
            "valid": True
        }
    
    @staticmethod
    def _validate_mime_type(content_type: str, file_ext: str) -> None:
        """Validate MIME type matches file extension."""
        mime_mappings = {
            '.pdf': ['application/pdf'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.doc': ['application/msword'],
            '.txt': ['text/plain'],
            '.csv': ['text/csv', 'application/csv'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        }
        
        expected_mimes = mime_mappings.get(file_ext, [])
        if expected_mimes and content_type not in expected_mimes:
            # Only warn, don't block (MIME types can be unreliable)
            pass
    
    @staticmethod
    def validate_text_input(text: str, field_name: str, min_length: int = None, max_length: int = None) -> str:
        """Validate text input."""
        if not text:
            raise ValidationError(f"{field_name} cannot be empty")
        
        if not isinstance(text, str):
            raise ValidationError(f"{field_name} must be a string")
        
        text = text.strip()
        
        if not text:
            raise ValidationError(f"{field_name} cannot be empty or whitespace only")
        
        min_len = min_length or InputValidator.MIN_TEXT_LENGTH
        max_len = max_length or InputValidator.MAX_TEXT_LENGTH
        
        if len(text) < min_len:
            raise ValidationError(f"{field_name} must be at least {min_len} characters")
        
        if len(text) > max_len:
            raise ValidationError(f"{field_name} must be no more than {max_len} characters")
        
        # Check for potentially malicious content
        InputValidator._check_malicious_content(text, field_name)
        
        return text
    
    @staticmethod
    def _check_malicious_content(text: str, field_name: str) -> None:
        """Check for potentially malicious content."""
        # Check for script tags
        if re.search(r'<script[^>]*>.*?</script>', text, re.IGNORECASE | re.DOTALL):
            raise ValidationError(f"{field_name} contains potentially malicious content")
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'union\s+select', r'drop\s+table', r'delete\s+from', r'insert\s+into',
            r'update\s+set', r'exec\s*\(', r'execute\s*\(', r'sp_executesql'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValidationError(f"{field_name} contains potentially malicious content")
        
        # Check for path traversal
        if '..' in text or '~/' in text:
            raise ValidationError(f"{field_name} contains potentially malicious content")
    
    @staticmethod
    def validate_company_name(company_name: str) -> str:
        """Validate company name."""
        return InputValidator.validate_text_input(
            company_name, 
            "Company name", 
            min_length=1, 
            max_length=InputValidator.MAX_COMPANY_NAME_LENGTH
        )
    
    @staticmethod
    def validate_job_title(job_title: str) -> str:
        """Validate job title."""
        return InputValidator.validate_text_input(
            job_title, 
            "Job title", 
            min_length=1, 
            max_length=InputValidator.MAX_JOB_TITLE_LENGTH
        )
    
    @staticmethod
    def validate_job_description(job_description: str) -> str:
        """Validate job description."""
        return InputValidator.validate_text_input(
            job_description, 
            "Job description", 
            min_length=20, 
            max_length=InputValidator.MAX_TEXT_LENGTH
        )
    
    @staticmethod
    def validate_document_type(document_type: str) -> str:
        """Validate document type."""
        if not document_type:
            raise ValidationError("Document type is required")
        
        allowed_types = {'cv', 'cover_letter', 'linkedin', 'other'}
        
        if document_type not in allowed_types:
            raise ValidationError(f"Invalid document type. Must be one of: {', '.join(allowed_types)}")
        
        return document_type
    
    @staticmethod
    def validate_tone(tone: str) -> str:
        """Validate tone parameter."""
        if not tone:
            return "professional"  # Default
        
        allowed_tones = {'professional', 'casual', 'enthusiastic', 'formal', 'confident'}
        
        if tone not in allowed_tones:
            raise ValidationError(f"Invalid tone. Must be one of: {', '.join(allowed_tones)}")
        
        return tone
    
    @staticmethod
    def validate_url(url: str, field_name: str = "URL") -> str:
        """Validate URL format."""
        if not url:
            raise ValidationError(f"{field_name} cannot be empty")
        
        if not InputValidator.URL_PATTERN.match(url):
            raise ValidationError(f"Invalid {field_name} format")
        
        # Check for suspicious domains
        suspicious_domains = ['localhost', '127.0.0.1', '0.0.0.0', 'file://']
        if any(domain in url.lower() for domain in suspicious_domains):
            raise ValidationError(f"{field_name} contains suspicious domain")
        
        return url
    
    @staticmethod
    def validate_urls_list(urls: List[str], max_count: int = None) -> List[str]:
        """Validate list of URLs."""
        if not urls:
            raise ValidationError("URLs list cannot be empty")
        
        if not isinstance(urls, list):
            raise ValidationError("URLs must be a list")
        
        max_count = max_count or InputValidator.MAX_BATCH_SIZE
        
        if len(urls) > max_count:
            raise ValidationError(f"Too many URLs (max {max_count})")
        
        validated_urls = []
        for i, url in enumerate(urls):
            try:
                validated_url = InputValidator.validate_url(url, f"URL {i+1}")
                validated_urls.append(validated_url)
            except ValidationError as e:
                raise ValidationError(f"Invalid URL at position {i+1}: {str(e)}")
        
        return validated_urls
    
    @staticmethod
    def validate_delay_seconds(delay: int) -> int:
        """Validate delay seconds for batch operations."""
        if delay is None:
            return 3  # Default
        
        if not isinstance(delay, int):
            raise ValidationError("Delay must be an integer")
        
        if delay < InputValidator.MIN_DELAY_SECONDS:
            raise ValidationError(f"Delay must be at least {InputValidator.MIN_DELAY_SECONDS} seconds")
        
        if delay > InputValidator.MAX_DELAY_SECONDS:
            raise ValidationError(f"Delay must be no more than {InputValidator.MAX_DELAY_SECONDS} seconds")
        
        return delay
    
    @staticmethod
    def validate_llm_parameters(max_tokens: int = None, temperature: float = None) -> Dict[str, Union[int, float]]:
        """Validate LLM generation parameters."""
        result = {}
        
        if max_tokens is not None:
            if not isinstance(max_tokens, int):
                raise ValidationError("max_tokens must be an integer")
            if max_tokens < 1 or max_tokens > 4096:
                raise ValidationError("max_tokens must be between 1 and 4096")
            result['max_tokens'] = max_tokens
        
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                raise ValidationError("temperature must be a number")
            if temperature < 0 or temperature > 2:
                raise ValidationError("temperature must be between 0 and 2")
            result['temperature'] = float(temperature)
        
        return result
    
    @staticmethod
    def validate_provider_and_model(provider: str = None, model: str = None) -> Dict[str, Optional[str]]:
        """Validate LLM provider and model."""
        if provider is not None:
            allowed_providers = {'ollama', 'openai', 'anthropic', 'google', 'auto'}
            if provider not in allowed_providers:
                raise ValidationError(f"Invalid provider. Must be one of: {', '.join(allowed_providers)}")
        
        if model is not None:
            # Basic validation - specific model validation should be done by LLM service
            if not isinstance(model, str) or not model.strip():
                raise ValidationError("Model must be a non-empty string")
            
            if len(model) > 100:
                raise ValidationError("Model name too long")
        
        return {
            'provider': provider,
            'model': model
        }
    
    @staticmethod
    def validate_country(country: str = None) -> Optional[str]:
        """Validate country parameter."""
        if not country:
            return None
        
        # List of supported countries for research
        supported_countries = {
            'australia', 'united states', 'canada', 'united kingdom', 'germany', 
            'france', 'netherlands', 'sweden', 'norway', 'denmark', 'finland', 
            'switzerland', 'singapore', 'japan', 'south korea', 'new zealand', 
            'ireland', 'belgium', 'austria'
        }
        
        country_lower = country.lower().strip()
        if country_lower not in supported_countries:
            raise ValidationError(f"Unsupported country. Must be one of: {', '.join(supported_countries)}")
        
        return country_lower.title()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not filename:
            return "unnamed_file"
        
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = filename.strip()
        
        # Ensure filename isn't too long
        if len(filename) > InputValidator.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            max_name_len = InputValidator.MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_len] + ext
        
        return filename or "unnamed_file"