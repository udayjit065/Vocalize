# Deployment Troubleshooting & History

This document chronicles the challenges faced during the deployment of the Vocalize application, specifically focusing on the Monorepo structure (Next.js + FastAPI) and the critical audio processing pipeline.

## 🎯 The Objective
Deploy a **Monorepo** containing:
1.  **Frontend**: Next.js 14 on Vercel.
2.  **Backend**: FastAPI (originally attempted on Koyeb, then Vercel Serverless).
3.  **Requirement**: Real-time audio analysis with high-fidelity inputs.

---

## 🚩 Core Issue 1: "RIFF Header" Error

### The Symptom
When the backend received audio, it crashed with:
```
wave.Error: file does not start with RIFF id
```
This error indicates that the Python `wave` module tried to read a file that it *thought* was a WAV file, but the internal header was missing or incorrect (likely a WebM or compromised binary).

### 🔍 How We Troubleshot It
1.  **Log Analysis**: We checked the backend logs.
    - *Observation*: The file size was non-zero (audio was arriving).
    - *Observation*: The error happened immediately at `wave.open()`.
2.  **Hypothesis**: The frontend `MediaRecorder` defaults to `audio/webm` on Chrome/Vercel environments, even if we requested `audio/wav`. Browsers often ignore the mimeType request if they don't natively support encoding it.
3.  **Verification**: We inspected the blob sent from the client. It was indeed WebM in many cases.

### ✅ The Solution (Point-Wise)
1.  **Frontend Enforcer**: We installed `extendable-media-recorder` and `extendable-media-recorder-wav-encoder`.
    - *Why?* Standard `MediaRecorder` is unreliable for format strictness. This library uses WebAssembly to *force* actual WAV encoding in the browser before upload.
2.  **Backend Robustness**: We updated `convert_audio.py` to be strictly for "Sanitization".
    - It now assumes it *should* get a WAV, but if we wanted to be safer in the future, we would add a step to convert *any* ffmpeg-readable format to WAV. Currently, the frontend fix solved the root cause.

---

## 🚩 Core Issue 2: Environment & CORS

### The Symptom
- "Network Error" on the frontend.
- Backend logs showing successful health checks but failed analysis requests.

### 🔍 How We Troubleshot It
1.  **Inspection**: We saw the frontend was calling `localhost:8000` even when deployed to Vercel production.
2.  **Root Cause**: Hardcoded API URLs.

### ✅ The Solution
1.  **Dynamic Config**: Created `frontend/lib/api.ts`:
    ```typescript
    export const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    ```
2.  **CORS Configuration**: Updated `backend/main.py` to explicitly allow the Vercel production domain (`https://vocalize-demo.vercel.app`) to prevent cross-origin blocking.

---

## 🚀 Summary of the "Correct Way"

To avoid these issues in the future, here is the established protocol:

1.  **Audio Formats**: Never trust the browser's default `MediaRecorder`. Always use a polyfill/encoder (like `extendable-media-recorder`) if the backend requires a specific header format like WAV.
2.  **Environment Variables**: Never hardcode URLs. Use a central config file (`api.ts`) that reads from `process.env`.
3.  **Monorepo Deployment**: Ensure the "Root Directory" in Vercel is set correctly (e.g., `frontend` folder) so it builds the correct `package.json`.
