import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from enum import Enum

class LLMProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LLMService:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider
        self.model = model
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        load_dotenv(override=True)  # Reload .env file
        
        # Determine provider and model
        if self.provider:
            self.current_provider = LLMProvider(self.provider)
        else:
            # Default provider from env or fallback to Ollama
            provider_str = os.getenv("LLM_PROVIDER", "ollama").lower()
            self.current_provider = LLMProvider(provider_str)
        
        if self.model:
            self.current_model = self.model
        else:
            # Get model for current provider
            self.current_model = self._get_default_model()
        
        # Load provider-specific configuration
        self._load_provider_config()
        
        print(f"LLM Service configured with: {self.current_provider.value}, model: {self.current_model}")
    
    def _get_default_model(self) -> str:
        """Get default model for current provider"""
        if self.current_provider == LLMProvider.OLLAMA:
            return os.getenv("OLLAMA_MODEL", "llama3.2:latest")
        elif self.current_provider == LLMProvider.OPENAI:
            return os.getenv("OPENAI_MODEL", "gpt-4")
        elif self.current_provider == LLMProvider.ANTHROPIC:
            return os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        return "llama3.2:latest"  # Fallback
    
    def _load_provider_config(self):
        """Load provider-specific configuration"""
        if self.current_provider == LLMProvider.OLLAMA:
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.api_key = None
        elif self.current_provider == LLMProvider.OPENAI:
            self.base_url = "https://api.openai.com/v1"
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                print("Warning: OPENAI_API_KEY not found in environment")
        elif self.current_provider == LLMProvider.ANTHROPIC:
            self.base_url = "https://api.anthropic.com/v1"
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                print("Warning: ANTHROPIC_API_KEY not found in environment")
    
    def refresh_config(self):
        """Refresh configuration from environment variables"""
        self._load_config()

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """Generate text using the configured LLM provider"""
        # Refresh config before each request to pick up .env changes
        self._load_config()
        
        if self.current_provider == LLMProvider.OLLAMA:
            return self._generate_ollama(prompt, max_tokens, temperature)
        elif self.current_provider == LLMProvider.OPENAI:
            return self._generate_openai(prompt, max_tokens, temperature)
        elif self.current_provider == LLMProvider.ANTHROPIC:
            return self._generate_anthropic(prompt, max_tokens, temperature)
        else:
            print(f"Unknown provider: {self.current_provider}")
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
            response = requests.post(url, json=payload, timeout=60)
            if response.ok:
                data = response.json()
                return data.get("response", "")
            else:
                print(f"Ollama API error: {response.status_code} - {response.text}")
                print(f"Make sure Ollama is running at {self.base_url} with model {self.current_model}")
        except requests.exceptions.ConnectionError:
            print(f"Could not connect to Ollama at {self.base_url}")
            print("Please make sure Ollama is running: ollama serve")
        except Exception as e:
            print(f"Ollama generation error: {e}")
        return None

    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using OpenAI API"""
        if not self.api_key:
            print("OpenAI API key not configured")
            return None
        
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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.ok:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"OpenAI generation error: {e}")
        return None

    def _generate_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Generate text using Anthropic Claude API"""
        if not self.api_key:
            print("Anthropic API key not configured")
            return None
        
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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.ok:
                data = response.json()
                return data.get("content", [{}])[0].get("text", "")
            else:
                print(f"Anthropic API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Anthropic generation error: {e}")
        return None

    def list_models(self) -> Optional[List[str]]:
        """List available models for the current provider"""
        if self.current_provider == LLMProvider.OLLAMA:
            return self._list_ollama_models()
        elif self.current_provider == LLMProvider.OPENAI:
            return self._list_openai_models()
        elif self.current_provider == LLMProvider.ANTHROPIC:
            return self._list_anthropic_models()
        return None

    def _list_ollama_models(self) -> Optional[List[str]]:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
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
            # Try a simple generation
            test_response = self.generate_text("Hello", max_tokens=10, temperature=0.1)
            if test_response:
                result["connected"] = True
            else:
                result["error"] = "No response from provider"
        except Exception as e:
            result["error"] = str(e)
        
        return result 