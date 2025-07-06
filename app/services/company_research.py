import os
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

class SearchProvider(Enum):
    DUCKDUCKGO = "duckduckgo"
    GOOGLE = "google"
    TAVILY = "tavily"
    YACY = "yacy"
    SEARXNG = "searxng"
    BRAVE = "brave"
    MANUAL = "manual"

@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    provider: str
    timestamp: datetime

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = []
    
    def can_make_request(self) -> bool:
        now = datetime.now()
        # Remove old requests outside the time window
        self.requests = [req for req in self.requests 
                        if now - req < timedelta(seconds=self.time_window)]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        self.requests.append(datetime.now())

class CompanyResearchService:
    def __init__(self):
        self.providers = {}
        self.rate_limiters = {}
        self.setup_providers()
    
    def setup_providers(self):
        """Setup available search providers with rate limiting"""
        
        # DuckDuckGo (free, but rate limited)
        if DUCKDUCKGO_AVAILABLE:
            self.providers[SearchProvider.DUCKDUCKGO] = self._search_duckduckgo
            self.rate_limiters[SearchProvider.DUCKDUCKGO] = RateLimiter(max_requests=10, time_window=60)  # 10 requests per minute
        
        # Google (requires API key)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if GOOGLE_AVAILABLE and google_api_key:
            self.providers[SearchProvider.GOOGLE] = self._search_google
            self.rate_limiters[SearchProvider.GOOGLE] = RateLimiter(max_requests=100, time_window=60)  # 100 requests per minute
        
        # Tavily (requires API key)
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if tavily_api_key:
            self.providers[SearchProvider.TAVILY] = self._search_tavily
            self.rate_limiters[SearchProvider.TAVILY] = RateLimiter(max_requests=50, time_window=60)  # 50 requests per minute
        
        # YaCy (self-hosted search engine)
        yacy_url = os.getenv('YACY_URL')
        if yacy_url:
            self.providers[SearchProvider.YACY] = self._search_yacy
            self.rate_limiters[SearchProvider.YACY] = RateLimiter(max_requests=30, time_window=60)  # 30 requests per minute
        
        # SearXNG (self-hosted search engine)
        searxng_url = os.getenv('SEARXNG_URL')
        if searxng_url:
            self.providers[SearchProvider.SEARXNG] = self._search_searxng
            self.rate_limiters[SearchProvider.SEARXNG] = RateLimiter(max_requests=30, time_window=60)  # 30 requests per minute
        
        # Brave Search (free, privacy-focused)
        self.providers[SearchProvider.BRAVE] = self._search_brave
        self.rate_limiters[SearchProvider.BRAVE] = RateLimiter(max_requests=20, time_window=60)  # 20 requests per minute
    
    def get_available_providers(self) -> List[str]:
        """Get list of available search providers"""
        return [provider.value for provider in self.providers.keys()]
    
    def search_company(self, company_name: str, provider: Optional[str] = None, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for company info using specified or fallback provider with optional country focus"""
        
        # Determine which provider to use
        available_providers = [p.value for p in self.providers.keys()]
        if provider is not None and provider in available_providers:
            search_provider = SearchProvider(provider)
        else:
            # Use fallback order: Tavily > Google > Brave > DuckDuckGo
            if SearchProvider.TAVILY in self.providers:
                search_provider = SearchProvider.TAVILY
            elif SearchProvider.GOOGLE in self.providers:
                search_provider = SearchProvider.GOOGLE
            elif SearchProvider.BRAVE in self.providers:
                search_provider = SearchProvider.BRAVE
            elif SearchProvider.DUCKDUCKGO in self.providers:
                search_provider = SearchProvider.DUCKDUCKGO
            else:
                return self._manual_company_info(company_name)
        
        # Check rate limiting
        rate_limiter = self.rate_limiters.get(search_provider)
        if rate_limiter and not rate_limiter.can_make_request():
            # Try fallback providers
            for fallback_provider in [SearchProvider.GOOGLE, SearchProvider.BRAVE, SearchProvider.DUCKDUCKGO, SearchProvider.TAVILY]:
                if (fallback_provider in self.providers and 
                    fallback_provider != search_provider and
                    self.rate_limiters[fallback_provider].can_make_request()):
                    search_provider = fallback_provider
                    break
            else:
                return self._manual_company_info(company_name)
        
        try:
            # Record the request
            if rate_limiter:
                rate_limiter.record_request()
            
            # Perform the search
            search_func = self.providers[search_provider]
            result = search_func(company_name, country)
            
            if result:
                result['provider_used'] = search_provider.value
                result['searched_at'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            print(f"Error searching with {search_provider.value}: {str(e)}")
            # Try manual fallback
            return self._manual_company_info(company_name)
    
    def _search_duckduckgo(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using DuckDuckGo with optional country focus"""
        try:
            ddgs = DDGS()
            # Add country to search query if specified
            search_query = f"{company_name} company"
            if country:
                search_query += f" {country}"
            
            results = list(ddgs.text(search_query, max_results=3))
            
            if not results:
                return None
            
            # Find the most relevant result
            for result in results:
                if company_name.lower() in result.get('title', '').lower():
                    return self._extract_company_info(result, company_name)
            
            # Fallback to first result
            return self._extract_company_info(results[0], company_name)
            
        except Exception as e:
            print(f"DuckDuckGo search error: {str(e)}")
            return None
    
    def _search_google(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using Google Custom Search API with optional country focus"""
        try:
            # Use Google's Generative AI for company research
            model = genai.GenerativeModel('gemini-pro')
            
            # Add country context to prompt if specified
            country_context = f" in {country}" if country else ""
            prompt = f"""
            Research the company \"{company_name}\"{country_context} and provide the following information in JSON format:
            {{
                "company_name": "official company name",
                "industry": "primary industry",
                "size": "company size (e.g., 1000-5000 employees)",
                "location": "headquarters location",
                "website": "official website",
                "description": "brief company description",
                "founded": "year founded if known",
                "revenue": "revenue range if known"
            }}
            
            Only return valid JSON, no additional text.
            """
            
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            
            return {
                'company_name': result.get('company_name', company_name),
                'industry': result.get('industry', ''),
                'size': result.get('size', ''),
                'location': result.get('location', ''),
                'website': result.get('website', ''),
                'description': result.get('description', ''),
                'founded': result.get('founded', ''),
                'revenue': result.get('revenue', ''),
                'research_data': result
            }
            
        except Exception as e:
            print(f"Google search error: {str(e)}")
            return None
    
    def _search_tavily(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using Tavily AI with optional country focus"""
        try:
            tavily_api_key = os.getenv('TAVILY_API_KEY')
            if not tavily_api_key:
                print("Tavily API key not found in environment variables")
                return None
            
            # Debug: Check API key format (don't log full key)
            if not tavily_api_key.startswith('tvly-'):
                print("Warning: Tavily API key doesn't start with 'tvly-'")
            
            # Add country to search query if specified
            search_query = f"{company_name} company information"
            if country:
                search_query += f" {country}"
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": tavily_api_key,
                "query": search_query,
                "search_depth": "basic",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 5
            }
            
            print(f"Making Tavily request for: {company_name}")
            response = requests.post(url, json=payload, timeout=10)
            
            # Detailed error handling
            if response.status_code == 401:
                print(f"Tavily API 401 Unauthorized - Check your API key")
                print(f"API Key starts with: {tavily_api_key[:10]}...")
                return None
            elif response.status_code == 403:
                print(f"Tavily API 403 Forbidden - Check your account status and plan limits")
                return None
            elif response.status_code == 429:
                print(f"Tavily API 429 Rate Limited - Too many requests")
                return None
            elif response.status_code != 200:
                print(f"Tavily API error {response.status_code}: {response.text}")
                return None
            
            data = response.json()
            
            # Extract information from Tavily response
            answer = data.get('answer', '')
            results = data.get('results', [])
            
            # Try to extract structured information
            company_info = {
                'company_name': company_name,
                'description': answer[:500] if answer else '',
                'website': '',
                'industry': '',
                'size': '',
                'location': '',
                'research_data': data
            }
            
            # Extract website from results
            for result in results:
                if result.get('url') and company_name.lower() in result.get('title', '').lower():
                    company_info['website'] = result.get('url', '')
                    break
            
            print(f"Tavily search successful for: {company_name}")
            return company_info
            
        except requests.exceptions.RequestException as e:
            print(f"Tavily network error: {str(e)}")
            return None
        except Exception as e:
            print(f"Tavily search error: {str(e)}")
            return None
    
    def _search_yacy(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using YaCy self-hosted search engine with optional country focus"""
        yacy_url = os.getenv('YACY_URL')
        if not yacy_url:
            print("YACY_URL not set in environment")
            return None
        try:
            # Add country to search query if specified
            search_query = f"{company_name} company information"
            if country:
                search_query += f" {country}"
            
            params = {
                "query": search_query,
                "maximumRecords": 5,
                "resource": "global"
            }
            response = requests.get(f"{yacy_url}/yacysearch.json", params=params, timeout=10)
            if response.status_code != 200:
                print(f"YaCy error {response.status_code}: {response.text}")
                return None
            data = response.json()
            items = data.get("channels", [{}])[0].get("items", [])
            if not items:
                return None
            # Use the first result
            result = items[0]
            return {
                "company_name": company_name,
                "website": result.get("link", ""),
                "description": result.get("description", "")[:500],
                "industry": "",
                "size": "",
                "location": "",
                "research_data": result
            }
        except Exception as e:
            print(f"YaCy search error: {str(e)}")
            return None

    def _search_searxng(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using SearXNG self-hosted search engine with optional country focus"""
        searxng_url = os.getenv('SEARXNG_URL')
        if not searxng_url:
            print("SEARXNG_URL not set in environment")
            return None
        try:
            # Add country to search query if specified
            search_query = f"{company_name} company information"
            if country:
                search_query += f" {country}"
            
            params = {
                "q": search_query,
                "format": "json",
                "categories": "general",
                "language": "en"
            }
            response = requests.get(f"{searxng_url}/search", params=params, timeout=10)
            if response.status_code != 200:
                print(f"SearXNG error {response.status_code}: {response.text}")
                return None
            data = response.json()
            results = data.get("results", [])
            if not results:
                return None
            # Use the first result
            result = results[0]
            return {
                "company_name": company_name,
                "website": result.get("url", ""),
                "description": result.get("content", "")[:500],
                "industry": "",
                "size": "",
                "location": "",
                "research_data": result
            }
        except Exception as e:
            print(f"SearXNG search error: {str(e)}")
            return None
    
    def _search_brave(self, company_name: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search using Brave Search API with optional country focus"""
        try:
            # Brave Search API endpoint
            url = "https://api.search.brave.com/res/v1/web/search"
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': os.getenv('BRAVE_API_KEY', '')  # Optional API key
            }
            
            # Add country to search query if specified
            search_query = f"{company_name} company about us mission vision"
            if country:
                search_query += f" {country}"
            
            params = {
                'q': search_query,
                'count': 5,
                'search_lang': 'en',
                'safesearch': 'moderate'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('web', {}).get('results', [])
                
                if not results:
                    return None
                
                # Extract comprehensive company information
                company_info = self._extract_comprehensive_company_info(results, company_name)
                company_info['provider_used'] = 'brave'
                company_info['searched_at'] = datetime.now().isoformat()
                return company_info
            else:
                print(f"Brave Search API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Brave search error: {str(e)}")
            return None
    
    def _extract_comprehensive_company_info(self, results: List[Dict[str, Any]], company_name: str) -> Dict[str, Any]:
        """Extract comprehensive company information from search results"""
        company_info = {
            'company_name': company_name,
            'industry': '',
            'size': '',
            'location': '',
            'website': '',
            'description': '',
            'founded': '',
            'revenue': '',
            'mission': '',
            'vision': '',
            'values': '',
            'recent_news': '',
            'culture': '',
            'achievements': ''
        }
        
        # Combine all search results for analysis
        combined_text = ' '.join([
            result.get('title', '') + ' ' + result.get('description', '')
            for result in results
        ]).lower()
        
        # Extract basic information
        for result in results:
            title = result.get('title', '').lower()
            description = result.get('description', '').lower()
            url = result.get('url', '')
            
            # Look for company website
            if not company_info['website'] and company_name.lower().replace(' ', '') in url:
                company_info['website'] = url
            
            # Look for industry mentions
            industries = ['technology', 'software', 'healthcare', 'finance', 'retail', 'manufacturing', 'consulting', 'education']
            for industry in industries:
                if industry in title or industry in description:
                    company_info['industry'] = industry.title()
                    break
            
            # Look for size indicators
            size_patterns = ['employees', 'staff', 'team', 'workforce']
            for pattern in size_patterns:
                if pattern in description:
                    # Extract size information
                    import re
                    size_match = re.search(r'(\d+(?:,\d+)?(?:\+)?)\s*(?:employees?|staff|team)', description)
                    if size_match:
                        company_info['size'] = f"{size_match.group(1)} employees"
                        break
            
            # Look for location
            location_patterns = ['headquartered in', 'based in', 'located in', 'headquarters']
            for pattern in location_patterns:
                if pattern in description:
                    # Extract location
                    import re
                    location_match = re.search(rf'{pattern}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', description)
                    if location_match:
                        company_info['location'] = location_match.group(1)
                        break
            
            # Look for founding year
            import re
            year_match = re.search(r'founded\s+in\s+(\d{4})', description)
            if year_match:
                company_info['founded'] = year_match.group(1)
            
            # Look for mission/vision statements
            if 'mission' in description or 'vision' in description:
                # Extract mission/vision content
                mission_match = re.search(r'mission[:\s]+([^.]+)', description)
                if mission_match:
                    company_info['mission'] = mission_match.group(1).strip()
                
                vision_match = re.search(r'vision[:\s]+([^.]+)', description)
                if vision_match:
                    company_info['vision'] = vision_match.group(1).strip()
            
            # Look for values
            if 'values' in description or 'principles' in description:
                values_match = re.search(r'values[:\s]+([^.]+)', description)
                if values_match:
                    company_info['values'] = values_match.group(1).strip()
        
        # Create a comprehensive description
        if not company_info['description']:
            # Use the first result's description as base
            if results:
                company_info['description'] = results[0].get('description', '')[:200] + '...'
        
        # Clean up empty fields
        company_info = {k: v for k, v in company_info.items() if v}
        
        return company_info
    
    def _manual_company_info(self, company_name: str) -> Dict[str, Any]:
        """Fallback manual company information"""
        return {
            'company_name': company_name,
            'description': f'Basic information for {company_name}. Please research manually for detailed information.',
            'website': '',
            'industry': 'Unknown',
            'size': 'Unknown',
            'location': 'Unknown',
            'provider_used': 'manual',
            'searched_at': datetime.now().isoformat(),
            'research_data': {'note': 'Manual fallback - no external search performed'}
        }
    
    def _extract_company_info(self, result: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Extract structured company information from search result"""
        info = {
            'company_name': result.get('title', company_name),
            'website': result.get('href', ''),
            'description': result.get('body', '')[:500],  # Limit description length
            'industry': '',
            'size': '',
            'location': '',
            'research_data': result
        }
        
        # Try to extract more info from the description
        description = result.get('body', '').lower()
        
        # Extract industry hints
        industries = ['technology', 'software', 'finance', 'healthcare', 'retail', 'manufacturing', 'consulting']
        for industry in industries:
            if industry in description:
                info['industry'] = industry.title()
                break
        
        # Extract size hints
        size_patterns = [
            r'(\d+)[,\s]*employees',
            r'(\d+)[,\s]*people',
            r'(\d+)[,\s]*staff'
        ]
        
        import re
        for pattern in size_patterns:
            match = re.search(pattern, description)
            if match:
                size = int(match.group(1))
                if size < 100:
                    info['size'] = f'{size} employees'
                elif size < 1000:
                    info['size'] = f'{size} employees'
                elif size < 10000:
                    info['size'] = f'{size} employees'
                else:
                    info['size'] = f'{size}+ employees'
                break
        
        return info 