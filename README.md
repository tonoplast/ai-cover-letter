# AI Cover Letter Generator

An advanced AI-powered system for generating highly personalized, professional cover letters using your CVs, experiences, and job descriptions—whether entered manually or scraped from job ad websites. Features include RAG (Retrieval-Augmented Generation) with embeddings, recency-weighted context, writing style adaptation, batch processing, multiple LLM providers, and a modern web interface.

---

## Features

- **Modern Web Interface**: Clean, tabbed UI for document upload, cover letter generation, chat/edit, and database inspection with improved layout.
- **Multiple LLM Providers**: Support for Ollama (local), OpenAI, and Anthropic Claude with dynamic model selection.
- **Batch Cover Letter Generation**: Input multiple job ad URLs for automatic scraping and tailored cover letter creation.
- **Document Parsing**: Supports PDF, DOCX, TXT, CSV, XLSX, and LinkedIn profile import.
- **Document Weighting**: Configurable weighting by document type and recency for better RAG performance.
- **RAG (Retrieval-Augmented Generation)**: Uses embeddings (MiniLM) to find and inject the most relevant content from all your uploaded documents.
- **Recency Weighting**: Prioritizes recent CVs and cover letters for both experience and writing style.
- **Writing Style Adaptation**: Learns your style from previous cover letters and applies it to new ones.
- **Company Research**: Integrates with multiple search providers (Tavily, OpenAI, Google, Brave Search, DuckDuckGo, YaCy, SearXNG) for company info.
- **Country-Specific Search**: Focus company research on specific countries for more relevant results.
- **Interactive Chat & Edit**: Refine cover letters in real time with an AI chat interface using your preferred LLM provider.
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
# LLM Configuration (choose one or more)
LLM_PROVIDER=ollama  # Default provider: ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# OpenAI (optional)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Anthropic (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Security
SECRET_KEY=your_random_secret_key_here
DEBUG=True
```

**Full setup with company research:**
```env
# LLM Configuration
LLM_PROVIDER=ollama  # Default provider
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Company Research APIs (optional)
TAVILY_API_KEY=tvly-your_tavily_api_key_here  # Recommended: https://tavily.com/
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here       # Optional: https://makersuite.google.com/
BRAVE_API_KEY=your_brave_api_key_here         # Optional: https://api.search.brave.com/

# Self-hosted search engines (optional)
YACY_URL=http://localhost:8090                # Install: https://yacy.net/
SEARXNG_URL=http://localhost:8080             # Install: https://docs.searxng.org/

# Document Weighting (optional)
CV_WEIGHT=1.0
COVER_LETTER_WEIGHT=0.8
LINKEDIN_WEIGHT=0.6
OTHER_WEIGHT=0.4
RECENCY_PERIOD_DAYS=365

