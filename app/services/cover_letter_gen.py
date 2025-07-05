from typing import Dict, Any, List
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.models import Experience, CoverLetter, CompanyResearch
from sqlalchemy.orm import Session
from datetime import datetime
import json

class CoverLetterGenerator:
    def __init__(self, db: Session, llm_service: LLMService):
        self.db = db
        self.llm = llm_service
        self.rag_service = RAGService(db)

    def generate_cover_letter(self, job_title: str, company_name: str, job_description: str, company_info: Dict[str, Any], user_experiences: List[Experience], writing_style: Dict[str, Any], tone: str = "professional", include_company_research: bool = True) -> str:
        base_prompt = self._build_prompt(job_title, company_name, job_description, company_info, user_experiences, writing_style, tone, include_company_research)
        
        # Enhance prompt with RAG context
        enhanced_prompt = self.rag_service.enhance_cover_letter_prompt(base_prompt, job_title, job_description, company_name)
        
        generated_content = self.llm.generate_text(enhanced_prompt, max_tokens=700, temperature=0.7)
        
        if not generated_content:
            # Fallback template if LLM fails
            return self._generate_fallback_cover_letter(job_title, company_name, job_description, user_experiences, tone)
        
        return generated_content

    def _build_prompt(self, job_title, company_name, job_description, company_info, user_experiences, writing_style, tone, include_company_research=True):
        # Handle experiences from CV data (dict format) vs Experience objects
        if user_experiences and isinstance(user_experiences[0], dict):
            # CV parsed data format
            exp_text = "\n".join([
                f"- {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')} ({exp.get('start_date', 'Unknown')} - {exp.get('end_date', 'Present')}): {exp.get('description', 'No description available')}" 
                for exp in user_experiences if exp
            ])
        else:
            # Experience objects format
            exp_text = "\n".join([
                f"- {exp.title} at {exp.company} ({exp.start_date.strftime('%Y-%m')} - {exp.end_date.strftime('%Y-%m') if exp.end_date else 'Present'}): {exp.description}" 
                for exp in user_experiences
            ])
        
        style_text = f"Writing style: {json.dumps(writing_style)}" if writing_style else ""
        
        # Conditionally include company research information
        company_text = ""
        if include_company_research and company_info:
            # Extract relevant company information for the cover letter
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
1. ONLY use the exact experiences and information provided below
2. DO NOT fabricate, invent, or add any experiences not listed
3. DO NOT mention specific companies, projects, or achievements unless they are in the provided experience
4. If no relevant experience is provided, focus on transferable skills and enthusiasm
5. Be honest and authentic - do not exaggerate or lie
6. Use specific details from the user's experience to make the letter personal and relevant
7. If company research is provided, reference it naturally to show interest in the company, but DO NOT make up information
8. Only mention company research if it's actually provided and relevant

Job Title: {job_title}
Company: {company_name}
Job Description: {job_description}
{company_text}

USER'S ACTUAL EXPERIENCE (ONLY USE THESE):
{exp_text if exp_text else "No specific work experience provided."}

{style_text}

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

Cover Letter:
"""
        return prompt
    
    def _generate_fallback_cover_letter(self, job_title: str, company_name: str, job_description: str, user_experiences: List, tone: str) -> str:
        """Generate a basic cover letter template when LLM is not available"""
        if not user_experiences:
            return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 

I am excited about the opportunity to contribute to your team and believe my background would be a great fit for this role.

Thank you for considering my application.

Best regards,
[Your Name]
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
[Your Name]
"""
        else:
            return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. 

I am excited about the opportunity to contribute to your team and believe my background would be a great fit for this role.

Thank you for considering my application.

Best regards,
[Your Name]
""" 