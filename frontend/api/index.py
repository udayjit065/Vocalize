"""
FastAPI Backend for TTS Fluency Analysis
"""
import sys
import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Add parent directory to path to import evaluation_engine (for local development)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Also add current directory for Docker deployment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from evaluation_engine.stt_api_key import analyze_audio_with_api_key, analyze_audio_with_sdk

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Fluency Analysis API Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

from convert_audio import convert_to_google_format

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    # Save uploaded file
    upload_path = f"temp_upload_{file.filename}"
    converted_path = f"temp_converted_{file.filename}.wav"
    
    try:
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Convert audio to Google-compatible format
        # This fixes the 400 error by ensuring format is 16000Hz WAV
        convert_to_google_format(upload_path, converted_path)
        
        # Analyze
        if GOOGLE_JSON:
            try:
                # Parse JSON string if it exists
                creds = json.loads(GOOGLE_JSON)
                result = analyze_audio_with_sdk(converted_path, creds, "auto")
            except Exception as e:
                print(f"SDK Error: {str(e)}")
                # Fallback to API Key if SDK fails
                result = analyze_audio_with_api_key(converted_path, API_KEY, "auto")
        else:
            result = analyze_audio_with_api_key(converted_path, API_KEY, "auto")
            
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
        
    finally:
        # Cleanup both files
        if os.path.exists(upload_path):
            os.remove(upload_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
