import os
import wave
import struct
import math

def generate_chime(filepath: str, frequency: float = 440.0, duration: float = 1.5, sample_rate: int = 22050):
    """
    Generates a simple, clean, decaying sine wave chime sound and saves it as a WAV file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Calculate audio parameters
    num_samples = int(sample_rate * duration)
    
    with wave.open(filepath, 'wb') as wav_file:
        # 1 channel (mono), 2 bytes per sample (16-bit), sample_rate, num_samples
        wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
        
        for i in range(num_samples):
            # Time elapsed
            t = float(i) / sample_rate
            
            # Simple chime envelope (fast attack, exponential decay)
            envelope = math.exp(-3.0 * t)
            
            # Create a nice complex chime-like harmonic sound (fundamental + 3rd and 5th harmonics)
            value = (
                1.0 * math.sin(2.0 * math.pi * frequency * t) +
                0.5 * math.sin(2.0 * math.pi * (frequency * 1.5) * t) +
                0.25 * math.sin(2.0 * math.pi * (frequency * 2.0) * t)
            )
            
            # Normalize and scale
            scaled_value = int(value * envelope * 16383.0)
            
            # Ensure it fits within 16-bit signed integer limits
            scaled_value = max(-32768, min(32767, scaled_value))
            
            # Pack as 16-bit little-endian signed integer
            data = struct.pack('<h', scaled_value)
            wav_file.writeframesraw(data)
            
    print(f"Generated chime WAV at {filepath}")

def main():
    samples_dir = "/Users/macbookair/Desktop/call-intelligence/samples"
    
    # Generate 5 different chimes for our presets, each with a slightly different pitch
    presets = {
        "promise_to_pay.wav": 523.25,      # C5 (Bright, positive)
        "refuse_to_pay.wav": 349.23,       # F4 (Dissonant, lower)
        "excuse_delay.wav": 392.00,        # G4 (Neutral, inquiring)
        "partial_pay.wav": 440.00,         # A4 (Constructive, middle)
        "no_response.wav": 293.66          # D4 (Flat, unsure)
    }
    
    for filename, freq in presets.items():
        path = os.path.join(samples_dir, filename)
        generate_chime(path, frequency=freq)

if __name__ == "__main__":
    main()