# Security
SECRET_KEY=your_random_secret_key_here
DEBUG=False
```

**Available LLM Providers:**
- **Ollama (Local)**: Fast, private, works offline with local models
- **OpenAI**: High-quality models (GPT-4, GPT-3.5), requires API key
- **Anthropic Claude**: Advanced reasoning, requires API key
- **Google Gemini**: Fast, cost-effective models (Gemini-1.5 Flash, Gemini-1.5 Pro), requires API key

**Available Search Providers:**
- **Tavily AI** (Recommended): Free tier available, comprehensive company research
- **OpenAI**: Uses GPT models for intelligent search, requires API key
- **Google Gemini**: Uses Gemini AI for intelligent company research, requires API key
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
- Assign document types with configurable weighting.
- Upload your most recent CV first for best results.
- **Smart Filename Parsing:** The system automatically detects document types and dates from filenames in the format `YYYY-MM-DD_Type_Company-Name.ext`.

#### ✍️ Generate Cover Letter Tab
- **Manual:** Enter job title, company, and description, select tone, and generate.
- **Company Research:** Toggle to include verified company information (mission, values, industry) in your cover letter.
- **Research Provider Selection:** Choose from multiple search providers with rate limit information.
- **Country-Specific Search:** Focus research on specific countries for more relevant results.
- **LLM Provider & Model Selection:** Choose your preferred AI provider and specific model.
- **Batch:** Paste multiple job ad URLs, set delay (to avoid blocking), and generate tailored cover letters for each.

#### 💬 Chat & Edit Tab
- Select a cover letter, chat with the AI to refine it using your preferred LLM provider and model.
- Export in your preferred format (PDF, DOCX, TXT).

#### 📊 Database Tab
- Inspect all uploaded documents, cover letters, experiences, and company research.
- Selectively delete or bulk clear items.

---

### **LLM Provider & Model Selection**

The system supports multiple LLM providers with dynamic model loading:

1. **Auto (Use Default)**: Uses the configured default provider and model
2. **Ollama (Local)**: Shows all available local models (requires Ollama running)
3. **OpenAI**: Shows all available OpenAI models (requires API key)
4. **Anthropic Claude**: Shows all available Claude models (requires API key)
5. **Google Gemini**: Shows all available Gemini models (requires API key)

**Model Selection Flow:**
- When you select a provider, the AI Model dropdown automatically populates with available models
- You can choose "Auto (Use Default)" to use the system's default model
- Or select a specific model for fine-tuned control

---

### **Company Research Features**

**Research Provider Selection:**
- **Auto (Best Available)**: System chooses the best available provider
- **Tavily AI**: Recommended for comprehensive company research
- **OpenAI**: Intelligent search using GPT models
- **Google Gemini**: Intelligent search using Gemini AI models
- **Brave Search**: Privacy-focused search
- **DuckDuckGo**: Free, no API key required
- **YaCy**: Self-hosted, privacy-focused
- **SearXNG**: Self-hosted meta-search

**Country-Specific Search:**
- Focus research on specific countries for more relevant results
- Available countries: Australia, United States, Canada, United Kingdom, Germany, France, Netherlands, Sweden, Norway, Denmark, Finland, Switzerland, Singapore, Japan, South Korea, New Zealand, Ireland, Belgium, Austria

---

### **Batch Website Scraping Example**

1. Go to the "Generate Cover Letter" tab.
2. Paste job ad URLs (one per line).
3. Configure company research settings (provider, country).
4. Select your preferred LLM provider and model.
5. Set delay (e.g., 3–7 seconds for Seek.com.au).
6. Click "Batch Generate Cover Letters".
7. Download or edit results as needed.

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
    "tone": "professional",
    "include_company_research": true,
    "research_provider": "tavily",
    "research_country": "Australia",
    "llm_provider": "google",
    "llm_model": "gemini-1.5-flash"
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
    "delay_seconds": 5,
    "include_company_research": true,
    "research_provider": "openai",
    "research_country": "Australia",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-sonnet-20240229"
  }'
```

#### Chat with Cover Letter (API)

```bash
curl -X POST "http://localhost:8000/chat-with-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "cover_letter_id": 1,
    "message": "Make this cover letter more professional",
    "llm_provider": "google",
    "llm_model": "gemini-1.5-flash"
  }'
```

---

## How It Works

- **RAG Pipeline:** All cover letter generation (manual or batch) uses a RAG pipeline with MiniLM embeddings to retrieve the most relevant content from your uploaded documents, weighted by recency and document type.
- **Writing Style:** Your writing style is learned from all previous cover letters, with more weight to recent ones.
- **LLM Generation:** The selected LLM receives a prompt with your experiences, writing style, and the most relevant document chunks.
- **Company Research:** When enabled, the system researches the company using your chosen provider and country focus.
- **Consistent Output:** Whether you enter job info manually or scrape from a website, the same logic and context are used for tailored, authentic cover letters.

---

## Filename-Based Date Extraction

The AI Cover Letter Generator includes intelligent filename parsing that automatically extracts dates and document types from your uploaded files. This feature improves the recency weighting system by using the actual document date rather than just the upload date.

### **Supported Filename Format**

The system recognizes filenames in the following format:
```
YYYY-MM-DD_Type_Company-Name.ext
```

