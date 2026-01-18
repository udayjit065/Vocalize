# 🛠️ Vocalize Development & Debugging Log (Personal Reference)

## 📅 Date: January 18, 2026
**Status:** ✅ SUCCEEDED - Application is fully deployed and functional on Vercel.

---

## 🎯 The Journey
We faced several complex challenges deploying this monorepo (Next.js + Python Backend) to Vercel. Here is exactly what went wrong and how we fixed it.

### 1. 🏗️ The "Next.js Not Detected" Infinite Loop
**The Problem:**
Vercel's build system couldn't find the Next.js app because it was nested in `/frontend` and the root `package.json` was missing or misconfigured. This caused Vercel to try and build the root recursively, leading to infinite loops.

**The Fix:**
- Created a **root `package.json`** with `workspaces: ["frontend"]`.
- Added a specific build script: `"build": "npm run build --workspace=frontend"`.
- This told Vercel exactly where to look and how to build.

### 2. 🐍 Python Backend Deployment (Rewrites vs. Native)
**The Problem:**
We initially tried to keep the Python code in a pure `backend/` folder and use `rewrites` in `vercel.json` to map `/api/*` to it. This failed repeatedly with 404s and 405s because Vercel Serverless Functions have strict location requirements.

**The Fix:**
- Moved the Python API **inside** the Next.js structure: `frontend/api/`.
- Renamed `main.py` directly to the Vercel convention: `frontend/api/[[...slug]].py`.
- This let Vercel handle the routing naturally without complex `rewrites` configuration.

### 3. 🔐 Google Auth & Environment Variables
**The Problem:**
Using the Google Service Account JSON (`GOOGLE_APPLICATION_CREDENTIALS_JSON`) was unstable in the serverless environment due to file path parsing issues.

**The Fix:**
- Switched to using `GOOGLE_API_KEY` only.
- Simplified the backend logic to rely solely on the API Key method for `google-cloud-speech` where possible, or passed credentials directly from the env var without expecting a file on disk.

### 4. 📂 Read-Only File System Error
**The Problem:**
The Python backend tries to save uploaded audio files to disk before processing. Vercel Serverless environment is **Read-Only** except for `/tmp`.
*Error:* `OSError: [Errno 30] Read-only file system`

**The Fix:**
- Updated all file operations to explicitly use `/tmp/` directory.
```python
upload_path = f"/tmp/temp_upload_{file.filename}"
converted_path = f"/tmp/temp_converted_{file.filename}.wav"
```

### 5. 🔊 The "RIFF Header" Crash (Format Mismatch)
**The Problem:**
The frontend uses the browser's `MediaRecorder`. By default on Chrome, this records in **WebM** format.
The Python backend uses `wave.open()`, which **only** reads **WAV (RIFF)** files.
*Error:* `wave.Error: file does not start with RIFF id`

**The Fix:**
- Instead of installing heavy `ffmpeg` on the lightweight serverless backend, we fixed it at the source.
- Modified `frontend/app/page.tsx` to **force** the use of `extendable-media-recorder` (which encodes to WAV).
- Logic changed to prioritize WAV over the browser's native WebM recorder.

---

## 🔑 Key Configurations

#### Frontend `vercel.json`
Kept it minimal to let Vercel do its magic:
```json
{
  "version": 2
}
```

#### Frontend `next.config.js`
Moved the rewrite rule here for cleaner Next.js integration:
```js
async rewrites() {
  return [
    {
      source: "/api/:path*",
      destination: "/api/:path*",
    },
  ];
},
```

---

## 🚀 Final Status
- **URL:** https://vocalize-demo.vercel.app
- **Tests:** Confirmed working with live microphone recording.
- **Result:** Captures audio -> Uploads WAV -> Google STT Analysis -> Returns Fluency Score & WPM.
