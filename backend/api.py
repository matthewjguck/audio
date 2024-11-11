import os
from dotenv import load_dotenv
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .ner_manager import NERManager
from .playback import Playback
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_KEY'))

class VoiceDictationTool:
    """Main class for handling the voice dictation tool with NER functionality."""

    def __init__(self, proper_nouns=False):
        """Initialize the VoiceDictationTool with necessary parameters."""
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.ner_manager = NERManager()
        self.playback = Playback()
        self.transcription = ""
        self.proper_nouns = []
        self.proper_nouns_enabled = proper_nouns

    def start_recording(self):
        """Start recording the user's voice for the dictated text."""
        self.audio_recorder.start_recording()

    def stop_recording(self):
        """Stop recording and process the audio for transcription and NER."""

        print("Recording stopped...")
        self.audio_recorder.stop_recording()
        self.audio_recorder.save_audio()

        self.transcription = self.transcriber.transcribe_audio(self.audio_recorder.audio_file)
        if self.transcription:
            print(f"Transcription: {self.transcription}")
            self.proper_nouns = self.ner_manager.extract_proper_nouns(self.transcription)
            print(f"Proper Nouns: {self.proper_nouns}")
            self.playback.playback_transcription(self.transcription)

            if self.proper_nouns_enabled:
                print("Proper nouns enabled.")
                self.playback.playback_transcription('The Proper nouns are: ' + ', '.join(self.proper_nouns))
                
            self.playback.cleanup()
        else:
            print("Transcription failed.")
        return self.transcription, self.proper_nouns
