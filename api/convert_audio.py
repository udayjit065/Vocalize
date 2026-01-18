"""Audio converter - Converts to 16000Hz mono WAV
Optimized for Vercel: Uses built-in wave module instead of scipy (~130MB saved)
"""
import wave
import struct
import os

def convert_to_google_format(input_file, output_file=None):
    """Convert audio to Google-compatible format (16000Hz mono WAV)"""
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_converted{ext}"
    
    print(f"Loading: {input_file}")
    
    # Read WAV file using built-in wave module
    with wave.open(input_file, 'rb') as wav_in:
        n_channels = wav_in.getnchannels()
        sample_width = wav_in.getsampwidth()
        rate = wav_in.getframerate()
        n_frames = wav_in.getnframes()
        
        # Read raw audio data
        raw_data = wav_in.readframes(n_frames)
    
    print(f"   {rate}Hz, channels={n_channels}, frames={n_frames}")
    
    # Determine format string based on sample width
    if sample_width == 1:
        fmt = f"{n_frames * n_channels}b"  # 8-bit signed
    elif sample_width == 2:
        fmt = f"{n_frames * n_channels}h"  # 16-bit signed
    elif sample_width == 4:
        fmt = f"{n_frames * n_channels}i"  # 32-bit signed
    else:
        raise ValueError(f"Unsupported sample width: {sample_width}")
    
    # Unpack raw bytes to integers
    samples = list(struct.unpack(fmt, raw_data))
    
    # Convert to mono by averaging channels
    if n_channels > 1:
        mono_samples = []
        for i in range(0, len(samples), n_channels):
            avg = sum(samples[i:i + n_channels]) // n_channels
            mono_samples.append(avg)
        samples = mono_samples
    
    # Resample to 16000Hz using linear interpolation
    if rate != 16000:
        original_length = len(samples)
        new_length = int(original_length * 16000 / rate)
        resampled = []
        
        for i in range(new_length):
            # Calculate position in original array
            pos = i * (original_length - 1) / (new_length - 1) if new_length > 1 else 0
            idx = int(pos)
            frac = pos - idx
            
            # Linear interpolation
            if idx + 1 < original_length:
                val = samples[idx] * (1 - frac) + samples[idx + 1] * frac
            else:
                val = samples[idx]
            resampled.append(int(val))
        
        samples = resampled
        rate = 16000
    
    # Normalize to 16-bit range if needed
    if sample_width != 2:
        max_val = max(abs(s) for s in samples) if samples else 1
        if max_val > 0:
            scale = 32767 / max_val
            samples = [int(s * scale) for s in samples]
    
    # Clamp values to int16 range
    samples = [max(-32768, min(32767, s)) for s in samples]
    
    # Write output WAV file
    with wave.open(output_file, 'wb') as wav_out:
        wav_out.setnchannels(1)  # Mono
        wav_out.setsampwidth(2)  # 16-bit
        wav_out.setframerate(16000)
        
        # Pack samples as 16-bit signed integers
        packed = struct.pack(f"{len(samples)}h", *samples)
        wav_out.writeframes(packed)
    
    print(f"Saved: {output_file}\n")
    return output_file

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        convert_to_google_format(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("Usage: python convert_audio.py input.wav [output.wav]")
