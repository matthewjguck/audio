import os
import pyaudio
import wave
import gtts

class Playback:
    """Class for handling text-to-speech playback."""

    def __init__(self):
        """Initialize Playback settings."""
        self.audio_file = "transcription_playback.wav"

    def text_to_speech(self, text):
        """Convert text to speech and save it as an audio file."""
        tts = gtts.gTTS(text=text, lang='en')
        tts.save(self.audio_file)

    def play_audio(self):
        """Play the generated audio file using pyaudio."""
        chunk = 1024  # Define chunk size for playback
        wf = wave.open(self.audio_file, 'rb')
        p = pyaudio.PyAudio()

        # Open a stream to play audio
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read audio in chunks and play
        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()

    def playback_transcription(self, text):
        """Convert text to speech and play it back."""
        self.text_to_speech(text)
        self.play_audio()

    def cleanup(self):
        """Remove the audio file after playback."""
        if os.path.exists(self.audio_file):
            os.remove(self.audio_file)
