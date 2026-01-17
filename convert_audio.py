"""Audio converter - Converts to 16000Hz mono WAV"""
import scipy.io.wavfile as wav
import numpy as np
import os

def convert_to_google_format(input_file, output_file=None):
    """Convert audio to Google-compatible format"""
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_converted{ext}"
    
    print(f"Loading: {input_file}")
    
    # Read WAV file
    rate, data = wav.read(input_file)
    print(f"   {rate}Hz, {data.shape}")
    
    # Convert to mono
    if len(data.shape) > 1 and data.shape[1] > 1:
        data = np.mean(data, axis=1)
    
    # Resample to 16000Hz
    if rate != 16000:
        num_samples = int(len(data) * 16000 / rate)
        data = np.interp(
            np.linspace(0, len(data), num_samples),
            np.arange(len(data)),
            data
        )
        rate = 16000
    
    # Convert to int16
    if data.dtype != np.int16:
        data = np.int16(data / np.max(np.abs(data)) * 32767)
    
    # Save
    wav.write(output_file, rate, data)
    print(f"Saved: {output_file}\n")
    
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        convert_to_google_format(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("Usage: python convert_audio.py input.wav [output.wav]")
