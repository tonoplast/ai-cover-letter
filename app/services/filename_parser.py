import re
from datetime import datetime
from typing import Optional, Dict, Any
import os

class FilenameParser:
    """
    Parser for extracting date and document type information from filenames.
    
    Expected format: YYYY-MM-DD_Type_Company-Name.ext
    Examples:
    - 2025-05-01_CV_Data-Science.pdf
    - 2024-10-21_Cover-Letter_Lookahead.pdf
    - 2023-09-01_CV_Neuroscience.pdf
    """
    
    @staticmethod
    def parse_filename(filename: str) -> Dict[str, Any]:
        """
        Parse a filename to extract date, document type, and company information.
        
        Args:
            filename: The filename to parse (e.g., "2025-05-01_CV_Data-Science.pdf")
            
        Returns:
            Dictionary containing:
            - date: datetime object if found, None otherwise
            - document_type: extracted document type (cv, cover_letter, etc.)
            - company: company name if found, None otherwise
            - original_filename: the original filename
            - is_valid_format: boolean indicating if the format was recognized
        """
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        
        # Split by underscore
        parts = name_without_ext.split('_')
        
        result = {
            'date': None,
            'document_type': None,
            'company': None,
            'original_filename': filename,
            'is_valid_format': False
        }
        
        if len(parts) < 2:
            return result
        
        # Try to parse the first part as a date
        date_str = parts[0]
        parsed_date = FilenameParser._parse_date(date_str)
        if parsed_date:
            result['date'] = parsed_date
            result['is_valid_format'] = True
        
        # Extract document type from second part
        if len(parts) >= 2:
            doc_type = parts[1].lower()
            # Map common variations to standard types
            doc_type_mapping = {
                'cv': 'cv',
                'resume': 'cv',
                'cover-letter': 'cover_letter',
                'coverletter': 'cover_letter',
                'linkedin': 'linkedin',
                'profile': 'linkedin'
            }
            result['document_type'] = doc_type_mapping.get(doc_type, doc_type)
        
        # Extract company name from remaining parts
        if len(parts) >= 3:
            company_parts = parts[2:]
            result['company'] = '_'.join(company_parts)
        
        return result
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats.
        
        Args:
            date_str: Date string to parse
            
        Returns:
            datetime object if successful, None otherwise
        """
        # Common date formats
        date_formats = [
            '%Y-%m-%d',      # 2025-05-01
            '%Y-%m-%d',      # 2025-5-1
            '%d-%m-%Y',      # 01-05-2025
            '%m-%d-%Y',      # 05-01-2025
            '%Y/%m/%d',      # 2025/05/01
            '%d/%m/%Y',      # 01/05/2025
            '%m/%d/%Y',      # 05/01/2025
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def extract_date_from_filename(filename: str) -> Optional[datetime]:
        """
        Extract date from filename if it follows the expected format.
        
        Args:
            filename: The filename to parse
            
        Returns:
            datetime object if date found, None otherwise
        """
        parsed = FilenameParser.parse_filename(filename)
        return parsed.get('date')
    
    @staticmethod
    def extract_document_type_from_filename(filename: str) -> Optional[str]:
        """
        Extract document type from filename if it follows the expected format.
        
        Args:
            filename: The filename to parse
            
        Returns:
            Document type string if found, None otherwise
        """
        parsed = FilenameParser.parse_filename(filename)
        return parsed.get('document_type')
    
    @staticmethod
    def extract_company_from_filename(filename: str) -> Optional[str]:
        """
        Extract company name from filename if it follows the expected format.
        
        Args:
            filename: The filename to parse
            
        Returns:
            Company name string if found, None otherwise
        """
        parsed = FilenameParser.parse_filename(filename)
        return parsed.get('company')
    
    @staticmethod
    def is_valid_filename_format(filename: str) -> bool:
        """
        Check if filename follows the expected format.
        
        Args:
            filename: The filename to check
            
        Returns:
            True if format is recognized, False otherwise
        """
        parsed = FilenameParser.parse_filename(filename)
        return parsed.get('is_valid_format', False)
    
    @staticmethod
    def generate_filename(date: datetime, document_type: str, company: Optional[str] = None, extension: str = "pdf") -> str:
        """
        Generate a filename in the expected format.
        
        Args:
            date: Date for the document
            document_type: Type of document (cv, cover_letter, etc.)
            company: Company name (optional)
            extension: File extension (default: pdf)
            
        Returns:
            Formatted filename string
        """
        date_str = date.strftime('%Y-%m-%d')
        
        # Map document types to filename format
        type_mapping = {
            'cv': 'CV',
            'cover_letter': 'Cover-Letter',
            'linkedin': 'LinkedIn',
            'other': 'Other'
        }
        
        type_str = type_mapping.get(document_type.lower(), document_type.title())
        
        if company:
            # Replace spaces and special characters with hyphens
            company_clean = re.sub(r'[^\w\s-]', '', str(company))
            company_clean = re.sub(r'[-\s]+', '-', company_clean).strip('-')
            filename = f"{date_str}_{type_str}_{company_clean}.{extension}"
        else:
            filename = f"{date_str}_{type_str}.{extension}"
        
        return filename 