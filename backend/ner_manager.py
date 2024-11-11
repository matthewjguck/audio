import google.generativeai as genai
import os

class NERManager:
    """Class for managing Named Entity Recognition and memory of proper nouns."""

    def __init__(self):
        
        self.memory = {}

    def extract_proper_nouns(self, transcription):
        prompt = (
            "Extract all proper nouns from the following text and return them in a list:\n"
            f"{transcription}\n"
            "Please return only the proper nouns, with no additional words."
            "For example, if the text is John and Mary are students at Stanford, you would return: ['John', 'Mary', 'Stanford']."
            "If there are no proper nouns, return an empty list."
        )
        response = self.call_gpt_api(prompt)
        if response:
            proper_nouns = response.split(", ")
            proper_nouns = [noun.strip() for noun in proper_nouns if noun]
            self.update_memory(proper_nouns)
            return proper_nouns
        else:
            print("No response received from Gemini API.")
            return []

    def call_gpt_api(self, prompt):
        """Call the Gemini API with the given prompt to extract proper nouns."""
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text if response else ""
        except Exception as e:
            print(f"An error occurred while calling the Gemini API: {e}")
            return ""

    def update_memory(self, proper_nouns):
        for noun in proper_nouns:
            self.memory[noun] = self.memory.get(noun, 0) + 1
    
    def clear_memory(self):
        """Clear the memory of proper nouns."""
        self.memory = {}
