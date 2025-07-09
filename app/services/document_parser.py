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
        """Robust experience extraction: don't fail if group is missing"""
        import re
        # Try to match various section headers
        experience_sections = re.split(r'(?i)\n\s*(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY|CAREER HISTORY|EMPLOYMENT|WORK HISTORY|WORK BACKGROUND|WORK)\s*:?\n', content)
        if len(experience_sections) < 2:
            return []
        # Take the section after the first match
        exp_content = experience_sections[1] if len(experience_sections) > 1 else experience_sections[-1]
        # Split into jobs by double newlines or bullet points
        jobs = re.split(r'\n\s*[-•]\s*|\n\n+', exp_content)
        experiences = []
        for job in jobs:
            job = job.strip()
            if len(job) < 10:
                continue
            # Try to extract title, company, duration, description
            m = re.match(r'(?P<title>.+?) at (?P<company>.+?) \((?P<duration>.+?)\)\s*-\s*(?P<description>.+)', job)
            if m:
                experiences.append(m.groupdict())
            else:
                # Fallback: just use the job text
                experiences.append({"description": job})
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
        """Analyze writing style characteristics with enhanced vocabulary and pattern detection"""
        import re
        from collections import Counter
        
        # Basic text analysis
        sentences = re.split(r'[.!?]+', content)
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Enhanced vocabulary analysis
        word_freq = Counter(words)
        most_common_words = [word for word, count in word_freq.most_common(20) if len(word) > 3]
        
        # Extract common phrases (2-3 word combinations)
        phrases = []
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:
                phrases.append(phrase)
        phrase_freq = Counter(phrases)
        common_phrases = [phrase for phrase, count in phrase_freq.most_common(10)]
        
        # Extract 3-word phrases
        three_word_phrases = []
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 8:
                three_word_phrases.append(phrase)
        three_word_freq = Counter(three_word_phrases)
        common_three_word_phrases = [phrase for phrase, count in three_word_freq.most_common(5)]
        
        # Analyze sentence structures
        sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Detect writing patterns
        formal_words = len(re.findall(r'\b(?:therefore|furthermore|moreover|consequently|subsequently|additionally|further|thus|hence)\b', content, re.IGNORECASE))
        action_verbs = len(re.findall(r'\b(?:developed|implemented|managed|led|created|designed|built|improved|established|coordinated|facilitated|delivered|achieved|increased|reduced|optimized|streamlined|enhanced|strengthened|expanded)\b', content, re.IGNORECASE))
        
        # Detect transition words and connectors
        transition_words = len(re.findall(r'\b(?:however|although|nevertheless|meanwhile|subsequently|furthermore|moreover|additionally|consequently|therefore|thus|hence|accordingly|conversely|similarly|likewise|meanwhile|subsequently|previously|initially|finally|ultimately)\b', content, re.IGNORECASE))
        
        # Detect personal pronouns and voice
        personal_pronouns = len(re.findall(r'\b(?:i|me|my|myself|we|us|our|ourselves)\b', content, re.IGNORECASE))
        
        # Detect professional terminology
        professional_terms = len(re.findall(r'\b(?:strategy|initiative|project|team|leadership|collaboration|innovation|solution|framework|methodology|optimization|implementation|analysis|development|management|coordination|facilitation|delivery|achievement|improvement)\b', content, re.IGNORECASE))
        
        # Analyze paragraph structure (approximate)
        paragraphs = content.split('\n\n')
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs if p.strip()) / len([p for p in paragraphs if p.strip()]) if paragraphs else 0
        
        # Detect writing tone indicators
        enthusiastic_words = len(re.findall(r'\b(?:excited|passionate|thrilled|delighted|enthusiastic|eager|motivated|inspired|committed|dedicated)\b', content, re.IGNORECASE))
        confident_words = len(re.findall(r'\b(?:confident|assured|certain|convinced|positive|successful|proven|demonstrated|established|achieved)\b', content, re.IGNORECASE))
        
        # Extract unique sentence starters
        sentence_starters = []
        for sentence in sentences:
            if sentence.strip():
                words_in_sentence = sentence.strip().split()
                if words_in_sentence:
                    starter = words_in_sentence[0].lower()
                    if len(starter) > 2:
                        sentence_starters.append(starter)
        starter_freq = Counter(sentence_starters)
        common_starters = [starter for starter, count in starter_freq.most_common(5)]
        
        return {
            # Basic metrics
            'avg_sentence_length': avg_sentence_length,
            'avg_paragraph_length': avg_paragraph_length,
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            
            # Vocabulary analysis
            'common_words': most_common_words,
            'common_phrases': common_phrases,
            'common_three_word_phrases': common_three_word_phrases,
            'common_sentence_starters': common_starters,
            
            # Style indicators
            'formal_words_count': formal_words,
            'action_verbs_count': action_verbs,
            'transition_words_count': transition_words,
            'personal_pronouns_count': personal_pronouns,
            'professional_terms_count': professional_terms,
            
            # Tone indicators
            'enthusiastic_words_count': enthusiastic_words,
            'confident_words_count': confident_words,
            
            # Writing patterns
            'uses_transitions': transition_words > 2,
            'uses_action_verbs': action_verbs > 3,
            'uses_professional_terms': professional_terms > 2,
            'personal_voice': personal_pronouns > 5,
            'enthusiastic_tone': enthusiastic_words > 2,
            'confident_tone': confident_words > 2,
            
            # Style summary
            'writing_style_summary': self._generate_style_summary({
                'avg_sentence_length': avg_sentence_length,
                'transition_words': transition_words,
                'action_verbs': action_verbs,
                'personal_pronouns': personal_pronouns,
                'enthusiastic_words': enthusiastic_words,
                'confident_words': confident_words,
                'professional_terms': professional_terms
            })
        }
    
    def _generate_style_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the writing style"""
        style_characteristics = []
        
        if metrics['avg_sentence_length'] > 20:
            style_characteristics.append("uses longer, detailed sentences")
        elif metrics['avg_sentence_length'] < 15:
            style_characteristics.append("uses concise, direct sentences")
        else:
            style_characteristics.append("uses balanced sentence lengths")
            
        if metrics['transition_words'] > 3:
            style_characteristics.append("employs smooth transitions between ideas")
            
        if metrics['action_verbs'] > 5:
            style_characteristics.append("uses strong action verbs")
            
        if metrics['personal_pronouns'] > 8:
            style_characteristics.append("writes in a personal, first-person voice")
        elif metrics['personal_pronouns'] < 3:
            style_characteristics.append("writes in a more formal, third-person style")
            
        if metrics['enthusiastic_words'] > 3:
            style_characteristics.append("conveys enthusiasm and passion")
            
        if metrics['confident_words'] > 3:
            style_characteristics.append("expresses confidence and certainty")
            
        if metrics['professional_terms'] > 4:
            style_characteristics.append("uses professional terminology")
            
        if not style_characteristics:
            style_characteristics.append("maintains a professional tone")
            
        return f"Writing style: {'; '.join(style_characteristics)}"
    
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
        """Parse document using docling, legacy, or fallback to raw text extraction"""
        file_extension = Path(file_path).suffix.lower()
        content = None
        parsed_data = {}
        error_msgs = []
        # Try docling first
        if DOCILING_AVAILABLE:
            try:
                docling_parser = DoclingDocumentParser()
                docling_result = docling_parser.parse_document(file_path, document_type)
                content = docling_result.get("content")
                parsed_data = docling_result.get("parsed_data", {})
            except Exception as e:
                error_msgs.append(f"docling: {e}")
        # If docling fails or content is empty, try legacy
        if not content or len(content.strip()) < 20:
            try:
                legacy_parser = LegacyDocumentParser()
                legacy_result = legacy_parser.parse_document(file_path, document_type)
                content = legacy_result.get("content")
                parsed_data = legacy_result.get("parsed_data", {})
            except Exception as e:
                error_msgs.append(f"legacy: {e}")
        # If both fail, fallback to raw text extraction for PDF
        if (not content or len(content.strip()) < 20) and file_extension == ".pdf":
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
                parsed_data = {"content": content, "parser": "raw_pdf"}
                error_msgs.append("docling and legacy failed, used raw PDF text extraction")
            except Exception as e:
                error_msgs.append(f"raw_pdf: {e}")
        # If still no content, return error
        if not content or len(content.strip()) < 20:
            parsed_data = {"error": ", ".join(error_msgs) or "All parsers failed", "content": ""}
            return {"content": "", "parsed_data": parsed_data, "document_type": document_type, "parser": "none"}
        # Attach error messages if any
        if error_msgs:
            parsed_data["parsing_errors"] = error_msgs
        return {"content": content, "parsed_data": parsed_data, "document_type": document_type, "parser": parsed_data.get("parser", "auto")}

    def parse_document_with_llm(self, file_path: str, document_type: str, llm_provider: Optional[str] = None, llm_model: Optional[str] = None, extract_images: bool = True, logo_recognition: str = "none", vision_llm_provider: str = None, vision_llm_model: str = None) -> Dict[str, Any]:
        """Parse document using LLM-enhanced extraction with optional image extraction"""
        from app.services.llm_service import LLMService
        # Always parse main document text for LLM extraction
        basic_parsed = self.parse_document(file_path, document_type)
        content = basic_parsed["content"]
        # If extract_images is True, use enhanced parser for image text extraction
        if extract_images:
            try:
                from app.services.enhanced_document_parser import EnhancedDocumentParser
                enhanced_parser = EnhancedDocumentParser()
                enhanced_parsed = enhanced_parser.parse_document_with_images(
                    file_path, document_type, extract_images=True, logo_recognition=logo_recognition, vision_llm_provider=vision_llm_provider, vision_llm_model=vision_llm_model
                )
                # Merge image-extracted text into content if present
                image_text = enhanced_parsed["parsed_data"].get("extracted_text", "")
                if image_text:
                    content += f"\n\n--- IMAGE EXTRACTED CONTENT ---\n{image_text}"
                # Merge image analysis into parsed_data
                if "image_analysis" in enhanced_parsed["parsed_data"]:
                    basic_parsed["parsed_data"]["image_analysis"] = enhanced_parsed["parsed_data"]["image_analysis"]
            except ImportError:
                pass
        # If no content extracted, return basic result
        if not content or len(content.strip()) < 50:
            return basic_parsed
        # Create LLM service
        llm_service = LLMService(provider=llm_provider, model=llm_model)
        # Create extraction prompt based on document type
        if document_type.lower() == "cv":
            extraction_prompt = self._create_cv_extraction_prompt(content)
        elif document_type.lower() == "cover_letter":
            extraction_prompt = self._create_cover_letter_extraction_prompt(content)
        elif document_type.lower() == "linkedin":
            extraction_prompt = self._create_linkedin_extraction_prompt(content)
        else:
            return basic_parsed
        try:
            llm_response = llm_service.generate_text(extraction_prompt, max_tokens=2048, temperature=0.1)
            if llm_response:
                enhanced_parsed_data = self._parse_llm_extraction_response(llm_response, document_type)
                basic_parsed["parsed_data"].update(enhanced_parsed_data)
                basic_parsed["parsed_data"]["llm_enhanced"] = True
                basic_parsed["parsed_data"]["llm_provider"] = llm_provider
                basic_parsed["parsed_data"]["llm_model"] = llm_model
            else:
                basic_parsed["parsed_data"]["llm_enhanced"] = False
                basic_parsed["parsed_data"]["llm_error"] = "No response from LLM"
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            basic_parsed["parsed_data"]["llm_enhanced"] = False
            basic_parsed["parsed_data"]["llm_error"] = str(e)
        return basic_parsed

    def _create_cv_extraction_prompt(self, content: str) -> str:
        """Create prompt for CV extraction"""
        return f"""
