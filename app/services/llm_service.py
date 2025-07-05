import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

class LLMService:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self._base_url = base_url
        self._model = model
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        load_dotenv(override=True)  # Reload .env file
        self.base_url = self._base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = self._model or os.getenv("OLLAMA_MODEL", "llama2")
        print(f"LLM Service configured with: {self.base_url}, model: {self.model}")
    
    def refresh_config(self):
        """Refresh configuration from environment variables"""
        self._load_config()

    def generate_text(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Optional[str]:
        """Generate text using Ollama API"""
        # Refresh config before each request to pick up .env changes
        self._load_config()
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
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
                print(f"Make sure Ollama is running at {self.base_url} with model {self.model}")
        except requests.exceptions.ConnectionError:
            print(f"Could not connect to Ollama at {self.base_url}")
            print("Please make sure Ollama is running: ollama serve")
        except Exception as e:
            print(f"LLM generation error: {e}")
        return None

    def list_models(self) -> Optional[list]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.ok:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            print(f"Error listing models: {e}")
        return None 