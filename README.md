# Vocalize | Professional Speech Analysis

Vocalize is an enterprise-grade speech analysis platform that provides real-time fluency scoring, words-per-minute (WPM) tracking, and high-fidelity transcription.

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd TTS

# Install Python backend dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure API Key
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_cloud_stt_api_key
```

### 3. Run the Application

#### **Backend (FastAPI)**
```bash
python -m uvicorn backend.main:app --reload
```

#### **Frontend (Next.js)**
```bash
cd frontend
npm run dev
```
Visit [http://localhost:3000](http://localhost:3000) to start analyzing.

---

## 🛠 Features

- **Real-time Recording**: Capture high-quality audio directly from the browser.
- **Fluency Scoring**: Automated algorithm to evaluate speech flow and pace.
- **WPM Analytics**: Instant calculation of communication velocity.
- **Minimalist UI**: Clean, Notion-inspired monochrome interface for a professional demo experience.
- **Auto-Conversion**: Built-in audio processing to ensure compatibility with Google Cloud STT.

---

## 📂 Project Structure

- `frontend/`: Next.js 14 web application.
- `backend/`: FastAPI server for audio processing.
- `evaluation_engine/`: Core logic for speech-to-text and fluency metrics.
- `recordings/`: Temporary storage for processed audio.

---

## 📝 CLI Tools

- `record_live.py`: Record and analyze directly from the terminal.
- `simple_test.py`: Test the pipeline with pre-recorded audio files.

---

## 🌐 Deployment

### Vercel (Frontend)
The frontend is optimized for Vercel. Connect your Github repository and ensure the `ROOT` is set to the `frontend` folder or use the default root if deploying the monorepo logic.

### Backend
Deploy the FastAPI backend to services like Heroku, Render, or Railway. Ensure the `GOOGLE_API_KEY` environment variable is set in your production environment.
# Vocalize