**Examples:**
- `2025-05-01_CV_Data-Science.pdf` - CV from May 1, 2025 for Data Science role
- `2024-10-21_Cover-Letter_Lookahead.pdf` - Cover letter from October 21, 2024 for Lookahead
- `2023-09-01_CV_Neuroscience.pdf` - CV from September 1, 2023 for Neuroscience role
- `2022-01-01_CV.pdf` - CV from January 1, 2022 (no company specified)

### **Automatic Detection**

When you upload documents, the system automatically:

1. **Extracts the date** from the filename (if present)
2. **Detects the document type** (CV, Cover-Letter, LinkedIn, etc.)
3. **Extracts company information** (if included)
4. **Uses the filename date for recency weighting** instead of upload date
5. **Falls back to upload date** if no date is found in the filename

### **Document Type Mapping**

The system recognizes these document types in filenames:
- `CV` or `Resume` → `cv`
- `Cover-Letter` or `CoverLetter` → `cover_letter`
- `LinkedIn` or `Profile` → `linkedin`
- Other types → `other`

### **Benefits**

- **More Accurate Recency Weighting:** Uses the actual document date rather than upload date
- **Automatic Document Type Detection:** Reduces manual selection errors
- **Better RAG Performance:** More recent documents get higher weights for better context
- **Consistent Formatting:** Generated documents follow the same naming convention

### **Fallback Behavior**

If a filename doesn't follow the expected format:
- Document type falls back to the manually selected type
- Date falls back to the upload timestamp
- Recency weighting uses the upload date
- No functionality is lost

### **Generated Filenames**

When the system generates new documents (like exported cover letters), it follows the same naming convention:
```
2025-01-15_Cover-Letter_Company-Name.pdf
```

---

## Advanced Features

- **LinkedIn Integration:** Import your LinkedIn profile for richer context.
- **Company Research:** Use multiple providers for company info, with fallback and rate limiting.
- **Country-Specific Search:** Focus research on specific countries for more relevant results.
- **Document Weighting:** Configure weights for different document types and recency periods.
- **Filename-Based Date Extraction:** Automatically extracts dates and document types from filenames for improved recency weighting.
- **Multiple LLM Providers:** Choose between local (Ollama), OpenAI, Anthropic, and Google Gemini models.
- **Dynamic Model Loading:** Automatically loads available models for each provider.
- **Anti-bot Scraping:** Selenium-based fallback for protected job sites, with configurable delays.
- **Selective Deletion:** Delete individual or multiple documents, cover letters, or experiences from the database.
- **Visual Diff:** See changes between original and revised cover letters in the chat interface.

---

## API Endpoints

### **LLM Management**
- `GET /llm-providers` - Get available LLM providers
- `GET /llm-models/{provider}` - Get available models for a provider
- `POST /test-llm-connection` - Test connection to a specific provider/model

### **Document Management**
- `POST /upload-multiple-documents` - Upload multiple documents
- `GET /documents` - List all documents
- `DELETE /delete-document/{id}` - Delete a document

### **Cover Letter Generation**
- `POST /generate-cover-letter` - Generate single cover letter
- `POST /batch-cover-letters` - Generate batch cover letters
- `POST /chat-with-cover-letter` - Chat with AI to edit cover letter

### **Company Research**
- `POST /company-research` - Research a company
- `GET /search-providers` - Get available search providers

### **Export**
- `POST /export-cover-letter/{id}?format={pdf|docx|txt}` - Export cover letter

---

## Troubleshooting

- **403/Blocked on Scraping:** Increase delay between jobs, or use manual job description input for protected sites.
- **No CV Uploaded:** Upload at least one CV for best RAG results.
- **LLM Not Responding:** Check your Ollama, OpenAI, Anthropic, or Google Gemini configuration and API keys.
- **Model Not Loading:** Ensure your LLM provider is running and accessible.
- **Company Research Failing:** Check your API keys and rate limits for the selected provider.
- **Timeout Errors:** Increase timeout values in your `.env` file for slow models.

### Timeout Configuration

If you're experiencing timeout errors with large or slow models, you can adjust the timeout settings:

```env
# LLM Timeout Configuration
OLLAMA_TIMEOUT=120    # 2 minutes for local models (increase for large models)
OPENAI_TIMEOUT=60     # 1 minute for OpenAI
ANTHROPIC_TIMEOUT=90  # 1.5 minutes for Claude (increase for complex models)
GOOGLE_TIMEOUT=60     # 1 minute for Google Gemini
```

