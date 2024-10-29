import os
from dotenv import load_dotenv
import google.generativeai as genai
import openai
import pyaudio
import wave
import threading

google_key = os.getenv('GOOGLE_KEY')

load_dotenv()
openai_key = os.getenv('OPENAI_KEY')


class VoiceDictationTool:
    """Main class for handling the voice dictation tool with NER functionality."""

    def __init__(self):
        """Initialize the VoiceDictationTool with necessary parameters."""

        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber(openai_key)
        self.ner_manager = NERManager(google_key)
        self.transcription = ""
        self.proper_nouns = []

    def start_recording(self):
        """Start recording the user's voice for the dictated text."""

        self.audio_recorder.start_recording()

    def stop_recording(self):
        """Stop recording and process the audio for transcription and NER."""

        print("Recording stopped...")
        self.audio_recorder.stop_recording()
        self.audio_recorder.save_audio()

        self.transcription = self.transcriber.transcribe_audio(self.audio_recorder.audio_file)
        if not self.transcription:
            print("No transcription detected. Using default transcription for testing.")
            self.transcription = "I'm Mark Smith in Stanford in Palo Alto"
        
        if self.transcription:
            print(f"Transcription: {self.transcription}")
            self.proper_nouns = self.ner_manager.extract_proper_nouns(self.transcription)
            print(f"Proper Nouns: {self.proper_nouns}")
        else:
            print("Transcription failed.")
        
        return self.transcription, self.proper_nouns


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


class Transcriber:
    """Class responsible for transcribing recorded audio."""

    def __init__(self, openai_key):
        """Initialize the transcriber with the OpenAI API key."""
        openai.api_key = openai_key  # Set the OpenAI API key

    def transcribe_audio(self, audio_file): 
        """Transcribe the given audio file using OpenAI's Whisper API."""
        try:
            with open(audio_file, "rb") as audio:
                # Correct method to call transcription with the Whisper model
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio,
                    response_format="text"  # Get plain text response
                )
            print("transcription worked")
            return transcript['text'] if 'text' in transcript else ""
        
        except Exception as e:
            print(f"An error occurred while transcribing: {e}")
            return None


class NERManager:
    """Class for managing Named Entity Recognition and memory of proper nouns."""

    def __init__(self, google_key):
        """Initialize the NER manager with the Google API key and an empty memory dictionary."""
        self.google_key = google_key  # Store the Google API key
        self.memory = {}  # Dictionary to store recognized proper nouns

    def extract_proper_nouns(self, transcription):
        """Extract proper nouns from the transcription using the Gemini API.
        
        Args:
            transcription (str): The transcribed text from the user's dictation.

        Returns:
            List[str]: A list of recognized proper nouns.
        """
        # Prepare the prompt for the Gemini API
        prompt = (
            "Extract all proper nouns from the following text and return them in a list:\n"
            f"{transcription}\n"
            "Please return only the proper nouns."
        )
        
        response = self.call_gpt_api(prompt)  # Call the API to get proper nouns
        
        if response:
            # Process the response to extract proper nouns
            proper_nouns = response.split(", ")
            proper_nouns = [noun.strip() for noun in proper_nouns if noun]
            self.update_memory(proper_nouns)
            return proper_nouns
        else:
            print("No response received from Gemini API.")
            return []

    def call_gpt_api(self, prompt):
        """Call the Gemini API with the given prompt to extract proper nouns.
        
        Args:
            prompt (str): The prompt to send to the API.

        Returns:
            str: The response from the Gemini API.
        """
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")  # Instantiate the Gemini model
            response = model.generate_content(prompt)  # Call the model with the prompt
            return response.text if response else ""
        except Exception as e:
            print(f"An error occurred while calling the Gemini API: {e}")
            return ""

    def read_back_proper_nouns(self, proper_nouns):
        """Read back recognized proper nouns to the user, spelling them out.
        
        Args:
            proper_nouns (List[str]): List of recognized proper nouns.
        """
        for noun in proper_nouns:
            print(f"Recognized proper noun: {noun} (spelling: {noun})")  # Placeholder for actual text-to-speech logic

    def update_memory(self, proper_nouns):
        """Update the memory dictionary with new proper nouns.
        
        Args:
            proper_nouns (List[str]): List of proper nouns to add to memory.
        """
        for noun in proper_nouns:
            self.memory[noun] = self.memory.get(noun, 0) + 1  # Use dictionary get() method for conciseness

    def get_memory(self):
        """Retrieve the current memory of proper nouns.

        Returns:
            dict: The memory dictionary containing proper nouns and their counts.
        """
        return self.memory
    
    def clear_memory(self):
        """Clear the memory of proper nouns."""
        self.memory = {}