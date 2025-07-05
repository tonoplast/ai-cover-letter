from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import routes
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Cover Letter Generator")

app.include_router(routes.router)

# Serve static files (UI)
static_dir = Path(__file__).parent / 'static'
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Serve the upload page at root
    @app.get("/")
    def root():
        return FileResponse("app/static/upload.html")
else:
    @app.get("/")
    def root_fallback():
        return {"message": "Welcome to the AI Cover Letter Generator API. Static UI not found."} 