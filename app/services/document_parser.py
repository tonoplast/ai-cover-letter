from pathlib import Path
import re
import warnings
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
from docx import Document
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Document, Experience, Skill
from app.database import get_db
import json

# Suppress torch warnings about pin_memory
warnings.filterwarnings("ignore", message=".*pin_memory.*")

try:
    from docling.document_converter import DocumentConverter
    DOCILING_AVAILABLE = True
except ImportError:
    DOCILING_AVAILABLE = False

class DoclingDocumentParser:
    def __init__(self):
        if not DOCILING_AVAILABLE:
            raise ImportError("docling is not installed. Please install it with 'pip install docling'.")
        self.converter = DocumentConverter()

    def parse_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """Parse document using docling and extract structured information"""
        result = self.converter.convert(file_path)
        doc = result.document
        # Export to markdown for flexibility
        markdown = doc.export_to_markdown()
        
        # Create parsed_data based on document type
        parsed_data = {
            "content": markdown,
            "document_type": document_type,
            "parser": "docling"
        }
        
        # Add type-specific analysis
        if document_type.lower() == "cover_letter":
            # Use legacy parser methods for analysis
            legacy_parser = LegacyDocumentParser()
            parsed_data.update(legacy_parser._parse_cover_letter(markdown))
        
        # Get document structure as dict
        doc_dict = {
            "content": markdown,
            "parsed_data": parsed_data,
            "document_type": document_type,
            "parser": "docling"
        }
        return doc_dict

