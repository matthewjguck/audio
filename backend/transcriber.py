import openai
import os

class Transcriber:
    """Class responsible for transcribing recorded audio."""

    def __init__(self, openai_key):
        """Initialize the transcriber with the OpenAI API key."""
        openai.api_key = openai_key

    def transcribe_audio(self, audio_file): 
        """Transcribe the given audio file using OpenAI's Whisper API."""
        print(os.path.exists(audio_file))
        try:
            with open(audio_file, "rb") as audio:
                transcript = openai.Audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
                print(transcript)
            return transcript['text'] if 'text' in transcript else ""
        except Exception as e:
            print(f"An error occurred while transcribing: {e}")
            return None