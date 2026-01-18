"""
Audio utilities for SatyaDrishti application.
Generates emergency siren sounds.
"""

import numpy as np
import io
import scipy.io.wavfile as wav


def generate_high_pitch_siren(duration=1.5):
    """Generate a high pitch siren sound for emergency alerts."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # High pitch modulation: 1200Hz to 2000Hz
    # Fast modulation for urgency
    modulator = 800 * np.sin(2 * np.pi * 8 * t) 
    carrier = np.sin(2 * np.pi * (1600 + modulator) * t)
    
    # Normalize (0.5 volume to prevent clipping)
    audio_data = np.int16(carrier * 32767 * 0.5)
    
    virtual_file = io.BytesIO()
    wav.write(virtual_file, sample_rate, audio_data)
    return virtual_file
