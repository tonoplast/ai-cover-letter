from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.models import Experience, CoverLetter, CompanyResearch, Document
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re
import logging

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm = llm_service
        self.rag_service = RAGService(db)

    def generate_cover_letter(self, job_title: str, company_name: str, job_description: str, company_info: Dict[str, Any], user_experiences: List[Experience], writing_style: Dict[str, Any], tone: str = "professional", include_company_research: bool = True, strict_relevance: bool = True) -> str:
        """Generate a cover letter with improved accuracy and consistency."""
        try:
            # Validate inputs
            if not job_title or not company_name:
                raise ValueError("Job title and company name are required")
            
            # Get user information and experiences
            user_info = self._extract_user_info()
            experiences_text = self._format_experiences(user_info['experiences'])
            
            # Build the consolidated prompt
            prompt = self._build_consolidated_prompt(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                company_info=company_info,
                user_name=user_info['name'],
                experiences_text=experiences_text,
                writing_style=writing_style,
                tone=tone,
                include_company_research=include_company_research
            )
            
            # Enhance with RAG context
            enhanced_prompt = self.rag_service.enhance_cover_letter_prompt(prompt, job_title, job_description, company_name)
            
            # Generate content
            generated_content = self.llm.generate_text(enhanced_prompt, max_tokens=800, temperature=0.7)
            
            if not generated_content:
                return self._generate_fallback_cover_letter(job_title, company_name, job_description, user_experiences, tone, user_info['name'])
            
            # Post-process and validate
            processed_content = self._post_process_content(generated_content, user_info['name'], company_name, job_title)
            
            # Validate output quality
            if not self._validate_cover_letter_quality(processed_content, company_name, job_title):
                logger.warning("Generated cover letter failed quality validation")
                return self._generate_fallback_cover_letter(job_title, company_name, job_description, user_experiences, tone, user_info['name'])
            
            return processed_content
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return self._generate_fallback_cover_letter(job_title, company_name, job_description, user_experiences, tone, "[Your Name]")
    def _extract_user_info(self) -> Dict[str, Any]:
        """Extract user information from the most recent CV and other documents."""
        try:
            # Get all CVs, most recent first
            cv_docs = self.db.query(Document).filter_by(document_type="cv").order_by(Document.uploaded_at.desc()).all()
            most_recent_cv = cv_docs[0] if cv_docs else None
            
            user_name = "[Your Name]"
            current_exp = None
            previous_exps = []
            additional_exps = []
            
            if most_recent_cv:
                parsed = most_recent_cv.parsed_data if isinstance(most_recent_cv.parsed_data, dict) else {}
                user_name = parsed.get("personal_info", {}).get("name", user_name)
                
                # Format name properly
                if user_name and user_name != "[Your Name]":
                    if user_name.isupper():
                        user_name = user_name.title()
                    elif user_name.islower():
                        user_name = user_name.title()
                
                # Extract experiences from most recent CV
                experiences = parsed.get("experiences", [])
                for exp in experiences:
                    duration = exp.get('duration', '').lower()
                    if current_exp is None and ('present' in duration or duration.endswith('-')):
                        current_exp = exp
                    else:
                        previous_exps.append(exp)
            
            # Use other CVs and cover letters for additional experience/context
            for doc in cv_docs[1:]:
                parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
                additional_exps.extend(parsed.get("experiences", []))
            
            # Add from cover letters (documents table, not generated)
            cover_letter_docs = self.db.query(Document).filter_by(document_type="cover_letter").all()
            for doc in cover_letter_docs:
                parsed = doc.parsed_data if isinstance(doc.parsed_data, dict) else {}
                additional_exps.extend(parsed.get("experiences", []))
            
            return {
                'name': user_name,
                'experiences': {
                    'current': current_exp,
                    'previous': previous_exps,
                    'additional': additional_exps
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting user info: {str(e)}")
            return {
                'name': "[Your Name]",
                'experiences': {
                    'current': None,
                    'previous': [],
                    'additional': []
                }
            }
    
    def _format_experiences(self, experiences: Dict[str, Any]) -> str:
        """Format experiences for the prompt."""
        exp_text = ""
        
        if experiences['current']:
            exp_text += "CURRENT POSITION (from most recent CV):\n"
            exp = experiences['current']
            exp_text += f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('duration', 'Unknown')}): {exp.get('description', 'No description available')}\n\n"
        
        if experiences['previous']:
            exp_text += "PREVIOUS POSITIONS (from most recent CV):\n"
            for exp in experiences['previous']:
                exp_text += f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('duration', 'Unknown')}): {exp.get('description', 'No description available')}\n"
            exp_text += "\n"
        
        if experiences['additional']:
            exp_text += "ADDITIONAL EXPERIENCE (from other CVs and cover letters):\n"
            for exp in experiences['additional']:
                exp_text += f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('duration', 'Unknown')}): {exp.get('description', 'No description available')}\n"
        
        return exp_text if exp_text else "No specific work experience provided."
    def _build_consolidated_prompt(self, job_title: str, company_name: str, job_description: str, company_info: Dict[str, Any], user_name: str, experiences_text: str, writing_style: Dict[str, Any], tone: str, include_company_research: bool) -> str:
        """Build a consolidated, improved prompt for cover letter generation."""
        
        # Format company research information
        company_text = ""
        if include_company_research and company_info:
            company_details = []
            if company_info.get('mission'):
                company_details.append(f"Mission: {company_info['mission']}")
            if company_info.get('vision'):
                company_details.append(f"Vision: {company_info['vision']}")
            if company_info.get('values'):
                company_details.append(f"Values: {company_info['values']}")
            if company_info.get('industry'):
                company_details.append(f"Industry: {company_info['industry']}")
            if company_info.get('description'):
                company_details.append(f"Description: {company_info['description']}")
            if company_details:
                company_text = f"\nCOMPANY RESEARCH:\n" + "\n".join(company_details) + "\n"
        
        # Format writing style instructions
        style_instructions = self._create_writing_style_instructions(writing_style)
        
        # Build the consolidated prompt
        prompt = f"""
You are an expert career assistant. Write a professional cover letter for the following job application.

TARGET ROLE & COMPANY:
- Job Title: {job_title}
- Company: {company_name}

JOB DESCRIPTION:
{job_description}
{company_text}

APPLICANT NAME: {user_name}

APPLICANT'S EXPERIENCE:
{experiences_text}

{style_instructions}

CRITICAL REQUIREMENTS:
1. Write this letter as an application for the {job_title} position at {company_name} ONLY
2. Reference {company_name} and the {job_title} position in the opening and closing paragraphs
3. Systematically address job requirements, matching experience to each where possible
4. Use ONLY the provided experience information - do not fabricate or exaggerate
5. Use present tense for current position, past tense for previous roles
6. Write in flowing, narrative style - NO bullet points or lists
7. Include proper signature formatting with two blank lines before the name
8. Use Australian English spelling and conventions
9. Ensure the letter is complete and professional
10. Sign off with the applicant's name: {user_name}

TONE: {tone.title()}

Output ONLY the final cover letter with no preambles or explanations.
"""
        return prompt
    
    def _post_process_content(self, content: str, user_name: str, company_name: str, job_title: str) -> str:
        """Post-process the generated content to ensure quality and consistency."""
        if not content:
            return content
        
        # Remove thinking tags and other unwanted content
        content = re.sub(r'<think>[\s\S]*?</think>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<thinking>[\s\S]*?</thinking>', '', content, flags=re.IGNORECASE)
        
        # Remove bullet points and lists
        content = re.sub(r'^[\s]*[-*•][\s]+.*$', '', content, flags=re.MULTILINE)
        
        # Remove incomplete lines ending with ellipses
        content = re.sub(r'^.*\.\.\.[\s]*$', '', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Ensure proper signature formatting
        content = self._fix_signature_formatting(content, user_name)
        
        # Validate company and job title references
        content = self._ensure_proper_references(content, company_name, job_title)
        
        return content.strip()
    
    def _fix_signature_formatting(self, content: str, user_name: str) -> str:
        """Fix signature formatting to ensure proper spacing and name inclusion."""
        # Common sign-offs
        signoff_patterns = [
            r'(Sincerely,|Best regards,|Kind regards,|Yours sincerely,|Yours faithfully,|Regards,)'
        ]
        
        for pattern in signoff_patterns:
            # Find sign-off and ensure proper formatting
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                signoff = match.group(1)
                
                # Replace with proper formatting
                replacement = f"{signoff}\n\n\n{user_name}"
                content = re.sub(
                    pattern + r'[\s\S]*?$',
                    replacement,
                    content,
                    flags=re.IGNORECASE
                )
                return content
        
        # If no sign-off found, add one
        if user_name not in content[-100:]:
            content = content.rstrip() + f"\n\nSincerely,\n\n\n{user_name}"
        
        return content
    
    def _ensure_proper_references(self, content: str, company_name: str, job_title: str) -> str:
        """Ensure the cover letter properly references the target company and job."""
        # Check if company name is mentioned in the first paragraph
        paragraphs = content.split('\n\n')
        if paragraphs and company_name.lower() not in paragraphs[0].lower():
            # Try to add company reference if missing
            logger.warning(f"Company name '{company_name}' not found in opening paragraph")
        
        # Check if job title is mentioned
        if job_title.lower() not in content.lower():
            logger.warning(f"Job title '{job_title}' not found in cover letter")
        
        return content
    
    def _validate_cover_letter_quality(self, content: str, company_name: str, job_title: str) -> bool:
        """Validate the quality of the generated cover letter."""
        if not content or len(content) < 200:
            return False
        
        # Check for required elements
        checks = [
            # Must contain company name
            company_name.lower() in content.lower(),
            # Must contain job title or similar
            job_title.lower() in content.lower() or 'position' in content.lower() or 'role' in content.lower(),
            # Must have proper greeting
            any(greeting in content.lower() for greeting in ['dear', 'hello', 'greetings']),
            # Must have proper closing
            any(closing in content.lower() for closing in ['sincerely', 'regards', 'best']),
            # Must not contain placeholder text
            '[your name]' not in content.lower(),
            # Must not contain bullet points
            not re.search(r'^[\s]*[-*•][\s]+', content, re.MULTILINE),
            # Must not be too generic
            len(set(content.lower().split())) > 50  # At least 50 unique words
        ]
        
        return sum(checks) >= 6  # At least 6 out of 8 checks must pass

    # Removed old _build_prompt method - replaced by _build_consolidated_prompt
    
    def _build_prompt_legacy(self, job_title, company_name, job_description, company_info, user_experiences, writing_style, tone, include_company_research=True):
        # Enhanced experience formatting: separate current and previous roles
        current_exp = None
        previous_exps = []
        # Parse experiences for 'Present' or missing end date
        for exp in user_experiences:
            duration = exp.get('duration', '').lower() if isinstance(exp, dict) else ''
            if current_exp is None and ('present' in duration or duration.endswith('-')):
                current_exp = exp
            else:
                previous_exps.append(exp)
        # If none marked as current, treat all as previous
        if not current_exp and user_experiences:
            previous_exps = user_experiences
        # Format experience text
        exp_text = ""
        if current_exp:
            exp_text += "CURRENT POSITION:\n"
            exp_text += f"- {current_exp.get('title', 'Unknown')} at {current_exp.get('company', 'Unknown')} ({current_exp.get('duration', 'Unknown')}): {current_exp.get('description', 'No description available')}\n"
        if previous_exps:
            exp_text += "PREVIOUS POSITIONS:\n"
            for exp in previous_exps:
                exp_text += f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('duration', 'Unknown')}): {exp.get('description', 'No description available')}\n"
        # Enhanced writing style instructions
        style_instructions = self._create_writing_style_instructions(writing_style)
        # Conditionally include company research information
        company_text = ""
        if include_company_research and company_info:
            company_details = []
            if company_info.get('mission'):
                company_details.append(f"Mission: {company_info['mission']}")
            if company_info.get('vision'):
                company_details.append(f"Vision: {company_info['vision']}")
            if company_info.get('values'):
                company_details.append(f"Values: {company_info['values']}")
            if company_info.get('industry'):
                company_details.append(f"Industry: {company_info['industry']}")
            if company_info.get('description'):
                company_details.append(f"Description: {company_info['description']}")
            if company_details:
                company_text = f"Company Research:\n" + "\n".join(company_details) + "\n\n"
        prompt = f"""
You are an expert career assistant. Write a cover letter for the following job application.

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. Carefully analyse the job description and requirements below. For each key requirement or responsibility, check if the user has matching or related experience in their CV or cover letters. If so, highlight it with specific examples. If not, focus on transferable skills or willingness to learn, but NEVER invent or exaggerate experience.
2. Prioritise addressing the specific requirements and responsibilities listed in the job description. For each, use concrete examples from the user's experience if available.
3. ONLY use the exact experiences and information provided below
4. DO NOT fabricate, invent, or add any experiences not listed
5. DO NOT mention specific companies, projects, or achievements unless they are in the provided experience
6. If no relevant experience is provided, focus on transferable skills and enthusiasm
7. Be honest and authentic - do not exaggerate or lie
8. Use specific details from the user's experience to make the letter personal and relevant
9. If company research is provided, reference it naturally to show interest in the company, but DO NOT make up information
10. Only mention company research if it's actually provided and relevant
11. CRITICAL: Match the user's writing style exactly as specified below
12. CRITICAL: Use present tense for the current position, and past tense for all previous roles
13. CRITICAL: Write in a narrative, flowing style - do not just list experiences
14. CRITICAL: Output ONLY the final cover letter. DO NOT include any explanations, preambles, or meta statements. DO NOT say things like 'Here's your cover letter' or 'Below is the cover letter'.
15. CRITICAL: Use Australian English spelling and conventions throughout the letter (not American English).
16. CRITICAL: Ensure the letter is complete and does not stop mid-sentence or mid-thought.
17. CRITICAL: Maintain a professional, natural, and non-generic tone. Avoid generic AI-sounding language.

Job Title: {job_title}
Company: {company_name}
Job Description: {job_description}
{company_text}

USER'S ACTUAL EXPERIENCE (ONLY USE THESE):
{exp_text if exp_text else "No specific work experience provided."}

{style_instructions}

Instructions:
- Write a professional cover letter using ONLY the information above
- Systematically address the job requirements and responsibilities, matching the user's experience to each where possible
- Use specific details from the user's experience (job titles, companies, dates, skills)
- Make connections between the user's background and the job requirements
- Be specific about relevant skills and experiences
- Match your tone to the job requirements
- Be concise (max 1 page)
- Focus on relevant skills and enthusiasm
- Do not invent or fabricate any information
- Make the letter personal by referencing actual experience details
- If company research is provided, naturally incorporate it to show interest in the company's mission, values, or industry
- If no company research is available, focus on the job requirements and your experience
- MOST IMPORTANT: Follow the writing style instructions exactly to match the user's personal writing style
- CRITICAL: Use present tense for the current position, and past tense for all previous roles
- CRITICAL: Write in a flowing, narrative style that tells a story - avoid bullet-point style lists
- CRITICAL: Connect experiences logically and show progression in your career
- CRITICAL: Output ONLY the final cover letter, with no explanations, preambles, or meta statements. Use Australian English spelling and conventions. Ensure the letter is complete and professional.

Cover Letter:
"""
        return prompt
    
    def _create_writing_style_instructions(self, writing_style: Dict[str, Any]) -> str:
        """Create detailed writing style instructions from the analyzed writing style"""
        if not writing_style:
            return ""
        
        instructions = []
        
        # Add style summary if available
        if writing_style.get('writing_style_summary'):
            instructions.append(f"WRITING STYLE OVERVIEW: {writing_style['writing_style_summary']}")
        
        # Vocabulary instructions
        if writing_style.get('common_words'):
            common_words = writing_style['common_words'][:10]  # Top 10 words
            instructions.append(f"FREQUENTLY USED WORDS: Incorporate these words naturally: {', '.join(common_words)}")
        
        if writing_style.get('common_phrases'):
            common_phrases = writing_style['common_phrases'][:5]  # Top 5 phrases
            instructions.append(f"COMMON PHRASES: Use these phrase patterns: {', '.join(common_phrases)}")
        
        if writing_style.get('common_sentence_starters'):
            starters = writing_style['common_sentence_starters'][:3]  # Top 3 starters
            instructions.append(f"SENTENCE STARTERS: Begin sentences with: {', '.join(starters)}")
        
        # Style characteristics
        if writing_style.get('uses_transitions', False):
            instructions.append("TRANSITIONS: Use smooth transitions between ideas (however, furthermore, moreover, etc.)")
        
        if writing_style.get('uses_action_verbs', False):
            instructions.append("ACTION VERBS: Use strong action verbs (developed, implemented, managed, led, created, etc.)")
        
        if writing_style.get('uses_professional_terms', False):
            instructions.append("PROFESSIONAL TERMINOLOGY: Include professional terms (strategy, initiative, collaboration, etc.)")
        
        if writing_style.get('personal_voice', False):
            instructions.append("VOICE: Write in a personal, first-person voice using 'I' statements")
        else:
            instructions.append("VOICE: Write in a more formal, professional tone")
        
        if writing_style.get('enthusiastic_tone', False):
            instructions.append("TONE: Convey enthusiasm and passion for the opportunity")
        
        if writing_style.get('confident_tone', False):
            instructions.append("TONE: Express confidence and certainty in your abilities")
        
        # Sentence structure
        avg_length = writing_style.get('avg_sentence_length', 0)
        if avg_length > 20:
            instructions.append("SENTENCE STRUCTURE: Use longer, detailed sentences with multiple clauses")
        elif avg_length < 15:
            instructions.append("SENTENCE STRUCTURE: Use concise, direct sentences")
        else:
            instructions.append("SENTENCE STRUCTURE: Use balanced sentence lengths")
        
        # Paragraph structure
        avg_para_length = writing_style.get('avg_paragraph_length', 0)
        if avg_para_length > 50:
            instructions.append("PARAGRAPH STRUCTURE: Use longer paragraphs with detailed explanations")
        elif avg_para_length < 30:
            instructions.append("PARAGRAPH STRUCTURE: Use shorter, focused paragraphs")
        
        if not instructions:
            return "WRITING STYLE: Maintain a professional, clear writing style"
        
        return "WRITING STYLE INSTRUCTIONS:\n" + "\n".join([f"- {instruction}" for instruction in instructions])
    
    def _generate_fallback_cover_letter(self, job_title: str, company_name: str, job_description: str, user_experiences: List, tone: str, user_name: str = "[Your Name]") -> str:
        """Generate a basic cover letter template when LLM is not available"""
        if not user_experiences:
            return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 

