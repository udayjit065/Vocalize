# Vocalize Code Flow & Architecture Guide

This document provides a detailed overview of the **Vocalize** codebase, explaining how the different components interact, the data flow for audio processing, and the role of key files.

## 🏗️ High-Level Architecture

The project follows a modern **Monorepo** structure with a clear separation of concerns:

1.  **Frontend (`frontend/`)**: 
    - Built with **Next.js 14** (React).
    - Handles the UI, audio recording, and displaying results.
    - Communicates with the backend via REST API.

2.  **Backend (`backend/`)**: 
    - Built with **FastAPI** (Python).
    - Acts as the bridge between the frontend and the core analysis logic.
    - Handles file uploads, audio conversion, and API responses.

3.  **Evaluation Engine (`evaluation_engine/`)**: 
    - Contains the core business logic.
    - specialized in Speech-to-Text (STT) integration (Google Cloud) and calculating fluency metrics (WPM, fillers, pauses).

---

## 🔄 End-to-End Data Flow

Here is the step-by-step journey of a user interaction:

### 1. Audio Recording (Frontend)
- **User Action**: User clicks the "Record" button on the UI.
- **File**: `frontend/app/page.tsx`
- **Logic**: 
  - The app initializes the microphone stream using `navigator.mediaDevices.getUserMedia`.
  - It uses `extendable-media-recorder` (with a preference for `wav-encoder`) to capture high-quality audio.
  - **Why WAV?** The backend prefers uncompressed audio for better analysis accuracy.
- **State**: The `isRecording` state turns `true`, visual feedback appears.

### 2. Submission & Upload
- **User Action**: User clicks "Stop".
- **File**: `frontend/app/page.tsx` -> `analyzeAudio` function.
- **Logic**:
  - The recorded audio chunks are compiled into a `Blob`.
  - A `FormData` object is created containing this blob.
  - A `POST` request is sent to `${BASE_URL}/analyze` (typically `http://localhost:8000/analyze` or the production URL).

### 3. API Entry Point (Backend)
- **File**: `backend/main.py`
- **Endpoint**: `@app.post("/analyze")`
- **Logic**:
  - Receives the `UploadFile`.
  - Saves the raw audio file temporarily to `/tmp/`.
  - **Crucial Step**: Calls `convert_to_google_format` to sanitize the audio.

### 4. Audio Processing
- **File**: `backend/convert_audio.py`
- **Logic**:
  - Reads the raw input audio.
  - Resamples it to **16,000 Hz** (optimal for Speech-to-Text).
  - Converts stereo to **Mono** (single channel).
  - Ensures the format is **16-bit PCM WAV**.
  - Saves the cleaned file to a new temp path.

### 5. Core Analysis (Evaluation Engine)
- **File**: `evaluation_engine/stt_api_key.py`
- **Function**: `analyze_audio_with_api_key`
- **Logic**:
  - **Transcription**: Sends the clean audio to **Google Cloud Speech-to-Text API** via HTTP (`requests`).
    - *Note*: It asks for word-level timestamps (`enableWordTimeOffsets: True`).
  - **Metric Calculation**: The `analyze_fluency` function processes the word timings:
    - **WPM**: (Total Words / Duration) * 60.
    - **Fillers**: Counts occurrences of "um", "uh", "like", etc.
    - **Pauses**: Identifies gaps between words > 0.8s (pause) or > 1.5s (long pause).
    - **Score**: A heuristic 0-5.0 score based on these metrics.

### 6. Response & Display
- **Backend Response**: Returns a JSON object:
  ```json
  {
    "transcript": "Hello world...",
    "fluency_metrics": {
      "wpm": 135.5,
      "fluency_score": 4.5,
      ...
    }
  }
  ```
- **Frontend Display**: 
  - `frontend/app/page.tsx` receives the JSON.
  - Updates `metrics` state.
  - Passes data to `MetricsCard` components to animate the results.
  - Displays the transcript text.

---

## 📂 Key Files Comparison

| File | Purpose | Key Functions |
|------|---------|---------------|
| `frontend/app/page.tsx` | Main UI Page | `startRecording`, `analyzeAudio`, Render Logic |
| `frontend/lib/api.ts` | Config | Defines `BASE_URL` for API connection |
| `backend/main.py` | API Server | `/analyze` route handler, CORS setup |
| `backend/convert_audio.py` | Audio Utility | `convert_to_google_format` (Standardizes audio) |
| `evaluation_engine/stt_api_key.py` | Core Logic | `recognize_speech_with_api_key`, `analyze_fluency` |

---

## 🛠️ How to Trace Issues

- **If Microphone Fails**: Check `frontend/app/page.tsx` -> `startRecording`. Look for browser permission errors or standard `MediaRecorder` issues vs `extendable-media-recorder`.
- **If "RIFF Header" Error**: This means the audio format sent to Python was wrong. The `convert_audio.py` script usually handles this, but if the upload itself is corrupt, check the frontend blob creation.
- **If Scoring seems wrong**: Check `evaluation_engine/stt_api_key.py` -> `analyze_fluency`. You can tweak the thresholds for pauses (0.8s) or WPM (120-150 range) there.
