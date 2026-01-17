"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Mic, 
  Square, 
  Loader2, 
  Activity, 
  ShieldCheck, 
  Clock, 
  MessageSquare,
  BarChart3,
  CheckCircle2
} from "lucide-react";
import { MetricsCard } from "./components/MetricsCard";
import { cn } from "@/lib/utils";

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState<"idle" | "listening" | "processing">("idle");
  
  const [mounted, setMounted] = useState(false);
  
  const mediaRecorderRef = useRef<any>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const librariesLoaded = useRef(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Set mounted state
  useEffect(() => {
    setMounted(true);
  }, []);

  // Initialize WAV encoder on client side
  useEffect(() => {
    if (!mounted) return;
    const initEncoder = async () => {
      if (typeof window === 'undefined' || librariesLoaded.current) return;
      try {
        const { register } = await import('extendable-media-recorder');
        const { connect } = await import('extendable-media-recorder-wav-encoder');
        await register(await connect());
        librariesLoaded.current = true;
      } catch (e) {
        console.log("Encoder initialization:", e);
      }
    };
    initEncoder();
  }, [mounted]);

  // Timer logic
  useEffect(() => {
    if (!mounted) return;
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
      if (!analyzing) setRecordingTime(0);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [isRecording, analyzing, mounted]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const { MediaRecorder } = await import('extendable-media-recorder');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/wav' });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e: any) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });
        await analyzeAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setStatus("listening");
      setResult(null);
    } catch (err) {
      console.error("Error accessing microphone:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setStatus("processing");
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach((track: any) => track.stop());
      }
    }
  };

  const analyzeAudio = async (audioBlob: Blob) => {
    setAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "recording.wav");

      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setAnalyzing(false);
      setStatus("idle");
    }
  };

  if (!mounted) return <div className="min-h-screen bg-white" />;

  return (
    <main className="min-h-screen bg-white text-black font-sans selection:bg-gray-200 overflow-x-hidden">
      <div className="max-w-4xl mx-auto px-6 py-12 lg:py-16">
        
        {/* Header */}
        <nav className="flex items-center justify-between mb-12 border-b border-gray-100 pb-8">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/20 flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-800">Vocalize</h1>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 rounded border border-gray-200 bg-gray-50">
            <ShieldCheck className="w-3.5 h-3.5 text-gray-400" />
            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Secure</span>
          </div>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          
          {/* Left Column: Control */}
          <div className="lg:col-span-4 space-y-8">
            <section className="space-y-6">
              <header>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Control</span>
                  {status !== 'idle' && (
                    <span className="text-[9px] font-bold uppercase text-black italic animate-pulse">{status}...</span>
                  )}
                </div>
              </header>

              <div className="flex flex-col items-center">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={analyzing}
                  className={cn(
                    "w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 border-2",
                    isRecording 
                      ? "bg-black text-white border-black scale-110" 
                      : "bg-white text-black border-gray-200 hover:border-black"
                  )}
                >
                  {isRecording ? (
                    <Square className="w-6 h-6 fill-current" />
                  ) : (
                    <Mic className="w-6 h-6" />
                  )}
                </button>

                <div className="mt-6 flex flex-col items-center gap-1">
                  <div className="text-3xl font-mono font-medium tracking-tight">
                    {formatTime(recordingTime)}
                  </div>
                  <p className="text-[10px] uppercase tracking-widest font-bold text-gray-400">Duration</p>
                </div>
              </div>
            </section>

            <div className="pt-8 border-t border-gray-100 space-y-4">
              <h4 className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Directives</h4>
              <ul className="space-y-3">
                {[
                  "Maintain steady pace",
                  "Speak clearly",
                  "Avoid filler words"
                ].map((text, i) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-gray-600">
                    <div className="w-1 h-1 rounded-full bg-black/20" />
                    {text}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* Analytics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <MetricsCard 
                label="Fluency Score"
                value={result?.fluency_metrics?.fluency_score || "0.0"}
                unit="/ 5.0"
                loading={analyzing}
              />
              <MetricsCard 
                label="WPM"
                value={Math.round(result?.fluency_metrics?.wpm || 0)}
                unit="Words/Min"
                loading={analyzing}
                delay={0.1}
              />
            </div>

            {/* Transcript Area */}
            <section className="border border-gray-100 rounded-lg overflow-hidden flex flex-col bg-white">
              <header className="px-6 py-4 border-b border-gray-100 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-gray-400" />
                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Transcript</span>
              </header>
              
              <div className="min-h-[300px] p-8">
                {!result && !analyzing && !isRecording && (
                    <div className="h-full flex flex-col items-center justify-center text-center opacity-20 py-12">
                        <p className="text-xs uppercase tracking-[0.2em]">Ready for input</p>
                    </div>
                )}

                {isRecording && (
                   <div className="flex items-center gap-2 text-gray-400 italic text-xs">
                     <span className="animate-pulse">●</span>
                     <span>Recording session...</span>
                   </div>
                )}

                {analyzing && (
                  <div className="space-y-4 opacity-10">
                     <div className="h-3 bg-black rounded w-3/4" />
                     <div className="h-3 bg-black rounded w-1/2" />
                     <div className="h-3 bg-black rounded w-2/3" />
                  </div>
                )}

                {result && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-4"
                  >
                    <p className="text-lg leading-relaxed text-black/80">
                      {result.transcript || "No speech detected."}
                    </p>
                  </motion.div>
                )}
              </div>
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
