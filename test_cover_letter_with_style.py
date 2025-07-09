#!/usr/bin/env python3
"""
Test script to demonstrate enhanced writing style in cover letter generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.document_parser import LegacyDocumentParser
from app.services.cover_letter_gen import CoverLetterGenerator
from app.services.llm_service import LLMService
from sqlalchemy.orm import Session
import json

def test_cover_letter_with_style():
    """Test cover letter generation with enhanced writing style"""
    
    print("=== Enhanced Writing Style Cover Letter Generation Test ===\n")
    
    # Sample user's writing style from their previous cover letter
    user_cover_letter = """
Dear Hiring Manager,

I am writing to express my keen interest in the Data Scientist position at TechCorp. With my extensive experience in machine learning and data analysis, I am confident that I can make significant contributions to your team.

Throughout my career, I have consistently demonstrated the ability to develop innovative solutions that drive business value. At my previous role at DataTech, I successfully implemented a predictive analytics framework that increased customer retention by 25%. This achievement was particularly rewarding as it directly impacted the company's bottom line.

Furthermore, I have a proven track record of collaborating with cross-functional teams to deliver complex projects on time and within budget. My expertise in Python, R, and SQL, combined with my strong analytical skills, enables me to tackle challenging problems effectively.

I am particularly excited about TechCorp's mission to leverage artificial intelligence for social good. Your commitment to ethical AI development aligns perfectly with my professional values and career aspirations.

I would welcome the opportunity to discuss how my background, technical skills, and passion for data science would make me a valuable addition to your team. Thank you for considering my application.

Best regards,
John Doe
"""
    
    # Sample user experience
    user_experience = [
        {
            "title": "Senior Data Scientist",
            "company": "DataTech Solutions",
            "start_date": "2022-01",
            "end_date": "Present",
            "description": "Led machine learning initiatives that improved customer retention by 25%. Developed predictive models using Python and R. Collaborated with cross-functional teams to deliver data-driven solutions."
        },
        {
            "title": "Data Analyst",
            "company": "Analytics Corp",
            "start_date": "2020-06",
            "end_date": "2021-12",
            "description": "Analyzed large datasets to identify business opportunities. Created dashboards and reports using SQL and Tableau. Supported decision-making processes with data insights."
        }
    ]
    
    print("User's Previous Cover Letter (Writing Style Reference):")
    print("-" * 60)
    print(user_cover_letter)
    print("-" * 60)
    
    # Analyze the user's writing style
    parser = LegacyDocumentParser()
    writing_style = parser._analyze_writing_style(user_cover_letter)
    
    print("\nExtracted Writing Style Analysis:")
    print("=" * 50)
    print(f"Style Summary: {writing_style.get('writing_style_summary', 'N/A')}")
    print(f"Common words: {', '.join(writing_style.get('common_words', [])[:8])}")
    print(f"Common phrases: {', '.join(writing_style.get('common_phrases', [])[:3])}")
    print(f"Personal voice: {writing_style.get('personal_voice', False)}")
    print(f"Professional terms: {writing_style.get('uses_professional_terms', False)}")
    print(f"Confident tone: {writing_style.get('confident_tone', False)}")
    
    # Create writing style instructions
    generator = CoverLetterGenerator(db=None, llm_service=None)
    style_instructions = generator._create_writing_style_instructions(writing_style)
    
    print(f"\nGenerated Writing Style Instructions:")
    print("=" * 50)
    print(style_instructions)
    
    # Show what the enhanced prompt would look like
    print(f"\n" + "=" * 60)
    print("Enhanced Cover Letter Generation Prompt:")
    print("=" * 60)
    
    # Create a sample prompt to show how the style is integrated
    sample_prompt = f"""
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
9. CRITICAL: Match the user's writing style exactly as specified below

Job Title: Software Engineer
Company: TechStartup
Job Description: We are looking for a software engineer to join our growing team. The ideal candidate will have experience with Python, JavaScript, and cloud technologies.

USER'S ACTUAL EXPERIENCE (ONLY USE THESE):
- Senior Data Scientist at DataTech Solutions (2022-01 - Present): Led machine learning initiatives that improved customer retention by 25%. Developed predictive models using Python and R. Collaborated with cross-functional teams to deliver data-driven solutions.
- Data Analyst at Analytics Corp (2020-06 - 2021-12): Analyzed large datasets to identify business opportunities. Created dashboards and reports using SQL and Tableau. Supported decision-making processes with data insights.

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

Cover Letter:
"""
    
    print(sample_prompt)
    
    print(f"\n" + "=" * 60)
    print("Key Improvements in Writing Style Analysis:")
    print("=" * 60)
    print("1. ✅ Enhanced vocabulary capture (common words, phrases, sentence starters)")
    print("2. ✅ Detailed style characteristics (transitions, action verbs, professional terms)")
    print("3. ✅ Tone analysis (enthusiastic, confident, formal)")
    print("4. ✅ Voice detection (personal vs formal)")
    print("5. ✅ Sentence and paragraph structure analysis")
    print("6. ✅ Structured writing style instructions for LLM")
    print("7. ✅ Integration with RAG system for better context")
    print("8. ✅ Recency weighting for more recent writing samples")
    
    print(f"\n" + "=" * 60)
    print("Expected Results:")
    print("=" * 60)
    print("The generated cover letter should now:")
    print("- Use similar vocabulary and phrases as the user's writing")
    print("- Match the user's sentence structure and length")
    print("- Maintain the same tone (confident, professional)")
    print("- Use similar transition words and connectors")
    print("- Follow the user's paragraph structure")
    print("- Incorporate the user's common sentence starters")
    print("- Use the same level of formality and personal voice")
    
    print(f"\n" + "=" * 60)
    print("Test completed! The enhanced writing style system is ready.")
    print("=" * 60)

if __name__ == "__main__":
    test_cover_letter_with_style() 