# 📘 Vercel Deployment & Architecture Guide

**Project:** Vocalize - AI Speech Fluency Analyzer
**Deployed URL:** [https://vocalize-demo.vercel.app](https://vocalize-demo.vercel.app)

---

## 🏗️ Architecture Overview

This project is deployed as a **Monorepo** on Vercel, combining a Next.js frontend with a Python Serverless backend.

```mermaid
graph TD
    Client[Browser Frontend] -->|Records WAV Audio| NextJS[Next.js App]
    NextJS -->|POST /api/analyze| VercelFn[Vercel Serverless Function (Python)]
    VercelFn -->|Google Speech API| GoogleCloud[Google Cloud Platform]
    VercelFn -->|JSON Result| Client
```

### Technology Stack
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Framer Motion.
- **Backend:** Python 3.12 (Serverless), FastAPI, Google Cloud Speech-to-Text.
- **Deployment:** Vercel (Hybrid Next.js + Python runtime).

---

## ⚙️ Configuration Details

### 1. Directory Structure
To ensure Vercel correctly detects both the frontend and the Python functions, we utilize the following structure:

```
TTS/ (Root)
├── package.json          # Defines workspace
├── frontend/             # Next.js Application
│   ├── app/
│   ├── api/              # Python Serverless Functions
│   │   ├── [[...slug]].py  # Main Entry Point (FastAPI)
│   │   ├── ...
│   └── package.json
└── docs/
```

### 2. File Routing
- The Python API is located at `frontend/api/`.
- Vercel automatically treats files in `api/` as serverless functions.
- We use a catch-all route `[[...slug]].py` to allow FastAPI to handle all `/api/*` sub-routes (e.g., `/api/analyze`, `/api/health`).

### 3. Audio Processing Pipeline
1.  **Recording:** The frontend enforces **WAV** format recording using `extendable-media-recorder` (WAV Encoder).
2.  **Upload:** Audio is sent via `multipart/form-data` to `/api/analyze`.
3.  **Processing:** 
    - The Python function saves the file momentarily to `/tmp/`.
    - It verifies the RIFF header.
    - Sends the audio to Google Speech-to-Text API.
    - Calculates WPM (Words Per Minute) and Fluency Score.
4.  **Response:** Returns a JSON object with the analysis metrics.

---

## 🚀 Deployment Instructions

### Prerequisites
- Vercel CLI or GitHub Integration.
- Google Cloud API Key with **Speech-to-Text API** enabled.

### Environment Variables
The following environment variables must be configured in Vercel:

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | API Key for Google Cloud Speech services. |
| `NEXT_PUBLIC_API_URL` | Base URL for API calls (e.g., `/api`). |

### How to Deploy
1.  **Push to GitHub:**
    ```bash
    git push origin main
    ```
2.  **Vercel Dashboard:**
    - Import the repository.
    - **Root Directory:** Leave as root (`./`).
    - **Framework Preset:** Next.js.
    - **Build Command:** Vercel will auto-detect configurations from the root `package.json`.

---

## 🩺 Monitoring & Debugging

Two dedicated endpoints are available for health checks:
- **`https://.../api/health`**: Returns `{"status": "healthy"}` and confirms API key loading.
- **`https://.../api/debug`**: Returns Python version and environment details (safe information only).

---

**Last Updated:** January 18, 2026
