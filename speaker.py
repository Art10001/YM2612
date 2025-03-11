import numpy as np
import pygame
from pygame.locals import *

class RealtimeFMSynth:
    def __init__(self, sample_rate=44100, buffer_size=1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.phase = 0
        self.active_notes = {}
        self.key_to_note = {
            K_a: 'C4', K_w: 'C#4', K_s: 'D4', K_e: 'D#4',
            K_d: 'E4', K_f: 'F4', K_t: 'F#4', K_g: 'G4',
            K_y: 'G#4', K_h: 'A4', K_u: 'A#4', K_j: 'B4',
            K_k: 'C5'
        }
        
        # Pygame setup
        pygame.init()
        pygame.mixer.init(frequency=sample_rate, buffer=buffer_size)
        self.screen = pygame.display.set_mode((300, 100))
        pygame.display.set_caption("FM Synth - Press ESC to quit")

    def note_to_freq(self, note):
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = int(note[-1])
        note_name = note[:-1]
        semitone = notes.index(note_name) + (octave - 4) * 12
        return 440 * (2 ** (semitone / 12))

    def fm_synthesis(self, freq, t, mod_ratio=3.0, mod_index=2.0):
        """Real-time FM synthesis with phase accumulation"""
        modulator = np.sin(2 * np.pi * freq * mod_ratio * t + np.pi/2)
        carrier = np.sin(2 * np.pi * freq * t + mod_index * modulator)
        return carrier

    def adsr_envelope(self, t, duration, attack=0.1, decay=0.1, sustain=0.7, release=0.2):
        """Dynamic envelope generator based on current time and note duration"""
        if t < attack:
            return t / attack
        elif t < attack + decay:
            return 1 - (1 - sustain) * ((t - attack) / decay)
        elif t < duration - release:
            return sustain
        else:
            return sustain * (1 - (t - (duration - release)) / release)

    def generate_chunk(self, freq, duration_held):
        """Generate audio chunk for real-time playback"""
        t = np.linspace(0, self.buffer_size/self.sample_rate, self.buffer_size)
        envelope = np.array([self.adsr_envelope(duration_held + x, 10) for x in t])
        
        # FM synthesis
        mod_ratio = 3.0
        mod_index = 2.0
        carrier = self.fm_synthesis(freq, t + duration_held, mod_ratio, mod_index)
        
        return (carrier * envelope).astype(np.float32)

    def run(self):
        clock = pygame.time.Clock()
        sound_channels = [pygame.mixer.Channel(i) for i in range(8)]
        
        while True:
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    return
                
                if event.type == KEYDOWN and event.key in self.key_to_note:
                    note = self.key_to_note[event.key]
                    freq = self.note_to_freq(note)
                    if event.key not in self.active_notes:
                        self.active_notes[event.key] = {
                            'start_time': current_time,
                            'freq': freq,
                            'last_played': 0
                        }
                
                if event.type == KEYUP and event.key in self.active_notes:
                    del self.active_notes[event.key]

            # Generate audio for active notes
            for key in list(self.active_notes.keys()):
                note_data = self.active_notes[key]
                duration_held = current_time - note_data['start_time']
                
                # Generate audio chunk
                chunk = self.generate_chunk(note_data['freq'], duration_held)
                sound = pygame.mixer.Sound(chunk)
                
                # Find available channel and play
                for channel in sound_channels:
                    if not channel.get_busy():
                        channel.play(sound)
                        break
                
                note_data['start_time'] = current_time  # Reset timing for next chunk

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    synth = RealtimeFMSynth()
    synth.run()
