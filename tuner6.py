import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import messagebox
import threading

# Define musical notes and their corresponding frequencies
NOTE_FREQUENCIES = {
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,  # standard tuning pitch
    "A#4": 466.16,
    "B4": 493.88,
    "C5": 523.25,
}

# Global variables to control playback and detection
is_playing = False
current_thread = None

def generate_sine_wave(freq, duration, sample_rate=44100):
    """Generate a sine wave at a given frequency and duration."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

def play_sound_continuous(frequency):
    """Play a sound of a specific frequency continuously."""
    global is_playing
    is_playing = True
    while is_playing:
        wave = generate_sine_wave(frequency, 1)  # Play in 1 second chunks
        sd.play(wave, samplerate=44100)
        sd.wait()  # Wait until sound is finished playing

def play_note():
    """Play the selected musical note."""
    global current_thread, is_playing

    note = note_var.get()
    if note in NOTE_FREQUENCIES:
        frequency = NOTE_FREQUENCIES[note]

        # Stop any currently playing thread
        stop_playing()

        # Start a new thread to play the note continuously
        current_thread = threading.Thread(target=play_sound_continuous, args=(frequency,))
        current_thread.start()
    else:
        messagebox.showerror("Error", "Please select a valid note.")

def stop_playing():
    """Stop any currently playing sound or detection."""
    global is_playing
    is_playing = False
    if current_thread is not None:
        current_thread.join()  # Wait for the thread to finish

def detect_frequency(data, sample_rate):
    """Detect the frequency of the audio input."""
    freqs = np.fft.fftfreq(len(data), 1 / sample_rate)
    fft_result = np.fft.fft(data)
    index = np.argmax(np.abs(fft_result[:len(fft_result) // 2]))  # Only look at positive frequencies
    return abs(freqs[index])

def detect_note():
    """Listen to the microphone input and detect the played note."""
    global current_thread, is_playing

    # Stop any currently playing thread
    stop_playing()

    sample_rate = 44100
    duration = 1  # Duration to listen for (in seconds)
    is_playing = True

    def listen():
        while is_playing:
            data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='float64')
            sd.wait()  # Wait until recording is finished
            frequency = detect_frequency(data.flatten(), sample_rate)

            # Find the closest note
            closest_note = min(NOTE_FREQUENCIES.keys(), key=lambda note: abs(NOTE_FREQUENCIES[note] - frequency))
            frequency_label.config(text=f"Detected Frequency: {frequency:.2f} Hz")
            note_label.config(text=f"Closest Note: {closest_note}")

            # Tuning feedback
            tuning_difference = frequency - NOTE_FREQUENCIES[closest_note]
            if abs(tuning_difference) < 5:
                feedback_label.config(text="In Tune", fg="green")
            elif tuning_difference > 0:
                feedback_label.config(text="Sharp", fg="red")
            else:
                feedback_label.config(text="Flat", fg="blue")

    current_thread = threading.Thread(target=listen)
    current_thread.start()

def create_tuner_gui():
    """Create the main GUI for the instrument tuner."""
    global note_var, frequency_label, note_label, feedback_label
    root = tk.Tk()
    root.title("Instrument Tuner")

    tk.Label(root, text="Select a Note:").pack(pady=10)

    note_var = tk.StringVar(value=list(NOTE_FREQUENCIES.keys())[0])
    note_menu = tk.OptionMenu(root, note_var, *NOTE_FREQUENCIES.keys())
    note_menu.pack(pady=10)

    play_button = tk.Button(root, text="Play Note", command=play_note)
    play_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop", command=stop_playing)
    stop_button.pack(pady=10)

    detect_button = tk.Button(root, text="Detect Note", command=detect_note)
    detect_button.pack(pady=10)

    frequency_label = tk.Label(root, text="Detected Frequency: ")
    frequency_label.pack(pady=10)

    note_label = tk.Label(root, text="Closest Note: ")
    note_label.pack(pady=10)

    feedback_label = tk.Label(root, text="Tuning Feedback: ")
    feedback_label.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_tuner_gui()