Please extract structured information from this CV/resume. Return ONLY a JSON object with the following structure:

{{
    "personal_info": {{
        "name": "Full Name",
        "email": "email@example.com", 
        "phone": "phone number",
        "location": "city, state/country",
        "linkedin": "linkedin url if found"
    }},
    "summary": "Professional summary or objective",
    "experiences": [
        {{
            "title": "Job Title",
            "company": "Company Name", 
            "duration": "Start Date - End Date or Present",
            "description": "Detailed job description and achievements"
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University/Institution Name",
            "year": "Graduation Year",
            "gpa": "GPA if mentioned"
        }}
    ],
    "skills": ["skill1", "skill2", "skill3"],
    "certifications": ["cert1", "cert2"],
    "languages": ["language1", "language2"]
}}

CV Content:
{content}

Extract the information and return ONLY the JSON object. Do not include any other text or explanations.
"""

    def _create_cover_letter_extraction_prompt(self, content: str) -> str:
        """Create prompt for cover letter extraction with enhanced writing style analysis"""
        return f"""
Please extract structured information from this cover letter. Return ONLY a JSON object with the following structure:

{{
    "recipient": "Recipient name if mentioned",
    "company": "Company name",
    "position": "Position being applied for",
    "key_points": ["point1", "point2", "point3"],
    "tone": "professional/enthusiastic/formal/conversational",
    "writing_style": {{
        "style_description": "brief description of overall writing style",
        "common_words": ["word1", "word2", "word3", "word4", "word5"],
        "common_phrases": ["phrase1", "phrase2", "phrase3"],
        "sentence_patterns": ["pattern1", "pattern2"],
        "vocabulary_level": "simple/moderate/advanced",
        "voice": "first-person/third-person/mixed",
        "transitions": ["transition1", "transition2"],
        "action_verbs": ["verb1", "verb2", "verb3"],
        "professional_terms": ["term1", "term2", "term3"],
        "enthusiasm_level": "low/moderate/high",
        "confidence_level": "low/moderate/high",
        "formality_level": "casual/professional/very formal"
    }},
    "call_to_action": "any call to action mentioned"
}}

