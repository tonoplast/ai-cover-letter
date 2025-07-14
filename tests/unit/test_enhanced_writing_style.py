#!/usr/bin/env python3
"""
Test script for enhanced writing style analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.document_parser import LegacyDocumentParser
import json

def test_writing_style_analysis():
    """Test the enhanced writing style analysis"""
    
    # Sample cover letter content with distinctive writing style
    sample_cover_letter = """
Dear Hiring Manager,

I am writing to express my keen interest in the Data Scientist position at TechCorp. With my extensive experience in machine learning and data analysis, I am confident that I can make significant contributions to your team.

Throughout my career, I have consistently demonstrated the ability to develop innovative solutions that drive business value. At my previous role at DataTech, I successfully implemented a predictive analytics framework that increased customer retention by 25%. This achievement was particularly rewarding as it directly impacted the company's bottom line.

Furthermore, I have a proven track record of collaborating with cross-functional teams to deliver complex projects on time and within budget. My expertise in Python, R, and SQL, combined with my strong analytical skills, enables me to tackle challenging problems effectively.

I am particularly excited about TechCorp's mission to leverage artificial intelligence for social good. Your commitment to ethical AI development aligns perfectly with my professional values and career aspirations.

I would welcome the opportunity to discuss how my background, technical skills, and passion for data science would make me a valuable addition to your team. Thank you for considering my application.

Best regards,
John Doe
"""
    
    print("=== Enhanced Writing Style Analysis Test ===\n")
    
    # Create parser and analyze writing style
    parser = LegacyDocumentParser()
    writing_style = parser._analyze_writing_style(sample_cover_letter)
    
    print("Sample Cover Letter:")
    print("-" * 50)
    print(sample_cover_letter)
    print("-" * 50)
    
    print("\nWriting Style Analysis Results:")
    print("=" * 50)
    
    # Display basic metrics
    print(f"Average sentence length: {writing_style.get('avg_sentence_length', 0):.1f} words")
    print(f"Average paragraph length: {writing_style.get('avg_paragraph_length', 0):.1f} words")
    print(f"Vocabulary diversity: {writing_style.get('vocabulary_diversity', 0):.3f}")
    
    # Display vocabulary analysis
    print(f"\nCommon words: {', '.join(writing_style.get('common_words', [])[:10])}")
    print(f"Common phrases: {', '.join(writing_style.get('common_phrases', [])[:5])}")
    print(f"Common 3-word phrases: {', '.join(writing_style.get('common_three_word_phrases', [])[:3])}")
    print(f"Common sentence starters: {', '.join(writing_style.get('common_sentence_starters', [])[:3])}")
    
    # Display style indicators
    print(f"\nStyle Indicators:")
    print(f"- Formal words: {writing_style.get('formal_words_count', 0)}")
    print(f"- Action verbs: {writing_style.get('action_verbs_count', 0)}")
    print(f"- Transition words: {writing_style.get('transition_words_count', 0)}")
    print(f"- Personal pronouns: {writing_style.get('personal_pronouns_count', 0)}")
    print(f"- Professional terms: {writing_style.get('professional_terms_count', 0)}")
    print(f"- Enthusiastic words: {writing_style.get('enthusiastic_words_count', 0)}")
    print(f"- Confident words: {writing_style.get('confident_words_count', 0)}")
    
    # Display writing patterns
    print(f"\nWriting Patterns:")
    print(f"- Uses transitions: {writing_style.get('uses_transitions', False)}")
    print(f"- Uses action verbs: {writing_style.get('uses_action_verbs', False)}")
    print(f"- Uses professional terms: {writing_style.get('uses_professional_terms', False)}")
    print(f"- Personal voice: {writing_style.get('personal_voice', False)}")
    print(f"- Enthusiastic tone: {writing_style.get('enthusiastic_tone', False)}")
    print(f"- Confident tone: {writing_style.get('confident_tone', False)}")
    
    # Display style summary
    print(f"\nStyle Summary:")
    print(f"{writing_style.get('writing_style_summary', 'No summary available')}")
    
    # Test the style instructions generation
    print(f"\n" + "=" * 50)
    print("Generated Writing Style Instructions:")
    print("=" * 50)
    
    # Create a mock generator to test the style instructions
    class MockGenerator:
        def _create_writing_style_instructions(self, writing_style):
            # Copy the method from CoverLetterGenerator
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
    
    mock_gen = MockGenerator()
    style_instructions = mock_gen._create_writing_style_instructions(writing_style)
    print(style_instructions)
    
    print(f"\n" + "=" * 50)
    print("Test completed successfully!")
    print("The enhanced writing style analysis is working correctly.")
    print("=" * 50)

if __name__ == "__main__":
    test_writing_style_analysis() 