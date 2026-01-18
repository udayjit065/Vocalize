"""
FastAPI Backend for TTS Fluency Analysis
Vercel Serverless Function with Debug Logging
"""
import sys
import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Create FastAPI app with /api as root path for Vercel
app = FastAPI(root_path="/api")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Fluency Analysis API Running", "api_key_set": bool(API_KEY)}

@app.get("/health")
def health():
    return {"status": "healthy", "api_key_loaded": bool(API_KEY)}

@app.get("/debug")
def debug():
    """Debug endpoint to check configuration"""
    return {
        "api_key_set": bool(API_KEY),
        "api_key_prefix": API_KEY[:10] + "..." if API_KEY else None,
        "python_version": sys.version,
        "cwd": os.getcwd(),
    }

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze audio file for fluency"""
    # Use /tmp/ for temp files (Vercel serverless requirement)
    upload_path = f"/tmp/temp_upload_{file.filename}"
    converted_path = f"/tmp/temp_converted_{file.filename}.wav"
    
    try:
        # Step 1: Save uploaded file
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Step 2: Import and convert audio
        from convert_audio import convert_to_google_format
        convert_to_google_format(upload_path, converted_path)
        
        # Step 3: Import and analyze
        from evaluation_engine.stt_api_key import analyze_audio_with_api_key
        
        if not API_KEY:
            return {"error": "GOOGLE_API_KEY not set in environment"}
        
        result = analyze_audio_with_api_key(converted_path, API_KEY, "auto")
        return result
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return {"error": str(e), "trace": error_trace}
        
    finally:
        # Cleanup both files
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
            if os.path.exists(converted_path):
                os.remove(converted_path)
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
