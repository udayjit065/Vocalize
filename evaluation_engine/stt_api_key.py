"""Google STT + Fluency Analysis"""
import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()

def analyze_fluency(words):
    """Compute fluency metrics from word timings"""
    if not words:
        return {"fluency_score": 0, "error": "No words"}
        
    fillers = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'so']
    filler_count = sum(1 for w in words if w['word'].lower() in fillers)
    
    # Calculate Gaps (Pauses)
    pause_count = 0
    long_pauses = 0
    for i in range(1, len(words)):
        gap = float(words[i]['startTime']) - float(words[i-1]['endTime'])
        if gap > 0.8:
            pause_count += 1
        if gap > 1.5:
            long_pauses += 1

    duration = float(words[-1]['endTime']) - float(words[0]['startTime'])
    wpm = (len(words) / duration) * 60 if duration > 0 else 0
    
    # 0-5 Scoring
    score = 5.0
    if wpm < 120 or wpm > 150: 
        score -= 1.0
    if (filler_count / len(words)) > 0.10: 
        score -= 1.0
    score -= (long_pauses * 0.5)

    return {
        "wpm": round(wpm, 1),
        "avg_word_time": round(duration / len(words), 2),
        "filler_rate": round(filler_count / len(words), 2),
        "pause_frequency": round(pause_count / len(words), 2),
        "long_pauses": long_pauses,
        "fluency_score": max(0, round(score, 1))
    }


def recognize_speech_with_api_key(audio_file_path, api_key, language_code="en-US"):
    """Google Speech-to-Text API call"""
    try:
        # Read and encode
        with open(audio_file_path, 'rb') as audio_file:
            audio_content = audio_file.read()
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
        headers = {"Content-Type": "application/json"}
        # Auto-detect: English primary, Punjabi/Hindi alternatives
        if language_code == "auto":
            config_data = {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": "en-US", 
                "alternativeLanguageCodes": ["pa-IN", "hi-IN"],
                "enableWordTimeOffsets": True,
                "enableAutomaticPunctuation": True
            }
        else:
            config_data = {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": language_code,
                "enableWordTimeOffsets": True,
                "enableAutomaticPunctuation": True
            }
        
        data = {
            "config": config_data,
            "audio": {
                "content": audio_base64
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            return {
                "error": f"API request failed: {response.status_code}",
                "details": response.text
            }
        
        result = response.json()
        
        if 'results' not in result or not result['results']:
            return {"error": "No transcription results returned"}
        
        # Process results
        processed_words = []
        full_transcript = ""
        
        for res in result['results']:
            if 'alternatives' in res and res['alternatives']:
                alternative = res['alternatives'][0]
                full_transcript += alternative.get('transcript', '') + " "
                
                # Extract word timings
                if 'words' in alternative:
                    for word_info in alternative['words']:
                        start_time = float(word_info.get('startTime', '0s').replace('s', ''))
                        end_time = float(word_info.get('endTime', '0s').replace('s', ''))
                        
                        processed_words.append({
                            "word": word_info.get('word', ''),
                            "startTime": start_time,
                            "endTime": end_time
                        })
        
        print(f"✅ Transcription complete: {len(processed_words)} words detected")
        
        return {
            "transcript": full_transcript.strip(),
            "words": processed_words,
            "word_count": len(processed_words)
        }
    
    except Exception as e:
        return {"error": f"Speech recognition failed: {str(e)}"}


def analyze_audio_with_api_key(audio_file_path, api_key, language_code="en-US"):
    """
    Complete pipeline: Audio → Speech Recognition → Fluency Analysis
    Uses API key authentication
    
    Args:
        audio_file_path: Path to audio file
        api_key: Your Google Cloud API key
        language_code: Language code (default: "en-US")
    
    Returns:
        dict with transcript, words, and fluency metrics
    """
    # Step 1: Recognize speech
    speech_result = recognize_speech_with_api_key(audio_file_path, api_key, language_code)
    
    if "error" in speech_result:
        return speech_result
    
    # Step 2: Analyze fluency
    fluency_metrics = analyze_fluency(speech_result['words'])
    
    # Step 3: Combine results
    return {
        "transcript": speech_result['transcript'],
        "word_count": speech_result['word_count'],
        "words": speech_result['words'],
        "fluency_metrics": fluency_metrics
    }


# Demo with sample data (for testing without API call)
if __name__ == "__main__":
    import json
    
    def print_header(text):
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70)
    
    def print_metrics_table(metrics):
        """Print metrics in a clean table format"""
        print("\n  📊 FLUENCY ANALYSIS RESULTS")
        print("  " + "─"*66)
        print(f"  │ {'Metric':<30} │ {'Value':<15} │ {'Status':<15} │")
        print("  " + "─"*66)
        
        # WPM
        wpm_status = "✓ Optimal" if 120 <= metrics['wpm'] <= 150 else "⚠ Review"
        print(f"  │ {'Words Per Minute (WPM)':<30} │ {metrics['wpm']:<15.1f} │ {wpm_status:<15} │")
        
        # Filler rate
        filler_status = "✓ Good" if metrics['filler_rate'] <= 0.10 else "⚠ High"
        print(f"  │ {'Filler Word Rate':<30} │ {metrics['filler_rate']*100:<15.1f}% │ {filler_status:<15} │")
        
        # Long pauses
        pause_status = "✓ Good" if metrics['long_pauses'] == 0 else "⚠ Review"
        print(f"  │ {'Long Pauses (>1.5s)':<30} │ {metrics['long_pauses']:<15} │ {pause_status:<15} │")
        
        print("  " + "─"*66)
        
        # Overall score
        score = metrics['fluency_score']
        stars = "⭐" * int(score)
        if score >= 4.5:
            status = " EXCELLENT"
        elif score >= 3.5:
            status = " GOOD"
        elif score >= 2.5:
            status = "FAIR"
        else:
            status = " NEEDS WORK"
        
        print(f"\n  🎯 OVERALL FLUENCY SCORE: {score:.1f}/5.0 {stars}")
        print(f"  Assessment: {status}\n")
    
    # Get API key from environment
    API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")
    
    print_header("GOOGLE SPEECH-TO-TEXT (API KEY METHOD)")
    print("  🔑 Using REST API with API Key Authentication\n")
    
    # Test with sample data (no API call)
    print_header("DEMO: Testing with Sample Data")
    
    sample_words = [
        {"word": "I", "startTime": 0.1, "endTime": 0.2},
        {"word": "believe", "startTime": 0.3, "endTime": 0.6},
        {"word": "the", "startTime": 0.7, "endTime": 0.9},
        {"word": "market", "startTime": 1.0, "endTime": 1.4},
        {"word": "is", "startTime": 1.5, "endTime": 1.6},
        {"word": "growing", "startTime": 1.7, "endTime": 2.2}
    ]
    
    sample_transcript = " ".join([w["word"] for w in sample_words])
    print(f"\n  📝 Sample Transcript: \"{sample_transcript}\"")
    print(f"  ⏱️  Duration: {sample_words[-1]['endTime']:.1f} seconds")
    
    metrics = analyze_fluency(sample_words)
    print_metrics_table(metrics)
    
    print_header("Ready for Real Audio Analysis")
    print("  ✓ Set API key: $env:GOOGLE_API_KEY=\"your-api-key\"")
    print("  ✓ Run: python stt_api_key.py")
    print("  ✓ Or import: from stt_api_key import analyze_audio_with_api_key\n")