**Recommended timeouts by model size:**
- **Small models** (7B parameters): 60-120 seconds
- **Medium models** (13B parameters): 120-180 seconds  
- **Large models** (70B+ parameters): 180-300 seconds

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Documentation

For detailed information about specific features and implementation details, see:

- **[RAG Cover Letter Weighting](./RAG_COVER_LETTER_WEIGHTING.md)** - How uploaded vs generated cover letters work in the RAG system
- **[Document Weighting](./DOCUMENT_WEIGHTING.md)** - Document type and recency weighting configuration
- **[LLM Provider Selection](./LLM_PROVIDER_SELECTION.md)** - Available LLM providers and model selection
- **[Research Provider Selection](./RESEARCH_PROVIDER_SELECTION.md)** - Company research providers and configuration
- **[Enhanced LLM Selection](./ENHANCED_LLM_SELECTION_SUMMARY.md)** - Advanced LLM selection features
- **[Enhanced Writing Style](./ENHANCED_WRITING_STYLE_SUMMARY.md)** - Writing style adaptation and analysis
- **[Implementation Summary](./IMPLEMENTATION_SUMMARY.md)** - Technical implementation overview

---

**For questions or support, open an issue or contact the maintainer.**

## Logo Recognition Options: Open Source & Vision LLM

The system supports logo recognition options for images in uploaded documents. You can select these options in the upload UI:

- **None**: No logo recognition performed.
- **Open Source**: (Stub) Intended for open-source logo recognition using models like OpenLogo or YOLO. Currently returns an empty result, but the backend is ready for integration.
- **Vision LLM**: (Stub) Intended for future use with vision-capable LLMs (e.g., GPT-4o, Gemini, Claude 3 Vision). Currently returns an empty result.

### How to Integrate OpenLogo or YOLO-based Logo Detection

1. **Install YOLOv5/YOLOv8 or OpenLogo dependencies**
   - [YOLOv5/YOLOv8](https://github.com/ultralytics/ultralytics):
     ```bash
     pip install ultralytics
     ```
   - [OpenLogo](https://github.com/MinchaoZhu/OpenLogo):
     - Download the dataset and pre-trained models from the repo.
     - Follow their setup instructions for inference.

2. **Replace the `recognize_logos_openlogo` stub**
   - Load your trained model (YOLO or OpenLogo).
   - For each image, run detection and extract logo names from the results.
   - Example (YOLOv5):
     ```python
     from ultralytics import YOLO
     model = YOLO('path/to/best.pt')
     results = model(image)
     detected_logos = [r['name'] for r in results]  # Adjust based on model output
     ```

3. **Vision LLM Integration (Future)**
   - When you have access to a vision LLM API, update the `recognize_logos_vision_llm` function to send the image and parse the response.
   - Example (pseudo-code):
     ```python
     def recognize_logos_vision_llm(image):
         # Convert image to base64 or bytes
         # Send to LLM API endpoint
         # Parse and return detected logo names
         pass
     ```

4. **Testing**
   - Use the `test_logo_recognition.py` script to test your integration on images in the `test_logos` folder.

---

**Note:**
- Open-source logo detection requires a trained model and may need a GPU for best performance.
- Vision LLMs require API access and may incur costs.

For more details, see the comments in `app/services/enhanced_document_parser.py` and the test script.

### Document Recency

Relevance for RAG (Retrieval-Augmented Generation) is determined by (in order of precedence):
1. **Date in filename** (e.g., `YYYY-MM-DD_Cover-Letter_Company.pdf` or `YYYY-MM-DD_CV_other-info.pdf`)
2. **Date in document content** (first date found in the file, e.g., `2024-10-21`)
3. **Upload date** (if no date found in filename or content)

**Upload order does not affect relevance.**

If you want a particular document to be prioritized, ensure the filename or content contains the correct date.

### Error Handling Improvements

- The backend robustly parses the `DOCUMENT_RECENCY_PERIOD_DAYS`