class LegacyDocumentParser:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx']
        
    def parse_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """Parse document using legacy methods"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        content = self._extract_content(file_path, file_extension)
        
        if document_type.lower() == 'cv':
            parsed_data = self._parse_cv(content)
        elif document_type.lower() == 'cover_letter':
            parsed_data = self._parse_cover_letter(content)
        elif document_type.lower() == 'linkedin':
            parsed_data = self._parse_linkedin(content)
        else:
            parsed_data = {"content": content}
        
        return {
            "content": content,
            "parsed_data": parsed_data,
            "document_type": document_type,
            "parser": "legacy"
        }
    
    def _extract_content(self, file_path: str, file_extension: str) -> str:
        """Extract text content from different file formats"""
        try:
            if file_extension == '.pdf':
                return self._extract_pdf_content(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_docx_content(file_path)
            elif file_extension == '.txt':
                return self._extract_txt_content(file_path)
            elif file_extension in ['.csv', '.xlsx']:
                return self._extract_excel_content(file_path)
            else:
                return ""
        except Exception as e:
            print(f"Error extracting content from {file_path}: {str(e)}")
            return ""
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF file"""
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text from DOCX or DOC file"""
        try:
            # Try to open as DOCX first
            doc = Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content
        except Exception as e:
            # If it's a .doc file, try to convert it or provide a helpful error
            if file_path.lower().endswith('.doc'):
                print(f"Warning: .doc files are not fully supported. Consider converting to .docx format.")
                print(f"Error details: {str(e)}")
                # Try to extract basic text content as fallback
                try:
                    import win32com.client
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    doc = word.Documents.Open(file_path)
                    content = doc.Content.Text
                    doc.Close()
                    word.Quit()
                    return content
                except ImportError:
                    print("win32com not available. Cannot convert .doc files.")
                    return f"[DOC file content could not be extracted. Please convert to DOCX format.]\nError: {str(e)}"
                except Exception as conv_error:
                    print(f"Failed to convert .doc file: {str(conv_error)}")
                    return f"[DOC file content could not be extracted. Please convert to DOCX format.]\nError: {str(e)}"
            else:
                raise e
    
    def _extract_txt_content(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_excel_content(self, file_path: str) -> str:
        """Extract text from Excel file"""
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        return df.to_string()
    
    def _parse_cv(self, content: str) -> Dict[str, Any]:
        """Parse CV content and extract structured information"""
        parsed_data = {
            "personal_info": self._extract_personal_info(content),
            "experiences": self._extract_experiences(content),
            "education": self._extract_education(content),
            "skills": self._extract_skills(content),
            "summary": self._extract_summary(content)
        }
        return parsed_data
    
    def _parse_cover_letter(self, content: str) -> Dict[str, Any]:
        """Parse cover letter content"""
        return {
            "content": content,
            "writing_style": self._analyze_writing_style(content),
            "key_points": self._extract_key_points(content),
            "tone": self._analyze_tone(content)
        }
    
    def _parse_linkedin(self, content: str) -> Dict[str, Any]:
        """Parse LinkedIn profile content"""
        return {
            "profile_info": self._extract_personal_info(content),
            "experiences": self._extract_experiences(content),
            "skills": self._extract_skills(content),
            "connections": self._extract_connections(content)
        }
    
    def _extract_personal_info(self, content: str) -> Dict[str, str]:
        """Extract personal information from content"""
        personal_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        if emails:
            personal_info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, content)
        if phones:
            personal_info['phone'] = ''.join(phones[0])
        
        # Extract name (simple heuristic)
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line.strip()) > 0 and len(line.split()) <= 4:
                personal_info['name'] = line.strip()
                break
        
        return personal_info
    
    def _extract_experiences(self, content: str) -> List[Dict[str, Any]]:
        """Extract work experiences from content"""
        experiences = []
        
        # Common section headers for experience
        experience_headers = [
            r'work\s+experience',
            r'employment\s+history',
            r'professional\s+experience',
            r'career\s+history',
            r'job\s+history'
        ]
        
        # Find experience section
        experience_section = ""
        for header in experience_headers:
            match = re.search(header, content, re.IGNORECASE)
            if match:
                start_idx = match.end()
                # Find next major section
                next_section = re.search(r'\n\s*[A-Z][A-Z\s]+\n', content[start_idx:])
                if next_section:
                    experience_section = content[start_idx:start_idx + next_section.start()]
                else:
                    experience_section = content[start_idx:]
                break
        
        if not experience_section:
            # Fallback: look for date patterns
            experience_section = content
        
        # Extract individual experiences
        # Look for date patterns and job titles
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\bpresent\b|\bcurrent\b)',
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\bpresent\b|\bcurrent\b)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\bpresent\b|\bcurrent\b)'
        ]
        
        lines = experience_section.split('\n')
        current_experience = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for date patterns
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if current_experience:
                        experiences.append(current_experience)
                    
                    current_experience = {
                        'start_date': match.group(1),
                        'end_date': match.group(2) if match.group(2).lower() not in ['present', 'current'] else None,
                        'is_current': match.group(2).lower() in ['present', 'current']
                    }
                    break
            
            # Extract job title and company
            if current_experience and not current_experience.get('title'):
                # Look for job title patterns
                title_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Director|Lead|Analyst|Consultant|Specialist))',
                    r'([A-Z][A-Za-z\s]+(?:at|@)\s+([A-Z][A-Za-z\s]+))'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, line)
                    if match:
                        if 'at' in line or '@' in line:
                            current_experience['title'] = match.group(1).split('at')[0].split('@')[0].strip()
                            current_experience['company'] = match.group(2).strip()
                        else:
                            current_experience['title'] = match.group(1).strip()
                        break
        
        if current_experience:
            experiences.append(current_experience)
        
        return experiences
    
    def _extract_education(self, content: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Look for education section
        education_patterns = [
            r'education',
            r'academic\s+background',
            r'qualifications'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                # Extract education details
                break
        
        return education
    
    def _extract_skills(self, content: str) -> List[str]:
        """Extract skills from content"""
        skills = []
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|AWS|Docker|Kubernetes|Git|Agile|Scrum)\b',
            r'\b(?:Leadership|Communication|Problem\s+Solving|Team\s+Work|Analytical|Creative)\b'
        ]
        
        for pattern in skill_patterns:
            found_skills = re.findall(pattern, content, re.IGNORECASE)
            skills.extend(found_skills)
        
        # Remove duplicates and clean
        skills = list(set([skill.strip() for skill in skills if skill.strip()]))
        
        return skills
    
    def _extract_summary(self, content: str) -> str:
        """Extract summary/objective section"""
        summary_patterns = [
            r'summary[:\s]*([^\n]+(?:\n[^\n]+)*)',
            r'objective[:\s]*([^\n]+(?:\n[^\n]+)*)',
            r'profile[:\s]*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """Analyze writing style characteristics"""
        sentences = re.split(r'[.!?]+', content)
        words = re.findall(r'\b\w+\b', content.lower())
        
        return {
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            'formal_words': len(re.findall(r'\b(?:therefore|furthermore|moreover|consequently|subsequently)\b', content, re.IGNORECASE)),
            'action_verbs': len(re.findall(r'\b(?:developed|implemented|managed|led|created|designed|built|improved)\b', content, re.IGNORECASE))
        }
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from cover letter"""
        # Look for bullet points or numbered lists
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        
        # Look for sentences with action verbs
        action_pattern = r'[^.!?]*(?:developed|implemented|managed|led|created|designed|built|improved)[^.!?]*[.!?]'
        action_sentences = re.findall(action_pattern, content, re.IGNORECASE)
        
        return bullets + action_sentences[:3]  # Limit to 3 action sentences
    
    def _analyze_tone(self, content: str) -> str:
        """Analyze the tone of the content"""
        enthusiastic_words = len(re.findall(r'\b(?:excited|passionate|thrilled|delighted|enthusiastic)\b', content, re.IGNORECASE))
        formal_words = len(re.findall(r'\b(?:respectfully|sincerely|regards|yours\s+truly)\b', content, re.IGNORECASE))
        
        if enthusiastic_words > 2:
            return "enthusiastic"
        elif formal_words > 1:
            return "formal"
        else:
            return "professional"
    
    def _extract_connections(self, content: str) -> int:
        """Extract number of connections from LinkedIn content"""
        connection_pattern = r'(\d+)\s*connections?'
        match = re.search(connection_pattern, content, re.IGNORECASE)
        return int(match.group(1)) if match else 0

