import os
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv('API_KEY')

class VoiceDictationTool:
    """Main class for handling the voice dictation tool with NER functionality."""

    def __init__(self):
        """Initialize the VoiceDictationTool with necessary parameters."""
        self.audio_recorder = AudioRecorder()  # Class responsible for recording audio
        self.transcriber = Transcriber(api_key)        # Class responsible for transcribing audio
        self.ner_manager = NERManager()        # Class for handling NER and memory management
        self.transcription = ""  # Store the transcribed text

    def start_recording(self):
        """Start recording the user's voice for the dictated text."""
        self.audio_recorder.record_audio()
        print(api_key)
        pass  # Placeholder for logic to start recording

    def stop_recording(self):
        """Stop recording and process the audio for transcription and NER."""
        print("recording done")
        pass  # Placeholder for logic to stop recording and process audio

    def update_transcription(self, transcription):
        """Update the frontend text box with the current transcription."""
        pass  # Placeholder for frontend update logic


class AudioRecorder:
    """Class responsible for recording audio from the user."""

    def __init__(self):
        """Initialize the audio recorder."""
        self.audio_file = "output.wav"  # Placeholder for audio file path

    def record_audio(self):
        """Record the user's audio input."""
        print("recording")
        pass  # Placeholder for recording logic

    def save_audio(self):
        """Save the recorded audio to a file."""
        pass  # Placeholder for saving audio logic

class Transcriber:
    """Class responsible for transcribing recorded audio."""

    def __init__(self, api_key):
        """Initialize the transcriber."""
        #api_key is the OpenAI API key for authentication
        #audio file -- self.audio_file 
        self.api_key = api_key
        #openai.api_key = self.api_key

    def transcribe_audio(self, audio_file): 
        try:
            with open(audio_file, "rb") as audio:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio,
                    response_format="text",
                    language='en' 
                )
            return transcript
        
        except Exception as e:
            print(f"An error occurred while transcribing: {e}")
            return None
            
        #return "Transcribed text goes here."  

class NERManager:
    """Class for managing Named Entity Recognition and memory of proper nouns."""

    def __init__(self):
        """Initialize the NER manager with an empty memory dictionary."""
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
        
        # Process the response to extract proper nouns
        proper_nouns = response.split(", ")  # Split by comma and space
        proper_nouns = [noun.strip() for noun in proper_nouns if noun]
        self.update_memory(proper_nouns)

        return proper_nouns

    def call_gpt_api(self, prompt):
        """Call the Gemini API with the given prompt to extract proper nouns.
        
        Args:
            prompt (str): The prompt to send to the API.

        Returns:
            str: The response from the Gemini API.
        """
        model = genai.GenerativeModel("gemini-1.5-flash")  # Instantiate the Gemini model
        response = model.generate_content(prompt)  # Call the model with the prompt
        
        return response.text  # Return the text content of the response

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
            if noun not in self.memory:
                self.memory[noun] = 1  # Initialize count if noun is new
            else:
                self.memory[noun] += 1  # Increment count if noun is already in memory

    def get_memory(self):
        """Retrieve the current memory of proper nouns.

        Returns:
            dict: The memory dictionary containing proper nouns and their counts.
        """
        return self.memory
    
    def clear_memory(self):
        """Clear the memory of proper nouns."""
        self.memory = {}


def main():
    """Main function to run the voice dictation tool."""
    dictation_tool = VoiceDictationTool()
    
    # Simulated user interface (would be replaced with frontend button interactions)
    while True:
        user_input = input("Type 'start' to begin recording, 'stop' to end recording, or 'exit' to quit: ")

        if user_input.lower() == 'start':
            dictation_tool.start_recording()  # Start recording audio
        elif user_input.lower() == 'stop':
            dictation_tool.stop_recording()    # Stop recording and process audio
        elif user_input.lower() == 'exit':
            print("Exiting the voice dictation tool.")
            break
        else:
            print("Invalid command. Please enter 'start', 'stop', or 'exit'.")

if __name__ == "__main__":
    main()
