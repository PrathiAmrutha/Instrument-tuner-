                          #final!!!

import numpy as np
import sounddevice as sd
from scipy.fft import fft
import tkinter as tk
from PIL import Image, ImageTk

# Define musical notes and their frequencies for violin and guitar
INSTRUMENT_NOTES = {
    'Violin': {
        'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G5#': 830.61, 'A5': 880.00, 'A5#': 932.33,
        'A4': 440.00, "A4#": 466.16, "B4": 493.88, "C5": 523.25, 'C#5': 554.37, 'D5': 587.33,
        'D4': 293.66, "D4#": 311.13, "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00, "G4#": 415.30,
        'G3': 196.00, 'G3#': 207.65, 'A3': 220.00, "A3#": 233.08, "B3": 246.94, "C4": 261.63, "C4#": 277.18
    },
    'Guitar': {
        'E4': 329.63, "F#4": 369.99, "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25, 'C#5': 554.37, 'D5': 587.33,
        'B3': 246.94, "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
        'G3': 196.00, 'A3': 220.00, "A#3": 233.08,
        'D3': 146.83,
        'A2': 110.00,
        'E2': 82.41
    }
}

# Define string notes for guitar
GUITAR_STRINGS = {
    '1st String (E4)': ['E4', 'F#4', 'G4', 'A4', 'B4', "C5", 'C#5', 'D5'],
    '2nd String (B3)': ['B3', "C4", 'C#4', 'D4', "D4#"],
    '3rd String (G3)': ['G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F#4'],
    '4th String (D3)': ['D3', 'E3', 'F#3', 'G3', 'A3', 'B3', 'C4'],
    '5th String (A2)': ['A2', 'B2', 'C#3', 'D3', 'E3', 'F#3', 'G#3'],
    '6th String (E2)': ['E2', 'F#2', 'G2', 'A2', 'B2', 'C#3', 'D3'],
}

# Define string notes for violin
VIOLIN_STRINGS = {
    '1st String (E5)': ['E5', "F5", 'F#5', 'G5', "G5#", 'A5', "A5#", 'B5', 'C#6', 'D6'],
    '2nd String (A4)': ['A4', "A4#", 'B4', "C5", 'C#5', 'D5'],
    '3rd String (D4)': ['D4', "D4#", 'E4', "F4", 'F#4', 'G4', "G4#"],
    '4th String (G3)': ['G3', "G3#", 'A3', "A3#", 'B3', 'C4', "C4#"],
}