I am excited about the opportunity to contribute to your team and believe my background would be a great fit for this role.

Thank you for considering my application.

Best regards,
{user_name}
"""
        
        # Get most recent experience
        latest_exp = user_experiences[0] if user_experiences else None
        
        if latest_exp:
            # Handle both dict and object formats
            if isinstance(latest_exp, dict):
                # CV parsed data format
                title = latest_exp.get('title', 'Unknown Position')
                company = latest_exp.get('company', 'Previous Company')
                description = latest_exp.get('description', 'No description available')
            else:
                # Experience object format
                title = latest_exp.title
                company = latest_exp.company
                description = latest_exp.description
            
            return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 

With my experience as {title} at {company}, I believe I have the skills and background necessary to excel in this role. My experience includes {description[:200]}...

I am excited about the opportunity to contribute to {company_name} and would welcome the chance to discuss how my background, skills, and enthusiasm would make me a valuable addition to your team.

Thank you for considering my application. I look forward to the opportunity to speak with you about this position.

Best regards,
{user_name}
"""
        else:
            return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 

I am excited about the opportunity to contribute to your team and believe my background would be a great fit for this role.

Thank you for considering my application.

Best regards,
{user_name}
"""

    # Removed old _build_general_prompt method - replaced by _build_consolidated_prompt
    
    def _build_general_prompt_legacy(self, job_title, company_name, job_description, company_info, user_experiences, writing_style, tone, include_company_research=True):
        # Same as _build_prompt but omits strict job requirement matching rules
        if user_experiences and isinstance(user_experiences[0], dict):
            exp_text = "\n".join([
                f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('start_date', 'Unknown')} - {exp.get('end_date', 'Present')}): {exp.get('description', 'No description available')}" 
                for exp in user_experiences if exp
            ])
        else:
            exp_text = "\n".join([
                f"- {exp.title} at {exp.company} ({exp.start_date.strftime('%Y-%m')} - {exp.end_date.strftime('%Y-%m') if exp.end_date else 'Present'}): {exp.description}" 
                for exp in user_experiences
            ])
        style_instructions = self._create_writing_style_instructions(writing_style)
        company_text = ""
        if include_company_research and company_info:
            company_details = []
            if company_info.get('mission'):
                company_details.append(f"Mission: {company_info['mission']}")
            if company_info.get('vision'):
                company_details.append(f"Vision: {company_info['vision']}")
            if company_info.get('values'):
                company_details.append(f"Values: {company_info['values']}")
            if company_info.get('industry'):
                company_details.append(f"Industry: {company_info['industry']}")
            if company_info.get('description'):
                company_details.append(f"Description: {company_info['description']}")
            if company_details:
                company_text = f"Company Research:\n" + "\n".join(company_details) + "\n\n"
        prompt = f"""
