import numpy as np
import wave
import pyaudio
import keyboard

class YM2612Simulator:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.duration = 1.0  # default duration in seconds
        self.frequency = 440.0  # default frequency in Hz (A4)
        self.audio_data = []

    def generate_tone(self, frequency, duration):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = 0.5 * np.sin(2 * np.pi * frequency * t)
        return tone

    def play_tone(self, frequency, duration):
        tone = self.generate_tone(frequency, duration)
        self.audio_data.extend(tone)

    def save_to_wav(self, filename):
        audio_data = np.array(self.audio_data, dtype=np.float32)
        audio_data = (audio_data * 32767).astype(np.int16)
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())

def main():
    simulator = YM2612Simulator()

    print("Press 'q' to quit.")
    print("Press 'a' to 'g' to play notes.")
    print("Press '1' to '5' to change duration.")

    while True:
        if keyboard.is_pressed('q'):
            break
        for key in 'abcdefg':
            if keyboard.is_pressed(key):
                frequency = 440.0 * (2 ** ((ord(key) - ord('a')) / 12.0))
                simulator.play_tone(frequency, simulator.duration)
        for key, duration in zip('12345', [0.1, 0.2, 0.5, 1.0, 2.0]):
            if keyboard.is_pressed(key):
                simulator.duration = duration

    simulator.save_to_wav('output.wav')
    print("Audio saved to output.wav")

if __name__ == "__main__":
    main()
