# Install pyaudio speech recognition
# pip install SpeechRecognition pyaudio

import tkinter as tk
from tkinter import ttk
import speech_recognition as sr
import threading
import queue

class VoiceFeedback:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Feedback")
        self.root.geometry("600x400")

        self.recognizer = sr.Recognizer()
        self.selected_mic_index = None
        self.listening = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.transcription_thread = None
        self.audio_capture_thread = None
        self.stop_event = threading.Event()

        # Change this to a Text widget instead of a Label
        self.text_widget = tk.Text(root, wrap=tk.WORD, width=60, height=10)
        self.text_widget.pack(pady=20)

        self.start_button = tk.Button(root, text="Start Listening", command=self.toggle_listening)
        self.start_button.pack(pady=10)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, wraplength=500)
        self.status_label.pack(pady=10)

        self.mic_var = tk.StringVar()
        self.mic_dropdown = ttk.Combobox(root, textvariable=self.mic_var, state='readonly')
        self.mic_dropdown.pack(pady=10)
        self.mic_dropdown.bind('<<ComboboxSelected>>', self.on_mic_selected)

        self.list_microphones()

    def list_microphones(self):
        mic_list = sr.Microphone.list_microphone_names()
        self.mic_dropdown['values'] = mic_list
        self.status_var.set("Please select a microphone from the dropdown.")

    def on_mic_selected(self, event):
        selected_mic = self.mic_var.get()
        self.selected_mic_index = sr.Microphone.list_microphone_names().index(selected_mic)
        self.status_var.set(f"Selected microphone: {selected_mic}")

    def toggle_listening(self):
        if self.listening:
            self.listening = False
            self.start_button.config(text="Start Listening")
            self.status_var.set("Stopping listening...")
            self.stop_event.set()  # Signal threads to stop
            # Wait for threads to finish with a timeout
            if self.audio_capture_thread:
                self.audio_capture_thread.join(timeout=2)
            if self.transcription_thread:
                self.transcription_thread.join(timeout=2)
            self.stop_event.clear()  # Reset the event for next time
            self.status_var.set("Listening stopped.")
        else:
            if self.selected_mic_index is None:
                self.status_var.set("Please select a microphone first.")
                return
            self.listening = True
            self.start_button.config(text="Stop Listening")
            self.status_var.set("Listening started. Speak now.")
            self.audio_capture_thread = threading.Thread(target=self.audio_capture_thread_func, daemon=True)
            self.transcription_thread = threading.Thread(target=self.transcription_thread_func, daemon=True)
            self.audio_capture_thread.start()
            self.transcription_thread.start()
            self.stop_event.clear()  # Ensure the event is cleared before starting

    def audio_capture_thread_func(self):
        with sr.Microphone(device_index=self.selected_mic_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while self.listening and not self.stop_event.is_set():
                try:
                    audio = self.recognizer.listen(source, phrase_time_limit=5, timeout=1)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    pass

    def transcription_thread_func(self):
        while self.listening and not self.stop_event.is_set():
            try:
                audio = self.audio_queue.get(timeout=1)
                try:
                    transcription = self.recognizer.recognize_google(audio)
                    self.text_queue.put(transcription + "\n")
                except queue.Empty:
                    pass
                except sr.UnknownValueError:
                    # self.text_queue.put("[Could not understand audio]\n")
                    pass
                except sr.RequestError:
                    self.text_queue.put("[Could not request results; check your network connection]\n")
            except queue.Empty:
                pass
            if not self.stop_event.is_set():
                self.root.after(10, self.update_text)

    def update_text(self):
        try:
            while True:
                text = self.text_queue.get_nowait()
                self.text_widget.insert(tk.END, text)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceFeedback(root)
    root.mainloop()
