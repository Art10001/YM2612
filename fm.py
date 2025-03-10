import numpy as np
import wave
import struct
import pygame
import math

class FMSynthesizer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.operators = [
            {'frequency': 0, 'amplitude': 0, 'phase': 0, 'envelope': self._create_envelope()},
            {'frequency': 0, 'amplitude': 0, 'phase': 0, 'envelope': self._create_envelope()}
        ]
        pygame.init()
        pygame.mixer.init()

    def _create_envelope(self):
        # Simple ADSR envelope
        return {
            'attack': 0.1,   # Attack time
            'decay': 0.1,    # Decay time
            'sustain': 0.7,  # Sustain level
            'release': 0.2   # Release time
        }

    def _generate_sine_wave(self, frequency, duration, amplitude=1.0, modulation=0):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Basic FM synthesis with two operators
        carrier = amplitude * np.sin(2 * np.pi * frequency * t + 
                                     modulation * np.sin(2 * np.pi * (frequency * 2) * t))
        
        return carrier

    def _apply_envelope(self, signal, duration):
        # Simple envelope application
        attack_samples = int(self.sample_rate * 0.1)
        decay_samples = int(self.sample_rate * 0.1)
        release_samples = int(self.sample_rate * 0.2)
        sustain_samples = len(signal) - attack_samples - decay_samples - release_samples

        envelope = np.ones_like(signal)
        
        # Attack phase
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, 0.7, decay_samples)
        
        # Sustain phase
        
        # Release phase
        envelope[-release_samples:] = np.linspace(0.7, 0, release_samples)
        
        return signal * envelope

    def generate_note(self, frequency, duration, note_type='sine'):
        # Generate audio based on frequency and duration
        if note_type == 'sine':
            # Basic FM synthesis
            modulation_index = 2  # Can be adjusted
            signal = self._generate_sine_wave(frequency, duration, modulation=modulation_index)
            signal = self._apply_envelope(signal, duration)
            return signal

    def write_wav(self, filename, signals):
        # Combine and write signals to WAV file
        combined_signal = np.concatenate(signals)
        
        # Normalize
        combined_signal = combined_signal / np.max(np.abs(combined_signal))
        
        # Convert to 16-bit PCM
        scaled = np.int16(combined_signal * 32767)
        
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(scaled.tobytes())

    def note_to_frequency(self, note):
        # Convert note name to frequency
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = int(note[-1])
        note_name = note[:-1]
        note_index = notes.index(note_name)
        return 440 * (2 ** ((note_index - 9) / 12 + (octave - 4)))

def main():
    synth = FMSynthesizer()
    
    # Example note sequence
    note_sequence = [
        ('C4', 0.5),   # Note, Duration
        ('E4', 0.5),
        ('G4', 0.5),
        ('C5', 1.0)
    ]
    
    # Generate signals for each note
    signals = []
    for note, duration in note_sequence:
        frequency = synth.note_to_frequency(note)
        signal = synth.generate_note(frequency, duration)
        signals.append(signal)
    
    # Write to WAV file
    synth.write_wav('fm_synth_output.wav', signals)
    print("WAV file generated: fm_synth_output.wav")

if __name__ == "__main__":
    main()
