#!/usr/bin/env python3
"""
Test script to demonstrate timeout configuration for LLM providers.
This script shows how to configure different timeouts for different providers.
"""

import os
import time
from app.services.llm_service import LLMService

def test_timeout_configuration():
    """Test timeout configuration for different LLM providers"""
    print("🔧 Testing LLM Provider Timeout Configuration")
    print("=" * 50)
    
    # Test different timeout configurations
    test_configs = [
        {
            "name": "Fast Timeout (30s)",
            "env_vars": {
                "OLLAMA_TIMEOUT": "30",
                "OPENAI_TIMEOUT": "30", 
                "ANTHROPIC_TIMEOUT": "30"
            }
        },
        {
            "name": "Medium Timeout (60s)",
            "env_vars": {
                "OLLAMA_TIMEOUT": "60",
                "OPENAI_TIMEOUT": "60",
                "ANTHROPIC_TIMEOUT": "60"
            }
        },
        {
            "name": "Slow Timeout (180s)",
            "env_vars": {
                "OLLAMA_TIMEOUT": "180",
                "OPENAI_TIMEOUT": "180",
                "ANTHROPIC_TIMEOUT": "180"
            }
        }
    ]
    
    for config in test_configs:
        print(f"\n📋 Testing: {config['name']}")
        print("-" * 30)
        
        # Set environment variables for this test
        for key, value in config['env_vars'].items():
            os.environ[key] = value
        
        # Test each provider
        providers = ['ollama', 'openai', 'anthropic']
        
        for provider in providers:
            print(f"\n  Testing {provider.upper()}:")
            
            try:
                # Create service with current timeout config
                llm_service = LLMService(provider=provider)
                
                # Show current timeout
                print(f"    Timeout: {llm_service.timeout} seconds")
                
                # Test connection (this will use the configured timeout)
                start_time = time.time()
                connection_test = llm_service.test_connection()
                elapsed_time = time.time() - start_time
                
                print(f"    Connection: {'✅ Connected' if connection_test['connected'] else '❌ Failed'}")
                print(f"    Response time: {elapsed_time:.2f} seconds")
                
                if connection_test['error']:
                    print(f"    Error: {connection_test['error']}")
                    
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Timeout configuration test completed!")
    
    print("\n💡 Timeout Configuration Tips:")
    print("   • Ollama: Use 120-300 seconds for large local models")
    print("   • OpenAI: 60 seconds is usually sufficient")
    print("   • Anthropic: 90-180 seconds for complex Claude models")
    print("   • Adjust based on your model size and hardware")
    
    print("\n🔧 To configure timeouts, add to your .env file:")
    print("   OLLAMA_TIMEOUT=120    # 2 minutes for local models")
    print("   OPENAI_TIMEOUT=60     # 1 minute for OpenAI")
    print("   ANTHROPIC_TIMEOUT=90  # 1.5 minutes for Claude")

def show_current_timeouts():
    """Show current timeout configuration"""
    print("\n📊 Current Timeout Configuration:")
    print("-" * 40)
    
    providers = [
        ('Ollama', 'OLLAMA_TIMEOUT', '120'),
        ('OpenAI', 'OPENAI_TIMEOUT', '60'),
        ('Anthropic', 'ANTHROPIC_TIMEOUT', '90')
    ]
    
    for name, env_var, default in providers:
        current_value = os.getenv(env_var, default)
        print(f"  {name}: {current_value} seconds")
    
    print("\n💡 These are the default values if not set in .env")

if __name__ == "__main__":
    show_current_timeouts()
    test_timeout_configuration() 