class DocumentParser:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt', '.csv', '.xlsx']
        self.legacy_parser = LegacyDocumentParser()
        self.docling_parser = None
        if DOCILING_AVAILABLE:
            self.docling_parser = DoclingDocumentParser()
        
    def parse_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """Try docling parser first, fallback to legacy parser if needed"""
        file_extension = Path(file_path).suffix.lower()
        
        # Check if docling supports this format
        if self.docling_parser and file_extension in ['.pdf', '.docx', '.txt', '.md']:
            try:
                return self.docling_parser.parse_document(file_path, document_type)
            except Exception as e:
                print(f"Docling parser failed: {e}. Falling back to legacy parser.")
        
        # Fallback to legacy parser
        try:
            return self.legacy_parser.parse_document(file_path, document_type)
        except Exception as e:
            print(f"Legacy parser also failed: {e}")
            # Return a basic structure with error information
            return {
                "content": f"[Error parsing document: {str(e)}]",
                "parsed_data": {"error": str(e)},
                "document_type": document_type,
                "parser": "error"
            }
    

    
    def _extract_personal_info(self, content: str) -> Dict[str, str]:
        """Extract personal information from content"""
        personal_info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        if emails:
            personal_info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, content)
        if phones:
            personal_info['phone'] = ''.join(phones[0])
        
        # Extract name (simple heuristic)
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line.strip()) > 0 and len(line.split()) <= 4:
                personal_info['name'] = line.strip()
                break
        
        return personal_info
    
    def _extract_experiences(self, content: str) -> List[Dict[str, Any]]:
        """Extract work experiences from content"""
        experiences = []
        
        # Common section headers for experience
        experience_headers = [
            r'work\s+experience',
            r'employment\s+history',
            r'professional\s+experience',
            r'career\s+history',
            r'job\s+history'
        ]
        
        # Find experience section
        experience_section = ""
        for header in experience_headers:
            match = re.search(header, content, re.IGNORECASE)
            if match:
                start_idx = match.end()
                # Find next major section
                next_section = re.search(r'\n\s*[A-Z][A-Z\s]+\n', content[start_idx:])
                if next_section:
                    experience_section = content[start_idx:start_idx + next_section.start()]
                else:
                    experience_section = content[start_idx:]
                break
        
        if not experience_section:
            # Fallback: look for date patterns
            experience_section = content
        
        # Extract individual experiences
        # Look for date patterns and job titles
        date_patterns = [
            r'(\d{4})\s*[-–]\s*(\d{4}|\bpresent\b|\bcurrent\b)',
            r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\bpresent\b|\bcurrent\b)',
            r'(\d{1,2}/\d{4})\s*[-–]\s*(\d{1,2}/\d{4}|\bpresent\b|\bcurrent\b)'
        ]
        
        lines = experience_section.split('\n')
        current_experience = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for date patterns
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if current_experience:
                        experiences.append(current_experience)
                    
                    current_experience = {
                        'start_date': match.group(1),
                        'end_date': match.group(2) if match.group(2).lower() not in ['present', 'current'] else None,
                        'is_current': match.group(2).lower() in ['present', 'current']
                    }
                    break
            
            # Extract job title and company
            if current_experience and not current_experience.get('title'):
                # Look for job title patterns
                title_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:Engineer|Developer|Manager|Director|Lead|Analyst|Consultant|Specialist))',
                    r'([A-Z][A-Za-z\s]+(?:at|@)\s+([A-Z][A-Za-z\s]+))'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, line)
                    if match:
                        if 'at' in line or '@' in line:
                            current_experience['title'] = match.group(1).split('at')[0].split('@')[0].strip()
                            current_experience['company'] = match.group(2).strip()
                        else:
                            current_experience['title'] = match.group(1).strip()
                        break
        
        if current_experience:
            experiences.append(current_experience)
        
        return experiences
    
    def _extract_education(self, content: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Look for education section
        education_patterns = [
            r'education',
            r'academic\s+background',
            r'qualifications'
        ]
        
        for pattern in education_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                # Extract education details
                break
        
        return education
    
    def _extract_skills(self, content: str) -> List[str]:
        """Extract skills from content"""
        skills = []
        
        # Common skill patterns
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|AWS|Docker|Kubernetes|Git|Agile|Scrum)\b',
            r'\b(?:Leadership|Communication|Problem\s+Solving|Team\s+Work|Analytical|Creative)\b'
        ]
        
        for pattern in skill_patterns:
            found_skills = re.findall(pattern, content, re.IGNORECASE)
            skills.extend(found_skills)
        
        # Remove duplicates and clean
        skills = list(set([skill.strip() for skill in skills if skill.strip()]))
        
        return skills
    
    def _extract_summary(self, content: str) -> str:
        """Extract summary/objective section"""
        summary_patterns = [
            r'summary[:\s]*([^\n]+(?:\n[^\n]+)*)',
            r'objective[:\s]*([^\n]+(?:\n[^\n]+)*)',
            r'profile[:\s]*([^\n]+(?:\n[^\n]+)*)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """Analyze writing style characteristics"""
        sentences = re.split(r'[.!?]+', content)
        words = re.findall(r'\b\w+\b', content.lower())
        
        return {
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            'formal_words': len(re.findall(r'\b(?:therefore|furthermore|moreover|consequently|subsequently)\b', content, re.IGNORECASE)),
            'action_verbs': len(re.findall(r'\b(?:developed|implemented|managed|led|created|designed|built|improved)\b', content, re.IGNORECASE))
        }
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from cover letter"""
        # Look for bullet points or numbered lists
        bullet_pattern = r'[•\-\*]\s*([^\n]+)'
        bullets = re.findall(bullet_pattern, content)
        
        # Look for sentences with action verbs
        action_pattern = r'[^.!?]*(?:developed|implemented|managed|led|created|designed|built|improved)[^.!?]*[.!?]'
        action_sentences = re.findall(action_pattern, content, re.IGNORECASE)
        
        return bullets + action_sentences[:3]  # Limit to 3 action sentences
    
    def _analyze_tone(self, content: str) -> str:
        """Analyze the tone of the content"""
        enthusiastic_words = len(re.findall(r'\b(?:excited|passionate|thrilled|delighted|enthusiastic)\b', content, re.IGNORECASE))
        formal_words = len(re.findall(r'\b(?:respectfully|sincerely|regards|yours\s+truly)\b', content, re.IGNORECASE))
        
        if enthusiastic_words > 2:
            return "enthusiastic"
        elif formal_words > 1:
            return "formal"
        else:
            return "professional"
    
    def _extract_connections(self, content: str) -> int:
        """Extract number of connections from LinkedIn content"""
        connection_pattern = r'(\d+)\s*connections?'
        match = re.search(connection_pattern, content, re.IGNORECASE)
        return int(match.group(1)) if match else 0 