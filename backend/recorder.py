import os
import pyaudio
import wave
import threading

class AudioRecorder:
    """Class responsible for recording audio from the user."""

    def __init__(self):
        """Initialize the audio recorder."""
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        self.is_recording = False

        self.audio = pyaudio.PyAudio()
        self.audio_file = self._get_next_audio_file_name()

    def _get_next_audio_file_name(self):
        """Find the next available filename in the current directory."""

        index = 1
        while os.path.exists(f"output{index}.wav"):
            index += 1
        return f"output{index}.wav"

    def start_recording(self):
        """Start recording the user's audio input in a separate thread."""

        if not self.is_recording:
            self.is_recording = True
            self.frames = []  # Clear previous audio frames
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
            print("Recording started...")

    def record_audio(self):
        """Record audio in the background until stopped."""
        
        try:
            stream = self.audio.open(format=self.format,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.chunk)

            while self.is_recording:
                data = stream.read(self.chunk, exception_on_overflow=False)  # Safeguard against overflow
                self.frames.append(data)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            print("Recording finished.")

        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False  # Stop recording in case of an error

    def stop_recording(self):
        """Stop the recording."""
        if self.is_recording:
            self.is_recording = False
            self.recording_thread.join()  # Wait for the recording thread to finish
            print("Recording stopped.")

    def save_audio(self):
        """Save the recorded audio to a file."""
        if not self.frames:
            print("No audio data to save.")
            return

        # Save the recorded frames as a .wav file
        try:
            wf = wave.open(self.audio_file, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print(f"Audio saved to {self.audio_file}")
        except Exception as e:
            print(f"Error saving audio: {e}")