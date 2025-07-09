import os
import requests
import json
import logging
import time
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from enum import Enum
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException
from app.exceptions import (
    LLMServiceError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    ConfigurationError
)

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class LLMService:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, use_australian_english: bool = True):
        self.provider = provider
        self.model = model
        self.use_australian_english = use_australian_english
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        try:
            load_dotenv(override=True)  # Reload .env file
            
            # Determine provider and model
            if self.provider:
                try:
                    self.current_provider = LLMProvider(self.provider)
                except ValueError:
                    raise ConfigurationError(f"Invalid LLM provider: {self.provider}")
            else:
                # Default provider from env or fallback to Ollama
                provider_str = os.getenv("LLM_PROVIDER", "ollama").lower()
                try:
                    self.current_provider = LLMProvider(provider_str)
                except ValueError:
                    logger.warning(f"Invalid provider '{provider_str}' in config, falling back to Ollama")
                    self.current_provider = LLMProvider.OLLAMA
            
            if self.model:
                self.current_model = self.model
            else:
                # Get model for current provider
                self.current_model = self._get_default_model()
            
            # Load provider-specific configuration
            self._load_provider_config()
            
            logger.info(f"LLM Service configured with: {self.current_provider.value}, model: {self.current_model}")
            
        except Exception as e:
            logger.error(f"Error loading LLM configuration: {str(e)}")
            raise ConfigurationError(f"Failed to load LLM configuration: {str(e)}")
    
    def _get_default_model(self) -> str:
        """Get default model for current provider"""
        if self.current_provider == LLMProvider.OLLAMA:
            return os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        elif self.current_provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-4")
        elif self.current_provider == LLMProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        elif self.current_provider == LLMProvider.GOOGLE:
            return os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        return "llama3.2:latest"  # Fallback
    
    def _load_provider_config(self):
        """Load provider-specific configuration"""
        try:
            if self.current_provider == LLMProvider.OLLAMA:
                self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                self.api_key = None
                # Ollama can take longer for local models
                timeout_str = os.getenv("OLLAMA_TIMEOUT", "120")
                try:
                    self.timeout = int(timeout_str)
                except ValueError:
                    logger.warning(f"Invalid OLLAMA_TIMEOUT value: {timeout_str}, using default 120")
                    self.timeout = 120
                    
            elif self.current_provider == LLMProvider.OPENAI:
                self.base_url = "https://api.openai.com/v1"
                self.api_key = os.getenv("OPENAI_API_KEY")
                if not self.api_key:
                    logger.warning("OPENAI_API_KEY not found in environment")
                timeout_str = os.getenv("OPENAI_TIMEOUT", "60")
                try:
                    self.timeout = int(timeout_str)
                except ValueError:
                    logger.warning(f"Invalid OPENAI_TIMEOUT value: {timeout_str}, using default 60")
                    self.timeout = 60
                    
            elif self.current_provider == LLMProvider.ANTHROPIC:
                self.base_url = "https://api.anthropic.com/v1"
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
                if not self.api_key:
                    logger.warning("ANTHROPIC_API_KEY not found in environment")
                timeout_str = os.getenv("ANTHROPIC_TIMEOUT", "90")
                try:
                    self.timeout = int(timeout_str)
                except ValueError:
                    logger.warning(f"Invalid ANTHROPIC_TIMEOUT value: {timeout_str}, using default 90")
                    self.timeout = 90
                    
            elif self.current_provider == LLMProvider.GOOGLE:
                self.base_url = "https://generativelanguage.googleapis.com/v1beta"
                self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
                if not self.api_key:
                    logger.warning("GOOGLE_GEMINI_API_KEY not found in environment")
                timeout_str = os.getenv("GOOGLE_TIMEOUT", "60")
                try:
                    self.timeout = int(timeout_str)
                except ValueError:
                    logger.warning(f"Invalid GOOGLE_TIMEOUT value: {timeout_str}, using default 60")
                    self.timeout = 60
            
            # Check if Australian English should be used globally
            use_australian_env = os.getenv("USE_AUSTRALIAN_ENGLISH", "true").lower()
            if use_australian_env in ("false", "0", "no", "off"):
                self.use_australian_english = False
            elif not hasattr(self, 'use_australian_english'):
                self.use_australian_english = True
                    
        except Exception as e:
            logger.error(f"Error loading provider config: {str(e)}")
            raise ConfigurationError(f"Failed to load provider configuration: {str(e)}")
    
    def refresh_config(self):
        """Refresh configuration from environment variables"""
        self._load_config()

    def _add_australian_english_instructions(self, prompt: str) -> str:
        """Add Australian English instructions to the prompt"""
        australian_instructions = """IMPORTANT: Use Australian English throughout your response. This includes:
- Australian spelling (e.g., "colour" not "color", "centre" not "center", "realise" not "realize")
- Australian terminology (e.g., "mobile" not "cell phone", "lift" not "elevator")
- Australian expressions and phrases where appropriate
- Australian business language conventions
- Use "organisation" not "organization"
- Use "analyse" not "analyze"
- Use "favour" not "favor"
- Use "honour" not "honor"
- Use "licence" (noun) and "license" (verb)
- Use "practise" (verb) and "practice" (noun)

"""
        return australian_instructions + prompt

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7, retry_count: int = 3) -> Optional[str]:
        """Generate text using the configured LLM provider with retry logic"""
        if not prompt or not prompt.strip():
            raise LLMServiceError("Prompt cannot be empty")
            
        if max_tokens <= 0 or max_tokens > 4096:
            raise LLMServiceError("max_tokens must be between 1 and 4096")
            
        if temperature < 0 or temperature > 2:
            raise LLMServiceError("temperature must be between 0 and 2")
        
        # Add Australian English instructions to all prompts (if enabled)
        if self.use_australian_english:
            australian_english_prompt = self._add_australian_english_instructions(prompt)
        else:
            australian_english_prompt = prompt
        
        for attempt in range(retry_count):
            try:
                if self.current_provider == LLMProvider.OLLAMA:
                    return self._generate_ollama(australian_english_prompt, max_tokens, temperature)
                elif self.current_provider == LLMProvider.OPENAI:
                    return self._generate_openai(australian_english_prompt, max_tokens, temperature)
                elif self.current_provider == LLMProvider.ANTHROPIC:
                    return self._generate_anthropic(australian_english_prompt, max_tokens, temperature)
                elif self.current_provider == LLMProvider.GOOGLE:
                    return self._generate_google(australian_english_prompt, max_tokens, temperature)
                else:
                    raise LLMServiceError(f"Unknown provider: {self.current_provider}")
                    
            except (LLMConnectionError, LLMTimeoutError) as e:
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"LLM request failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"LLM request failed after {retry_count} attempts: {str(e)}")
                    raise
            except LLMRateLimitError as e:
                if attempt < retry_count - 1:
                    wait_time = 60  # Wait longer for rate limits
                    logger.warning(f"Rate limit hit (attempt {attempt + 1}), waiting {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {retry_count} attempts: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error in LLM generation: {str(e)}")
                raise LLMServiceError(f"LLM generation failed: {str(e)}")
        
        return None

    def _generate_ollama(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using Ollama API"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.current_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            elif response.status_code == 404:
                raise LLMServiceError(f"Model '{self.current_model}' not found. Please ensure it's installed in Ollama.")
            elif response.status_code >= 500:
                raise LLMServiceError(f"Ollama server error: {response.status_code} - {response.text}")
            else:
                raise LLMServiceError(f"Ollama API error: {response.status_code} - {response.text}")
                
        except ConnectionError as e:
            raise LLMConnectionError(f"Could not connect to Ollama at {self.base_url}. Please ensure Ollama is running.")
        except Timeout as e:
            raise LLMTimeoutError(f"Ollama request timed out after {self.timeout} seconds")
        except RequestException as e:
            raise LLMServiceError(f"Ollama request failed: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected Ollama error: {str(e)}")

    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using OpenAI API"""
        if not self.api_key:
            raise LLMServiceError("OpenAI API key not configured")
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.current_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            elif response.status_code == 401:
                raise LLMServiceError("OpenAI API key is invalid or missing")
            elif response.status_code == 429:
                raise LLMRateLimitError("OpenAI rate limit exceeded")
            elif response.status_code >= 500:
                raise LLMServiceError(f"OpenAI server error: {response.status_code} - {response.text}")
            else:
                raise LLMServiceError(f"OpenAI API error: {response.status_code} - {response.text}")
                
        except ConnectionError as e:
            raise LLMConnectionError("Could not connect to OpenAI API")
        except Timeout as e:
            raise LLMTimeoutError(f"OpenAI request timed out after {self.timeout} seconds")
        except RequestException as e:
            raise LLMServiceError(f"OpenAI request failed: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected OpenAI error: {str(e)}")

    def _generate_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using Anthropic Claude API"""
        if not self.api_key:
            raise LLMServiceError("Anthropic API key not configured")
        
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": self.current_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("content", [{}])[0].get("text", "")
            elif response.status_code == 401:
                raise LLMServiceError("Anthropic API key is invalid or missing")
            elif response.status_code == 429:
                raise LLMRateLimitError("Anthropic rate limit exceeded")
            elif response.status_code >= 500:
                raise LLMServiceError(f"Anthropic server error: {response.status_code} - {response.text}")
            else:
                raise LLMServiceError(f"Anthropic API error: {response.status_code} - {response.text}")
                
        except ConnectionError as e:
            raise LLMConnectionError("Could not connect to Anthropic API")
        except Timeout as e:
            raise LLMTimeoutError(f"Anthropic request timed out after {self.timeout} seconds")
        except RequestException as e:
            raise LLMServiceError(f"Anthropic request failed: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected Anthropic error: {str(e)}")

    def _generate_google(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using Google Gemini API"""
        if not self.api_key:
            raise LLMServiceError("Google API key not configured")
        
        url = f"{self.base_url}/models/{self.current_model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(f"{url}?key={self.api_key}", headers=headers, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            elif response.status_code == 401:
                raise LLMServiceError("Google API key is invalid or missing")
            elif response.status_code == 429:
                raise LLMRateLimitError("Google API rate limit exceeded")
            elif response.status_code >= 500:
                raise LLMServiceError(f"Google server error: {response.status_code} - {response.text}")
            else:
                raise LLMServiceError(f"Google API error: {response.status_code} - {response.text}")
                
        except ConnectionError as e:
            raise LLMConnectionError("Could not connect to Google API")
        except Timeout as e:
            raise LLMTimeoutError(f"Google request timed out after {self.timeout} seconds")
        except RequestException as e:
            raise LLMServiceError(f"Google request failed: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"Unexpected Google error: {str(e)}")

    def get_default_vision_model(self) -> Optional[str]:
        """Return the default vision model for the current provider, if available."""
        if self.current_provider == LLMProvider.OLLAMA:
            models = self._list_ollama_models() or []
            for vision_model in ["llava:latest", "bakllava:latest"]:
                if vision_model in models:
                    return vision_model
            return None
        elif self.current_provider == LLMProvider.OPENAI:
            models = self._list_openai_models() or []
            for vision_model in ["gpt-4o", "gpt-4-vision-preview"]:
                if vision_model in models:
                    return vision_model
            return None
        elif self.current_provider == LLMProvider.ANTHROPIC:
            models = self._list_anthropic_models() or []
            for vision_model in ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]:
                if vision_model in models:
                    return vision_model
            return None
        elif self.current_provider == LLMProvider.GOOGLE:
            models = self._list_google_models() or []
            for vision_model in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]:
                if vision_model in models:
                    return vision_model
            return None
        return None

    def list_models(self) -> Optional[List[str]]:
        """List all available models for the current provider (text and vision)."""
        if self.current_provider == LLMProvider.OLLAMA:
            # Only return models that are actually installed in Ollama
            models = self._list_ollama_models() or []
            return models
        elif self.current_provider == LLMProvider.OPENAI:
            models = self._list_openai_models() or []
            return models
        elif self.current_provider == LLMProvider.ANTHROPIC:
            models = self._list_anthropic_models() or []
            return models
        elif self.current_provider == LLMProvider.GOOGLE:
            models = self._list_google_models() or []
            return models
        return None

    def has_vision_models(self) -> bool:
        """Check if any vision models are actually available for the current provider."""
        if self.current_provider == LLMProvider.OLLAMA:
            models = self._list_ollama_models() or []
            vision_models = ["llava", "bakllava"]
            return any(any(vm in model for vm in vision_models) for model in models)
        elif self.current_provider == LLMProvider.OPENAI:
            models = self._list_openai_models() or []
            vision_models = ["gpt-4o", "gpt-4-vision"]
            return any(any(vm in model for vm in vision_models) for model in models)
        elif self.current_provider == LLMProvider.ANTHROPIC:
            models = self._list_anthropic_models() or []
            vision_models = ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            return any(any(vm in model for vm in vision_models) for model in models)
        elif self.current_provider == LLMProvider.GOOGLE:
            models = self._list_google_models() or []
            vision_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
            return any(any(vm in model for vm in vision_models) for model in models)
        return False

    def _list_ollama_models(self) -> Optional[List[str]]:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)  # Shorter timeout for model listing
            if response.ok:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Error listing Ollama models: {e}")
        return None

    def _list_openai_models(self) -> Optional[List[str]]:
        """List available OpenAI models"""
        if not self.api_key:
            return None
        
        try:
            # Try to fetch models from OpenAI API
            import openai
            openai.api_key = self.api_key
            
            response = openai.Model.list()
            if response and hasattr(response, 'data'):
                # Filter for chat models and sort by name
                chat_models = [
                    model.id for model in response.data 
                    if 'gpt' in model.id.lower() and 'instruct' not in model.id.lower()
                ]
                return sorted(chat_models)
        except ImportError:
            print("OpenAI package not installed. Using fallback models.")
        except Exception as e:
            print(f"Could not fetch OpenAI models from API: {e}")
        
        # Fallback to common OpenAI models
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

    def _list_anthropic_models(self) -> Optional[List[str]]:
        """List available Anthropic models"""
        if not self.api_key:
            return None
        
        try:
            # Try to fetch models from Anthropic API
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.models.list()
            if response and hasattr(response, 'data'):
                # Filter for Claude models and sort by name
                claude_models = [
                    model.id for model in response.data 
                    if 'claude' in model.id.lower()
                ]
                return sorted(claude_models)
        except ImportError:
            print("Anthropic package not installed. Using fallback models.")
        except Exception as e:
            print(f"Could not fetch Anthropic models from API: {e}")
        
        # Fallback to common Anthropic models
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]

    def _list_google_models(self) -> Optional[List[str]]:
        """List available Google Gemini models"""
        if not self.api_key:
            return None
        
        try:
            # Try to fetch models from Google AI API
            url = f"{self.base_url}/models"
            response = requests.get(f"{url}?key={self.api_key}", timeout=10)
            if response.ok:
                data = response.json()
                # Filter for Gemini models and sort by name
                gemini_models = [
                    model["name"].split("/")[-1] for model in data.get("models", [])
                    if "gemini" in model["name"].lower()
                ]
                return sorted(gemini_models)
        except Exception as e:
            print(f"Could not fetch Google models from API: {e}")
        
        # Fallback to common Google Gemini models
        return [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-1.0-pro-001"
        ]

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their configurations"""
        providers = []
        
        # Check Ollama
        try:
            response = requests.get(f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/tags", timeout=5)
            ollama_available = response.ok
        except:
            ollama_available = False
        
        providers.append({
            "name": "ollama",
            "display_name": "Ollama (Local)",
            "available": ollama_available,
            "requires_api_key": False,
            "default_model": os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        })
        
        # Check OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        providers.append({
            "name": "openai",
            "display_name": "OpenAI",
            "available": bool(openai_key),
            "requires_api_key": True,
            "default_model": os.getenv("OPENAI_MODEL", "gpt-4")
        })
        
        # Check Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        providers.append({
            "name": "anthropic",
            "display_name": "Anthropic Claude",
            "available": bool(anthropic_key),
            "requires_api_key": True,
            "default_model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        })
        
        # Check Google Gemini
        google_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        providers.append({
            "name": "google",
            "display_name": "Google Gemini",
            "available": bool(google_key),
            "requires_api_key": True,
            "default_model": os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        })
        
        return providers

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the current provider"""
        result = {
            "provider": self.current_provider.value,
            "model": self.current_model,
            "connected": False,
            "error": None
        }
        
        try:
            # Try a simple generation with minimal retry
            test_response = self.generate_text("Hello", max_tokens=10, temperature=0.1, retry_count=1)
            if test_response:
                result["connected"] = True
            else:
                result["error"] = "No response from provider"
        except LLMServiceError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result