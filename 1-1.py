                          #notes playing thing is fine just detection should be changed

import numpy as np
import sounddevice as sd
from scipy.fft import fft
import tkinter as tk

# Define musical notes and their frequencies for violin and guitar
INSTRUMENT_NOTES = {
    'Violin': {
        'E5': 659.25,
        'A4': 440.00,
        'D4': 293.66,
        'G3': 196.00
    },
    'Guitar': {
        'E4': 329.63,
        'A3': 220.00,
        'D3': 146.83,
        'G2': 98.00,
        'B2': 123.47,
        'E2': 82.41
    }
}


class TuningApp:
    def __init__(self, master):
        self.master = master
        master.title("Musical Instrument Tuner")

        self.instrument_var = tk.StringVar(value="Violin")

        tk.Label(master, text="Select Instrument:").pack(pady=10)
        tk.Radiobutton(master, text="Violin", variable=self.instrument_var, value="Violin",
                       command=self.update_notes).pack()
        tk.Radiobutton(master, text="Guitar", variable=self.instrument_var, value="Guitar",
                       command=self.update_notes).pack()

        self.note_var = tk.StringVar()
        self.note_var.set(next(iter(INSTRUMENT_NOTES[self.instrument_var.get()])))

        tk.Label(master, text="Select Note:").pack(pady=10)
        self.note_menu = tk.OptionMenu(master, self.note_var, *INSTRUMENT_NOTES[self.instrument_var.get()].keys())
        self.note_menu.pack(pady=5)

        self.play_button = tk.Button(master, text="Play Note", command=self.play_note)
        self.play_button.pack(pady=20)

        self.detect_button = tk.Button(master, text="Detect Note", command=self.detect_note)
        self.detect_button.pack(pady=20)

        self.stop_button = tk.Button(master, text="Stop Detection", command=self.stop_detection)
        self.stop_button.pack(pady=20)

        self.exit_button = tk.Button(master, text="Exit", command=master.quit)
        self.exit_button.pack(pady=20)

        self.detected_note_label = tk.Label(master, text="", font=("Arial", 16))
        self.detected_note_label.pack(pady=10)

        self.is_detecting = False

    def update_notes(self):
        """Update the note dropdown based on the selected instrument."""
        notes = INSTRUMENT_NOTES[self.instrument_var.get()].keys()
        self.note_var.set(next(iter(notes)))  # Reset to the first note
        self.note_menu['menu'].delete(0, 'end')
        for note in notes:
            self.note_menu['menu'].add_command(label=note, command=lambda value=note: self.note_var.set(value))

    def play_note(self):
        """Play the selected note."""
        note = self.note_var.get()
        frequency = INSTRUMENT_NOTES[self.instrument_var.get()][note]
        sd.play(np.sin(2 * np.pi * np.arange(44100) * frequency / 44100), samplerate=44100)

    def record_sound(self, duration=3, fs=44100):
        """Record sound for a given duration."""
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
        sd.wait()  # Wait until recording is finished
        return audio.flatten()

    def analyze_sound(self, audio, fs=44100):
        """Analyze the recorded sound and return the dominant frequency."""
        if np.max(np.abs(audio)) < 0.01:  # If the sound is too quiet
            self.detected_note_label.config(text="Not audible, please try again.")
            return None

        freqs = np.fft.rfftfreq(len(audio), 1 / fs)
        spectrum = np.abs(fft(audio))

        peak_freq = freqs[np.argmax(spectrum)]
        return peak_freq

    def detect_note(self):
        """Start note detection."""
        if not self.is_detecting:
            self.is_detecting = True
            audio = self.record_sound()
            dominant_frequency = self.analyze_sound(audio)

            if dominant_frequency is not None:
                closest_note = self.get_closest_note(dominant_frequency)
                self.detected_note_label.config(text=f"Detected note: {closest_note}")

            self.is_detecting = False  # Reset detection after one round

    def get_closest_note(self, frequency):
        """Determine the closest musical note to the given frequency."""
        closest_note = min(INSTRUMENT_NOTES[self.instrument_var.get()].keys(),
                           key=lambda note: abs(INSTRUMENT_NOTES[self.instrument_var.get()][note] - frequency))
        return closest_note

    def stop_detection(self):
        """Stop note detection."""
        self.is_detecting = False
        self.detected_note_label.config(text="Detection stopped.")


def main():
    root = tk.Tk()
    app = TuningApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