You are an expert career assistant. Write a cover letter for the following job application.

RULES:
- ONLY use the exact experiences and information provided below
- DO NOT fabricate, invent, or add any experiences not listed
- Be honest and authentic - do not exaggerate or lie
- Use specific details from the user's experience to make the letter personal and relevant
- If company research is provided, reference it naturally to show interest in the company, but DO NOT make up information
- Only mention company research if it's actually provided and relevant
- Match the user's writing style exactly as specified below
- Use PAST TENSE for completed experiences and PRESENT TENSE only for current positions
- Write in a narrative, flowing style - do not just list experiences
- Output ONLY the final cover letter. DO NOT include any explanations, preambles, or meta statements. DO NOT say things like 'Here's your cover letter' or 'Below is the cover letter'.
- Use Australian English spelling and conventions throughout the letter (not American English).
- Ensure the letter is complete and does not stop mid-sentence or mid-thought.
- Maintain a professional, natural, and non-generic tone. Avoid generic AI-sounding language.

Job Title: {job_title}
Company: {company_name}
Job Description: {job_description}
{company_text}

USER'S ACTUAL EXPERIENCE (ONLY USE THESE):
{exp_text if exp_text else "No specific work experience provided."}

{style_instructions}

Instructions:
- Write a professional cover letter using ONLY the information above
- Use specific details from the user's experience (job titles, companies, dates, skills)
- Make connections between the user's background and the job requirements
- Be specific about relevant skills and experiences
- Match your tone to the job requirements
- Be concise (max 1 page)
- Focus on relevant skills and enthusiasm
- Do not invent or fabricate any information
- Make the letter personal by referencing actual experience details
- If company research is provided, naturally incorporate it to show interest in the company's mission, values, or industry
- If no company research is available, focus on the job requirements and your experience
- MOST IMPORTANT: Follow the writing style instructions exactly to match the user's personal writing style
- Use PAST TENSE for completed work experiences and PRESENT TENSE only for current positions
- Write in a flowing, narrative style that tells a story - avoid bullet-point style lists
- Connect experiences logically and show progression in your career
- Output ONLY the final cover letter, with no explanations, preambles, or meta statements. Use Australian English spelling and conventions. Ensure the letter is complete and professional.

Cover Letter:
"""
        return prompt 