class TuningApp:
    def __init__(self, master):
        self.master = master
        master.title("Musical Instrument Tuner")

        # Load background image
        self.bg_image = Image.open("image1.jpeg")  # Replace with your image file
        self.bg_image = self.bg_image.resize((1550, 900))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        bg_label = tk.Label(master, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)

        self.instrument_var = tk.StringVar(value="Violin")
        self.string_var = tk.StringVar()
        self.note_var = tk.StringVar()

        tk.Label(master, text="Select Instrument:", font=("Arial", 16), bg='lightblue').pack(pady=10)
        tk.Radiobutton(master, text="Violin", variable=self.instrument_var, value="Violin",
                       command=self.update_notes, font=("Arial", 14)).pack()
        tk.Radiobutton(master, text="Guitar", variable=self.instrument_var, value="Guitar",
                       command=self.update_notes, font=("Arial", 14)).pack()

        tk.Label(master, text="Select String:", font=("Arial", 16), bg='lightblue').pack(pady=10)
        self.string_menu = tk.OptionMenu(master, self.string_var, '')
        self.string_menu.pack(pady=5)

        tk.Label(master, text="Select Note:", font=("Arial", 16), bg='lightblue').pack(pady=10)
        self.note_menu = tk.OptionMenu(master, self.note_var, '')
        self.note_menu.pack(pady=5)

        self.play_button = tk.Button(master, text="Play Note", command=self.play_note, font=("Arial", 14), bg='lightgreen')
        self.play_button.pack(pady=20)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_playing, font=("Arial", 14), bg='lightcoral')
        self.stop_button.pack(pady=20)

        self.detect_button = tk.Button(master, text="Detect Note", command=self.detect_note, font=("Arial", 14), bg='lightyellow')
        self.detect_button.pack(pady=20)

        self.detected_note_label = tk.Label(master, text="Closest Detected Note: ", font=("Arial", 16), bg='lightblue')
        self.detected_note_label.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=self.on_exit, font=("Arial", 14), bg='lightcoral')
        self.exit_button.pack(pady=20)

        self.is_playing = False

        self.update_notes()  # Initial call to set up notes and strings

    def update_notes(self):
        """Update the string dropdown based on the selected instrument."""
        if self.instrument_var.get() == "Guitar":
            self.string_var.set(next(iter(GUITAR_STRINGS.keys())))
            self.string_menu['menu'].delete(0, 'end')
            for string in GUITAR_STRINGS.keys():
                self.string_menu['menu'].add_command(label=string, command=lambda value=string: self.update_string_notes(value))
        else:  # Violin
            self.string_var.set(next(iter(VIOLIN_STRINGS.keys())))
            self.string_menu['menu'].delete(0, 'end')
            for string in VIOLIN_STRINGS.keys():
                self.string_menu['menu'].add_command(label=string, command=lambda value=string: self.update_string_notes(value))

        self.update_string_notes(self.string_var.get())  # Update notes based on selected string

    def update_string_notes(self, selected_string):
        """Update the note dropdown based on the selected string."""
        if self.instrument_var.get() == "Guitar":
            notes = GUITAR_STRINGS[selected_string]
        else:  # Violin
            notes = VIOLIN_STRINGS[selected_string]

        self.note_var.set(notes[0])  # Reset to the first note
        self.note_menu['menu'].delete(0, 'end')
        for note in notes:
            self.note_menu['menu'].add_command(label=note, command=lambda value=note: self.note_var.set(value))

        # Update the displayed selected string
        self.string_var.set(selected_string)  # Ensure the dropdown shows the selected string

    def play_note_continuously(self):
        """Play the selected note continuously."""
        note = self.note_var.get()
        frequency = INSTRUMENT_NOTES[self.instrument_var.get()][note]
        self.is_playing = True
        while self.is_playing:
            sd.play(np.sin(2 * np.pi * np.arange(44100) * frequency / 44100), samplerate=44100)
            sd.wait()  # Wait until the sound is played

    def play_note(self):
        """Play the selected note continuously in a separate thread."""
        if not self.is_playing:
            import threading
            thread = threading.Thread(target=self.play_note_continuously)
            thread.start()

    def stop_playing(self):
        """Stop playing the note."""
        self.is_playing = False

    def record_sound(self, duration=3, fs=44100):
        """Record sound for a given duration."""
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64')
        sd.wait()  # Wait until recording is finished
        return audio.flatten() #rec gives 2D array, flatten to 1D array

    def analyze_sound(self, audio, fs=44100):
        """Analyze the recorded sound and return the dominant frequency."""
        if np.max(np.abs(audio)) < 0.01:  # If the sound is too quiet
            self.detected_note_label.config(text="No sound detected, please try again.")
            return None

        freqs = np.fft.rfftfreq(len(audio), 1 / fs)
        spectrum = np.abs(fft(audio))

        peak_freq = freqs[np.argmax(spectrum)]
        return peak_freq

    def detect_note(self):
        """Start note detection."""
        audio = self.record_sound(duration=3)  # Record for 3 seconds
        dominant_frequency = self.analyze_sound(audio)

        if dominant_frequency is not None:
            closest_note = self.get_closest_note(dominant_frequency)
            self.detected_note_label.config(text=f"Detected note: {closest_note}")
        else:
            self.detected_note_label.config(text="No detection, please try again.")

    def get_closest_note(self, frequency):
        """Determine the closest musical note to the given frequency."""
        closest_note = min(INSTRUMENT_NOTES[self.instrument_var.get()].keys(),
                           key=lambda note: abs(INSTRUMENT_NOTES[self.instrument_var.get()][note] - frequency))
        return closest_note

    def on_exit(self):
        """Handle exit button click."""
        self.stop_playing()  # Ensure sound stops before exiting
        self.master.quit()  # Exit the application

def main():
    root = tk.Tk()
    root.geometry('1000x650')
    app = TuningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()