#!/usr/bin/env python3
"""
Setup script for AI Cover Letter Generator
Installs dependencies with uv and initializes the database
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up AI Cover Letter Generator...")
    
    # Check if uv is installed
    if not run_command("uv --version", "Checking if uv is installed"):
        print("❌ uv is not installed. Please install it first:")
        print("   pip install uv")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Creating from template...")
        # Create .env file with default values
        env_content = """# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/cover_letter_db

# LinkedIn Credentials (for profile scraping)
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Ollama Configuration (for local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Optional: Alternative LLM endpoints
# OPENAI_API_KEY=your_openai_api_key
# ANTHROPIC_API_KEY=your_anthropic_api_key
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("📝 Created .env file. Please edit it with your database credentials and API keys")
    
    # Initialize database
    print("🗄️  Initializing database...")
    if not run_command("alembic upgrade head", "Running database migrations"):
        print("❌ Failed to initialize database")
        print("💡 Make sure PostgreSQL is running and your .env file has correct DATABASE_URL")
        sys.exit(1)
    
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your credentials")
    print("2. Start the application: uvicorn app.main:app --reload")
    print("3. Open http://localhost:8000 in your browser")

if __name__ == "__main__":
    main() 