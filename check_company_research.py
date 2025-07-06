#!/usr/bin/env python3
"""
Check company research data in the database
"""

import os
import sys
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from app.models import CoverLetter, CompanyResearch

def check_company_research():
    """Check company research data in the database"""
    
    db = next(get_db())
    
    try:
        print("=== Company Research Data Check ===")
        
        # Check CompanyResearch table
        company_research = db.query(CompanyResearch).all()
        print(f"Company Research records: {len(company_research)}")
        
        for cr in company_research:
            print(f"\n📊 Company Research ID {cr.id}:")
            print(f"   Company: {cr.company_name}")
            print(f"   Researched: {cr.researched_at}")
            print(f"   Website: {cr.website}")
            print(f"   Industry: {cr.industry}")
            print(f"   Description: {cr.description[:100] if cr.description else 'None'}...")
            print(f"   Research Data Keys: {list(cr.research_data.keys()) if cr.research_data else 'None'}")
            if cr.research_data:
                print(f"   Provider Used: {cr.research_data.get('provider_used', 'Unknown')}")
        
        # Check CoverLetter table
        cover_letters = db.query(CoverLetter).all()
        print(f"\n📝 Cover Letters: {len(cover_letters)}")
        
        for cl in cover_letters:
            print(f"\n📄 Cover Letter ID {cl.id}:")
            print(f"   Job: {cl.job_title}")
            print(f"   Company: {cl.company_name}")
            print(f"   Generated: {cl.generated_at}")
            print(f"   Company Research Data: {cl.company_research}")
            
            if cl.company_research:
                print(f"   Research Data Keys: {list(cl.company_research.keys())}")
                print(f"   Provider Used: {cl.company_research.get('provider_used', 'Unknown')}")
            else:
                print("   ❌ No company research data stored")
        
        # Check for mismatches
        print(f"\n🔍 Checking for data mismatches...")
        
        for cl in cover_letters:
            if cl.company_name:
                # Look for matching company research
                matching_research = db.query(CompanyResearch).filter(
                    CompanyResearch.company_name.ilike(f"%{cl.company_name}%")
                ).first()
                
                if matching_research:
                    print(f"   ✅ Cover Letter {cl.id} ({cl.company_name}) has matching research data")
                else:
                    print(f"   ❌ Cover Letter {cl.id} ({cl.company_name}) has NO matching research data")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_company_research() 