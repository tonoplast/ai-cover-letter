# AI Cover Letter Generator

An advanced AI-powered system for generating highly personalized, professional cover letters using your CVs, experiences, and job descriptions—whether entered manually or scraped from job ad websites. Features include RAG (Retrieval-Augmented Generation) with embeddings, recency-weighted context, writing style adaptation, batch processing, and a modern web interface.

---

## Features

- **Modern Web Interface**: Tabbed UI for document upload, cover letter generation, chat/edit, and database inspection.
- **Batch Cover Letter Generation**: Input multiple job ad URLs for automatic scraping and tailored cover letter creation.
- **Document Parsing**: Supports PDF, DOCX, TXT, CSV, XLSX, and LinkedIn profile import.
- **RAG (Retrieval-Augmented Generation)**: Uses embeddings (MiniLM) to find and inject the most relevant content from all your uploaded documents.
- **Recency Weighting**: Prioritizes recent CVs and cover letters for both experience and writing style.
- **Writing Style Adaptation**: Learns your style from previous cover letters and applies it to new ones.
- **Local LLM Integration**: Works with local models (e.g., Ollama, llama3.2) for fast, private generation.
- **Company Research**: Integrates with multiple search providers (Tavily, Google, Brave Search, DuckDuckGo, YaCy, SearXNG) for company info.
- **Interactive Chat & Edit**: Refine cover letters in real time with an AI chat interface.
- **Professional Export**: Download cover letters as PDF, DOCX, or TXT.
- **Database Management**: Inspect, selectively delete, and manage all documents and generated content.
- **Anti-blocking for Scraping**: Configurable delay between website scrapes to avoid IP bans.

---

## Getting Started

### 1. **Quick Setup (Recommended)**

```bash
# Run the setup script
python setup.py

# Or install dependencies manually
pip install -r requirements.txt
# For RAG and LLM features:
pip install sentence-transformers torch reportlab google-generativeai selenium webdriver-manager
```

### 2. **Environment Setup**

Copy `env.template` to `.env` and configure your settings:

```bash
cp env.template .env
```

**Minimal setup for local development:**
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
SECRET_KEY=your_random_secret_key_here
DEBUG=True
```

**Full setup with company research:**
```env
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Company Research APIs (optional)
TAVILY_API_KEY=tvly-your_tavily_api_key_here  # Recommended: https://tavily.com/
GOOGLE_API_KEY=your_google_api_key_here       # Optional: https://makersuite.google.com/
BRAVE_API_KEY=your_brave_api_key_here         # Optional: https://api.search.brave.com/

# Self-hosted search engines (optional)
YACY_URL=http://localhost:8090                # Install: https://yacy.net/
SEARXNG_URL=http://localhost:8080             # Install: https://docs.searxng.org/

# Security
SECRET_KEY=your_random_secret_key_here
DEBUG=False
```

**Available Search Providers:**
- **Tavily AI** (Recommended): Free tier available, comprehensive company research
- **Google AI**: Requires API key, high-quality results
- **Brave Search**: Privacy-focused, works without API key (better with one)
- **DuckDuckGo**: Free, no API key required, rate limited
- **YaCy**: Self-hosted, privacy-focused
- **SearXNG**: Self-hosted, meta-search engine

### 3. **Initialize the Database**

```bash
alembic upgrade head
```

### 4. **Run the Application**

```bash
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## Usage

### **Web Interface**

#### 📁 Upload Documents Tab
- Drag & drop or select multiple files (CV, cover letter, LinkedIn, etc.).
- Assign document types.
- Upload your most recent CV first for best results.

#### ✍️ Generate Cover Letter Tab
- **Manual:** Enter job title, company, and description, select tone, and generate.
- **Company Research:** Toggle to include verified company information (mission, values, industry) in your cover letter.
- **Batch:** Paste multiple job ad URLs, set delay (to avoid blocking), and generate tailored cover letters for each.

#### 💬 Chat & Edit Tab
- Select a cover letter, chat with the AI to refine it, and export in your preferred format.

#### 📊 Database Tab
- Inspect all uploaded documents, cover letters, experiences, and company research.
- Selectively delete or bulk clear items.

---

### **Batch Website Scraping Example**

1. Go to the "Generate Cover Letter" tab.
2. Paste job ad URLs (one per line).
3. Set delay (e.g., 3–7 seconds for Seek.com.au).
4. Click "Batch Generate Cover Letters".
5. Download or edit results as needed.

---

### **API Examples**

#### Upload Multiple Documents

```bash
curl -X POST "http://localhost:8000/upload-multiple-documents" \
  -F "files=@cv_latest.pdf" \
  -F "files=@cover_letter_sample.pdf" \
  -F "document_types=cv" \
  -F "document_types=cover_letter"
```

#### Generate Cover Letter (API)

```bash
curl -X POST "http://localhost:8000/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Data Scientist",
    "company_name": "Victoria Legal Aid",
    "job_description": "We are seeking a data scientist...",
    "tone": "professional"
  }'
```

#### Batch Cover Letter Generation (API)

```bash
curl -X POST "http://localhost:8000/batch-cover-letters" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Software Engineer",
    "job_description": "Exciting opportunity...",
    "tone": "enthusiastic",
    "websites": [
      "https://www.seek.com.au/job/123456",
      "https://www.seek.com.au/job/789012"
    ],
    "delay_seconds": 5
  }'
```

---

## How It Works

- **RAG Pipeline:** All cover letter generation (manual or batch) uses a RAG pipeline with MiniLM embeddings to retrieve the most relevant content from your uploaded documents, weighted by recency.
- **Writing Style:** Your writing style is learned from all previous cover letters, with more weight to recent ones.
- **LLM Generation:** The LLM receives a prompt with your experiences, writing style, and the most relevant document chunks.
- **Consistent Output:** Whether you enter job info manually or scrape from a website, the same logic and context are used for tailored, authentic cover letters.

---

## Advanced Features

- **LinkedIn Integration:** Import your LinkedIn profile for richer context.
- **Company Research:** Use multiple providers for company info, with fallback and rate limiting.
- **Anti-bot Scraping:** Selenium-based fallback for protected job sites, with configurable delays.
- **Selective Deletion:** Delete individual or multiple documents, cover letters, or experiences from the database.
- **Visual Diff:** See changes between original and revised cover letters in the chat interface.

---

## Troubleshooting

- **403/Blocked on Scraping:** Increase delay between jobs, or use manual job description input for protected sites.
- **No CV Uploaded:** Upload at least one CV for best RAG results.
- **LLM Not Responding:** Check your Ollama or LLM server is running and accessible.

---

## Contributing

Pull requests and feature suggestions are welcome! Please open an issue or PR.

---

## License

MIT

---

**For questions or support, open an issue or contact the maintainer.** 