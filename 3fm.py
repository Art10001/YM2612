import numpy as np
import wave
import pygame
from pygame.locals import *

class RealTimeFMSynth:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.notes = {}
        self.recorded_notes = []
        self.key_to_note = {
            K_a: 'C4', K_w: 'C#4', K_s: 'D4', K_e: 'D#4',
            K_d: 'E4', K_f: 'F4', K_t: 'F#4', K_g: 'G4',
            K_y: 'G#4', K_h: 'A4', K_u: 'A#4', K_j: 'B4',
            K_k: 'C5'
        }
        self.running = True
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((300, 100))
        pygame.display.set_caption("FM Synth - Press ESC to quit")

    def note_to_freq(self, note):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = int(note[-1])
        note_name = note[:-1]
        semitone = notes.index(note_name) + (octave - 4) * 12
        return 444 * (2 ** (semitone / 12))

    def fm_operator(self, freq, ratio, index, phase, mod_phase):
        """FM operator with phase modulation"""
        carrier = np.sin(2 * np.pi * freq * phase + 
                        index * np.sin(2 * np.pi * freq * ratio * mod_phase))
        return carrier

    def generate_note(self, freq, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        envelope = self.adsr_envelope(len(t))
        
        # 2-operator FM synthesis
        mod_ratio = 3.0
        mod_index = 2.0
        mod_phase = t * 0.5  # Different phase offset
        
        carrier = self.fm_operator(freq, mod_ratio, mod_index, t, mod_phase)
        return carrier * envelope

    def adsr_envelope(self, length):
        attack = int(0.1 * length)
        decay = int(0.2 * length)
        sustain_level = 0.6
        release = int(0.3 * length)
        sustain = length - (attack + decay + release)
        
        envelope = np.zeros(length)
        # Attack
        envelope[:attack] = np.linspace(0, 1, attack)
        # Decay
        envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
        # Sustain
        envelope[attack+decay:-release] = sustain_level
        # Release
        envelope[-release:] = np.linspace(sustain_level, 0, release)
        return envelope

    def record_to_wav(self, filename):
        # Calculate total duration
        max_time = max(note['end'] for note in self.recorded_notes)
        total_samples = int(max_time * self.sample_rate)
        buffer = np.zeros(total_samples)
        
        for note in self.recorded_notes:
            start_sample = int(note['start'] * self.sample_rate)
            end_sample = int(note['end'] * self.sample_rate)
            duration = note['end'] - note['start']
            
            # Generate note
            note_wave = self.generate_note(note['freq'], duration)
            
            # Apply to buffer
            buffer[start_sample:start_sample+len(note_wave)] += note_wave
        
        # Normalize and convert
        buffer /= np.max(np.abs(buffer))
        buffer = np.int16(buffer * 32767)
        
        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.sample_rate)
            f.writeframes(buffer.tobytes())

    def run(self):
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            current_time = pygame.time.get_ticks() / 1000.0 - start_time
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key in self.key_to_note:
                        note = self.key_to_note[event.key]
                        freq = self.note_to_freq(note)
                        self.notes[event.key] = {
                            'start': current_time,
                            'freq': freq,
                            'note': note
                        }
                
                if event.type == KEYUP and event.key in self.notes:
                    note_data = self.notes.pop(event.key)
                    self.recorded_notes.append({
                        **note_data,
                        'end': current_time
                    })
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        if self.recorded_notes:
            self.record_to_wav('keyboard_recording.wav')
            print(f"Saved recording with {len(self.recorded_notes)} notes")

if __name__ == "__main__":
    synth = RealTimeFMSynth()
    synth.run()