Cover Letter Content:
{content}

Extract the information and return ONLY the JSON object. Do not include any other text or explanations.
"""

    def _create_linkedin_extraction_prompt(self, content: str) -> str:
        """Create prompt for LinkedIn profile extraction"""
        return f"""
Please extract structured information from this LinkedIn profile. Return ONLY a JSON object with the following structure:

{{
    "personal_info": {{
        "name": "Full Name",
        "headline": "Professional headline",
        "location": "Location",
        "connections": "number of connections if mentioned"
    }},
    "summary": "Professional summary",
    "experiences": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Duration",
            "description": "Job description"
        }}
    ],
    "education": [
        {{
            "degree": "Degree",
            "institution": "Institution",
            "year": "Year"
        }}
    ],
    "skills": ["skill1", "skill2", "skill3"]
}}

LinkedIn Profile Content:
{content}

Extract the information and return ONLY the JSON object. Do not include any other text or explanations.
"""

    def _parse_llm_extraction_response(self, response: str, document_type: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                # If no JSON found, return empty dict
                return {}
                
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
            return {}
    
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
        """Robust experience extraction: don't fail if group is missing"""
        import re
        # Try to match various section headers
        experience_sections = re.split(r'(?i)\n\s*(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY|CAREER HISTORY|EMPLOYMENT|WORK HISTORY|WORK BACKGROUND|WORK)\s*:?\n', content)
        if len(experience_sections) < 2:
            return []
        # Take the section after the first match
        exp_content = experience_sections[1] if len(experience_sections) > 1 else experience_sections[-1]
        # Split into jobs by double newlines or bullet points
        jobs = re.split(r'\n\s*[-•]\s*|\n\n+', exp_content)
        experiences = []
        for job in jobs:
            job = job.strip()
            if len(job) < 10:
                continue
            # Try to extract title, company, duration, description
            m = re.match(r'(?P<title>.+?) at (?P<company>.+?) \((?P<duration>.+?)\)\s*-\s*(?P<description>.+)', job)
            if m:
                experiences.append(m.groupdict())
            else:
                # Fallback: just use the job text
                experiences.append({"description": job})
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
        """Analyze writing style characteristics with enhanced vocabulary and pattern detection"""
        import re
        from collections import Counter
        
        # Basic text analysis
        sentences = re.split(r'[.!?]+', content)
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Enhanced vocabulary analysis
        word_freq = Counter(words)
        most_common_words = [word for word, count in word_freq.most_common(20) if len(word) > 3]
        
        # Extract common phrases (2-3 word combinations)
        phrases = []
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 5:
                phrases.append(phrase)
        phrase_freq = Counter(phrases)
        common_phrases = [phrase for phrase, count in phrase_freq.most_common(10)]
        
        # Extract 3-word phrases
        three_word_phrases = []
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(phrase) > 8:
                three_word_phrases.append(phrase)
        three_word_freq = Counter(three_word_phrases)
        common_three_word_phrases = [phrase for phrase, count in three_word_freq.most_common(5)]
        
        # Analyze sentence structures
        sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Detect writing patterns
        formal_words = len(re.findall(r'\b(?:therefore|furthermore|moreover|consequently|subsequently|additionally|further|thus|hence)\b', content, re.IGNORECASE))
        action_verbs = len(re.findall(r'\b(?:developed|implemented|managed|led|created|designed|built|improved|established|coordinated|facilitated|delivered|achieved|increased|reduced|optimized|streamlined|enhanced|strengthened|expanded)\b', content, re.IGNORECASE))
        
        # Detect transition words and connectors
        transition_words = len(re.findall(r'\b(?:however|although|nevertheless|meanwhile|subsequently|furthermore|moreover|additionally|consequently|therefore|thus|hence|accordingly|conversely|similarly|likewise|meanwhile|subsequently|previously|initially|finally|ultimately)\b', content, re.IGNORECASE))
        
        # Detect personal pronouns and voice
        personal_pronouns = len(re.findall(r'\b(?:i|me|my|myself|we|us|our|ourselves)\b', content, re.IGNORECASE))
        
        # Detect professional terminology
        professional_terms = len(re.findall(r'\b(?:strategy|initiative|project|team|leadership|collaboration|innovation|solution|framework|methodology|optimization|implementation|analysis|development|management|coordination|facilitation|delivery|achievement|improvement)\b', content, re.IGNORECASE))
        
        # Analyze paragraph structure (approximate)
        paragraphs = content.split('\n\n')
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs if p.strip()) / len([p for p in paragraphs if p.strip()]) if paragraphs else 0
        
        # Detect writing tone indicators
        enthusiastic_words = len(re.findall(r'\b(?:excited|passionate|thrilled|delighted|enthusiastic|eager|motivated|inspired|committed|dedicated)\b', content, re.IGNORECASE))
        confident_words = len(re.findall(r'\b(?:confident|assured|certain|convinced|positive|successful|proven|demonstrated|established|achieved)\b', content, re.IGNORECASE))
        
        # Extract unique sentence starters
        sentence_starters = []
        for sentence in sentences:
            if sentence.strip():
                words_in_sentence = sentence.strip().split()
                if words_in_sentence:
                    starter = words_in_sentence[0].lower()
                    if len(starter) > 2:
                        sentence_starters.append(starter)
        starter_freq = Counter(sentence_starters)
        common_starters = [starter for starter, count in starter_freq.most_common(5)]
        
        return {
            # Basic metrics
            'avg_sentence_length': avg_sentence_length,
            'avg_paragraph_length': avg_paragraph_length,
            'vocabulary_diversity': len(set(words)) / len(words) if words else 0,
            
            # Vocabulary analysis
            'common_words': most_common_words,
            'common_phrases': common_phrases,
            'common_three_word_phrases': common_three_word_phrases,
            'common_sentence_starters': common_starters,
            
            # Style indicators
            'formal_words_count': formal_words,
            'action_verbs_count': action_verbs,
            'transition_words_count': transition_words,
            'personal_pronouns_count': personal_pronouns,
            'professional_terms_count': professional_terms,
            
            # Tone indicators
            'enthusiastic_words_count': enthusiastic_words,
            'confident_words_count': confident_words,
            
            # Writing patterns
            'uses_transitions': transition_words > 2,
            'uses_action_verbs': action_verbs > 3,
            'uses_professional_terms': professional_terms > 2,
            'personal_voice': personal_pronouns > 5,
            'enthusiastic_tone': enthusiastic_words > 2,
            'confident_tone': confident_words > 2,
            
            # Style summary
            'writing_style_summary': self._generate_style_summary({
                'avg_sentence_length': avg_sentence_length,
                'transition_words': transition_words,
                'action_verbs': action_verbs,
                'personal_pronouns': personal_pronouns,
                'enthusiastic_words': enthusiastic_words,
                'confident_words': confident_words,
                'professional_terms': professional_terms
            })
        }
    
    def _generate_style_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the writing style"""
        style_characteristics = []
        
        if metrics['avg_sentence_length'] > 20:
            style_characteristics.append("uses longer, detailed sentences")
        elif metrics['avg_sentence_length'] < 15:
            style_characteristics.append("uses concise, direct sentences")
        else:
            style_characteristics.append("uses balanced sentence lengths")
            
        if metrics['transition_words'] > 3:
            style_characteristics.append("employs smooth transitions between ideas")
            
        if metrics['action_verbs'] > 5:
            style_characteristics.append("uses strong action verbs")
            
        if metrics['personal_pronouns'] > 8:
            style_characteristics.append("writes in a personal, first-person voice")
        elif metrics['personal_pronouns'] < 3:
            style_characteristics.append("writes in a more formal, third-person style")
            
        if metrics['enthusiastic_words'] > 3:
            style_characteristics.append("conveys enthusiasm and passion")
            
        if metrics['confident_words'] > 3:
            style_characteristics.append("expresses confidence and certainty")
            
        if metrics['professional_terms'] > 4:
            style_characteristics.append("uses professional terminology")
            
        if not style_characteristics:
            style_characteristics.append("maintains a professional tone")
            
        return f"Writing style: {'; '.join(style_characteristics)}"
    
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